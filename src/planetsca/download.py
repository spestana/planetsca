import json
import os
import pathlib
import time
from typing import List

import requests
from huggingface_hub import hf_hub_download
from requests.auth import HTTPBasicAuth

from planetsca import search


def order(
    id_list: List[str], item_type: str, bundle_type: str, filter: dict, api_key: str
) -> str:
    """
    Builds payload for Planet API and submits an order.

    Parameters
    ----------
        id_list: List[str]
            Item id that contains date and location information
        item_type: str
            Class of spacecraft and/or processing level of an item https://developers.planet.com/docs/apis/data/items-assets/
        bundle_type: str
            Groups of assets for an item and contain metadata https://developers.planet.com/apis/orders/product-bundles-reference/
        filter: dict
            Dictionary containing data filter information
        api_key: str
            Planet API key

    Returns
    -------
        order_url: str
            URL from which to download image from Planet API
    """

    # build payload
    payload = build_payload(
        id_list,
        item_type,
        bundle_type,
        search.get_filter(filter, "GeometryFilter")["config"]["coordinates"],
    )

    # submit payload and get order url
    order_url = order_now(payload, api_key)

    return order_url


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


def order_now(payload, api_key):
    """
    Helper function for ordering data from Planet

    Parameters
    ----------
        payload: dict
            Dictionary containing all necessary information for the Planet API
        api_key: str
            Planet API key

    Returns
    ----------
        order_url: str
            URL from which to download image from Planet API
    """

    orders_url = "https://api.planet.com/compute/ops/orders/v2"
    response = requests.post(
        orders_url,
        data=json.dumps(payload),
        auth=HTTPBasicAuth(api_key, ""),
        headers={"Content-Type": "application/json"},
    )
    # print(response)

    if response.status_code == 202:
        order_id = response.json()["id"]
        url = f"https://api.planet.com/compute/ops/orders/v2/{order_id}"
        # feature_check = requests.get(url, auth=(PLANET_API_KEY, ""))
        feature_check = requests.get(url, auth=HTTPBasicAuth(api_key, ""))
        if feature_check.status_code == 200:
            print(
                f"Submitted a total of {len(feature_check.json()['products'][0]['item_ids'])} image ids: accepted a total of {len(feature_check.json()['products'][0]['item_ids'])} ids"
            )
            order_url = f"https://api.planet.com/compute/ops/orders/v2/{order_id}"
            print(f"Order URL: {order_url}")
            return order_url
    else:
        print(f"Failed with Exception code : {response.status_code}")
        return response


def download(order_url, api_key, out_dirpath, overwrite=False):
    """
    Helper function for downloading the ordered data from Planet, makes a download request every 60 seconds until data is ready to download

    Parameters
    ----------
        order_url: str
            Order urls created from prepare_submit_orders()
        api_key: str
            Planet API key
        out_dirpath: str
            Path to output directory

    Returns
    ----------
        None
    """

    print("Attempting to download")
    request_fufilled = True
    counter = 1
    while request_fufilled:
        r = requests.get(order_url, auth=HTTPBasicAuth(api_key, ""))
        try:
            if r.status_code == 200:
                response = r.json()
                results = response["_links"]["results"]
                results_urls = [r["location"] for r in results]
                results_names = [r["name"] for r in results]
                print("{} items to download".format(len(results_urls)))

                for url, name in zip(results_urls, results_names):
                    path = pathlib.Path(os.path.join(out_dirpath, name))

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
        # Data isn't ready yet
        except Exception:
            print("data not ready yet, this was attempt number {}".format(counter))
            print("will automatically try again in 60 seconds")
            # TODO: use warning or logging to handle these cases
            counter += 1
        r.close()
        time.sleep(60)
    print("Completed downloads")
    return None


def retrieve_dataset(out_direc, file):
    """
    Downloads datasets from Hugging Face

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
