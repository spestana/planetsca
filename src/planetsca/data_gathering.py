# Imports
import importlib
import json
import os
import pathlib
import time

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import requests
from huggingface_hub import hf_hub_download
from requests.auth import HTTPBasicAuth
from shapely.geometry import shape

headers = {"Content-Type": "application/json"}


def extract_domain(file_name):
    """
    Helper function for extracting domain from a geojson file

    Parameters
    ----------
        file_name: str
            file path to geojson file

    Returns
    -------
        file.domain: dict
            Dictionary containing data filter information
    """

    file = importlib.import_module(file_name)
    return file.domain


def build_payload(item_ids, item_type, bundle_type, aoi_coordinates):
    """
    Helper function building payload for the Planet API

    Parameters
    ----------
        item_ids: str
            Item id that contains date and location information
        item_type: str
            Class of spacecraft and/or processing level of an item https://developers.planet.com/docs/apis/data/items-assets/
        bundle_type: str
            Groups of assets for an item and contain metadata https://developers.planet.com/apis/orders/product-bundles-reference/
        aoi_coordinates: list[float]
            Area of interest coordinates

    Returns
    -------
        payload: dict
            Dictionary containing all necessary information for the Planet API
    """

    payload = {
        "name": item_ids[0],
        "source_type": "scenes",
        "products": [
            {
                "item_ids": item_ids,
                "item_type": item_type,
                "product_bundle": bundle_type,
            }
        ],
        "tools": [
            {"clip": {"aoi": {"type": "Polygon", "coordinates": aoi_coordinates}}}
        ],
    }
    return payload


def order_now(payload, apiKey):
    """
    Helper function for ordering data from Planet

    Parameters
    ----------
        payload: dict
            Dictionary containing all necessary information for the Planet API
        apiKey: str
            Planet API key
    """

    orders_url = "https://api.planet.com/compute/ops/orders/v2"
    response = requests.post(
        orders_url,
        data=json.dumps(payload),
        auth=HTTPBasicAuth(apiKey, ""),
        headers=headers,
    )
    print(response)

    if response.status_code == 202:
        order_id = response.json()["id"]
        url = f"https://api.planet.com/compute/ops/orders/v2/{order_id}"
        # feature_check = requests.get(url, auth=(PLANET_API_KEY, ""))
        feature_check = requests.get(url, auth=HTTPBasicAuth(apiKey, ""))
        if feature_check.status_code == 200:
            print(
                f"Submitted a total of {len(feature_check.json()['products'][0]['item_ids'])} image ids: accepted a total of {len(feature_check.json()['products'][0]['item_ids'])} ids"
            )
            print(f"Order URL: https://api.planet.com/compute/ops/orders/v2/{order_id}")
            return f"https://api.planet.com/compute/ops/orders/v2/{order_id}"
    else:
        print(f"Failed with Exception code : {response.status_code}")


def download_results(order_url, apiKey, folder, overwrite=False):
    """
    Helper function for downloading the ordered data from Planet, makes a download request every 60 seconds until data is ready to download

    Parameters
    ----------
        order_url: str
            Order urls created from prepare_submit_orders()
        apiKey: str
            Planet API key
        folder: str
            folder path for output
    """

    print("Attempting to download")  # Tell user what to do
    request_fufilled = True
    counter = 1
    while request_fufilled:
        r = requests.get(order_url, auth=HTTPBasicAuth(apiKey, ""))
        try:
            if r.status_code == 200:
                response = r.json()
                results = response["_links"]["results"]
                results_urls = [r["location"] for r in results]
                results_names = [r["name"] for r in results]
                print("{} items to download".format(len(results_urls)))

                for url, name in zip(results_urls, results_names):
                    path = pathlib.Path(os.path.join(folder, name))

                    if overwrite or not path.exists():
                        print("downloading {} to {}".format(name, path))
                        r = requests.get(url, allow_redirects=True)
                        path.parent.mkdir(parents=True, exist_ok=True)
                        open(path, "wb").write(r.content)
                    else:
                        print("{} already exists, skipping {}".format(path, name))
            else:
                print(f"Failed with response {r.status_code}")
            request_fufilled = False
        # Data isn't ready yet, need to code in functionality to rerun the download when data is ready
        except Exception:
            print("data not ready yet, this was attempt number {}".format(counter))
            print("will automatically try again in 60 seconds")
            counter += 1
        r.close()
        time.sleep(60)
    print("Completed downloads")
    # except Exception as e:
    #     print(e)
    #     print(order_url)
    #     raise Exception
    # r.close()


def search_API_request_object(item_type, apiKey, domain):
    """
    Sends a request to find if data is available in the Planet API

    Parameters
    ----------
        item_type: str
            Class of spacecraft and/or processing level of an item https://developers.planet.com/docs/apis/data/items-assets/
        apiKey: str
            Planet API key
        domain: dict
            Dictionary containing data filter information

    Returns
    -------
        result: Response
            Response object containing json file
    """

    # Search API request object
    search_endpoint_request = {"item_types": [item_type], "filter": domain}
    result = requests.post(
        "https://api.planet.com/data/v1/quick-search",
        auth=HTTPBasicAuth(apiKey, ""),
        json=search_endpoint_request,
    )
    return result


def prep_ID_geometry_lists(result, domain):
    """
    Creates list of IDs of requested data from Planet

    Parameters
    ----------
        result: Response
            Response object containing json file
        domain: dict
            Dictionary containing information as read from a geojson file

    Returns
    -------
        id_list, geom_list: list[str], list[float]
            List of IDs and geometries of requested data from Planet
    """

    domain_geometry = shape(domain["config"][0]["config"])

    # view available data and prepare the list of planet IDs to download
    geojson_data = result.json()
    gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])

    # Add a new column to 'gdf' with the intersection area
    gdf["intersection_area"] = gdf["geometry"].intersection(domain_geometry).area

    # Calculate the percentage overlap
    gdf["overlap_percentage"] = (gdf["intersection_area"] / domain_geometry.area) * 100

    # prep the ID and geometry lists
    id_list = [
        feature["id"]
        for idx, feature in enumerate(geojson_data["features"])
        if gdf["overlap_percentage"].iloc[idx] >= 99
    ]
    geom_list = [
        feature["geometry"]
        for idx, feature in enumerate(geojson_data["features"])
        if gdf["overlap_percentage"].iloc[idx] >= 99
    ]
    print(len(id_list))
    print(sorted(id_list))

    return id_list, geom_list


def prepare_submit_orders(id_list, item_type, bundle_type, apiKey, domain):
    """
    Submits order payloads to the Planet API by iterating through each id

    Parameters
    ----------
        id_list: list[str]
            List of IDs of data to be requested from Planet
        item_type: str
            Class of spacecraft and/or processing level of an item https://developers.planet.com/docs/apis/data/items-assets/
        bundle_type: str
            Groups of assets for an item and contain metadata https://developers.planet.com/apis/orders/product-bundles-reference/
        apiKey: str
            Planet API key
        domain: dict
            Dictionary containing data filter information

    Returns
    -------
        order_urls: DataFrame
            Order urls with geometry IDs and indices
    """

    # prepare and submit the orders
    order_urls = pd.DataFrame(columns=["index", "ID_geom", "order_url"])

    # loop through each order payload, and submit
    for idx, IDD in enumerate(id_list):
        print(idx, IDD)

        payload = build_payload(
            [IDD], item_type, bundle_type, domain["config"][0]["config"]["coordinates"]
        )
        order_url = order_now(payload, apiKey)

        order_urls.loc[idx, "index"] = idx
        order_urls.loc[idx, "ID_geom"] = IDD
        order_urls.loc[idx, "order_url"] = order_url

    return order_urls


def save_to_csv(order_urls):
    """
    For checking out data and saving to a csv for later use

    Parameters
    ----------
        order_urls: DataFrame
            Order urls with geometry IDs and indices
    """

    print(order_urls)
    order_urls.to_csv("urlSaver.csv", index=None)  # save all URLs


def download_ready_orders(order_urls, apiKey, out_direc):
    """
    Downloads ready orders from the Planet API, if "data not ready yet" waits 60 seconds before making another request

    Parameters
    ----------
        order_urls: DataFrame
            Order urls with geometry IDs and indices
        apiKey: str
            Planet API key
        out_direc: str
            File path to output directory
    """

    for url in order_urls.itertuples():
        print(url.index, url.order_url)
        print("start downloading data to", out_direc + url.ID_geom)
        if url.order_url is not None:
            try:
                ~np.isnan(url.order_url)
            except Exception:
                download_results(url.order_url, apiKey, folder=out_direc + url.ID_geom)
        # break


def show_img(image_path):
    """
    Displays rasterio image

    Parameters
    ----------
        image_path: str
            File path to tif image

    Returns
    -------
        img: DataSetReader
            Contains Raster data and ways to interact with the image
    """

    fp = image_path
    img = rasterio.open(fp)
    return img


def retrieve_dataset(out_direc, file):
    """
    Downloads datasets from hugging faces

    Parameters
    ----------
        out_direc: str
            File path to output directory
        file: str
            File name to download
    """

    hf_hub_download(
        repo_id="geo-smart/planetsca_datasets",
        filename=file,
        local_dir=out_direc,
    )
