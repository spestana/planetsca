import os
import requests
import geopandas as gpd
from requests.auth import HTTPBasicAuth
from shapely.geometry import shape
import numpy as np
import subprocess
import json
import pathlib
import pandas as pd
import rasterio
import time
from rasterio.plot import show

headers = {'Content-Type': 'application/json'}

#---------------------------- geojson_551.py
geo_json_geometry = {
  "type": "Polygon",
  "coordinates": [
    [
      [
        -105.88556387570844,
        40.51902315502832
      ],
      [
        -105.87210147791147,
        40.51902315502832
      ],
      [
        -105.87210147791147,
        40.52888545899697
      ],
      [
        -105.88556387570844,
        40.52888545899697
      ],
      [
        -105.88556387570844,
        40.51902315502832
      ]
    ]
  ]
}

# filter for items the overlap with our chosen geometry
geometry_filter = {
  "type": "GeometryFilter",
  "field_name": "geometry",
  "config": geo_json_geometry
}

# filter images acquired in a certain date range
date_range_filter = {
  "type": "DateRangeFilter",
  "field_name": "acquired",
  "config": {
    "gte": "2023-07-25T00:00:00.000Z",
    "lte": "2023-09-01T00:00:00.000Z"
  }
}

# filter any images which are more than 50% clouds
cloud_cover_filter = {
  "type": "RangeFilter",
  "field_name": "cloud_cover",
  "config": {
    "lte": 0.05
  }
}

# create a filter that combines our geo and date filters
# could also use an "OrFilter"
#domain = {
#  "type": "AndFilter",
#  "config": [geometry_filter, date_range_filter]
#}

# create a filter that combines our geo and date filters
# could also use an "OrFilter"
domain = {
  "type": "AndFilter",
  "config": [geometry_filter, date_range_filter, cloud_cover_filter]
}

#----------------------------


#---------------------------- Pre-built functions

def build_payload(item_ids, item_type, bundle_type, aoi_coordinates):
    payload = {
        "name": item_ids[0],
        "source_type": "scenes",
        "products": [
            {
                "item_ids": item_ids,
                "item_type": item_type,
                "product_bundle": bundle_type
            }
        ],
        "tools": [
            {
                "clip": {
                    "aoi": {
                        "type": "Polygon",
                        "coordinates": aoi_coordinates
                    }
                }
            }
        ]
    }
    return payload

def order_now(payload,apiKey):
    orders_url = 'https://api.planet.com/compute/ops/orders/v2'
    response = requests.post(orders_url, data=json.dumps(payload), auth=HTTPBasicAuth(apiKey, ''), headers=headers)
    print(response)

    if response.status_code==202:
        order_id =response.json()['id']
        url = f"https://api.planet.com/compute/ops/orders/v2/{order_id}"
        # feature_check = requests.get(url, auth=(PLANET_API_KEY, ""))
        feature_check = requests.get(url, auth=HTTPBasicAuth(apiKey, ''))
        if feature_check.status_code==200:
            print(f"Submitted a total of {len(feature_check.json()['products'][0]['item_ids'])} image ids: accepted a total of {len(feature_check.json()['products'][0]['item_ids'])} ids")
            print(f"Order URL: https://api.planet.com/compute/ops/orders/v2/{order_id}")
            return f"https://api.planet.com/compute/ops/orders/v2/{order_id}"
    else:
        print(f'Failed with Exception code : {response.status_code}')
        
def download_results(order_url,folder, apiKey, overwrite=False):
    print("Attempting to download") #Tell user what to do
    request_fufilled = True
    while request_fufilled:
      r = requests.get(order_url, auth=HTTPBasicAuth(apiKey, ''))
      try:
          if r.status_code ==200:
              response = r.json()
              results = response['_links']['results']
              results_urls = [r['location'] for r in results]
              results_names = [r['name'] for r in results]
              print('{} items to download'.format(len(results_urls)))

              for url, name in zip(results_urls, results_names):
                  path = pathlib.Path(os.path.join(folder,name))

                  if overwrite or not path.exists():
                      print('downloading {} to {}'.format(name, path))
                      r = requests.get(url, allow_redirects=True)
                      path.parent.mkdir(parents=True, exist_ok=True)
                      open(path, 'wb').write(r.content)
                  else:
                      print('{} already exists, skipping {}'.format(path, name))
          else:
              print(f'Failed with response {r.status_code}')
          request_fufilled = False
      #Data isn't ready yet, need to code in functionality to rerun the download when data is ready
      except:
          print('data not ready yet')
      r.close()
      time.sleep(60)
    # except Exception as e:
    #     print(e)
    #     print(order_url)
    #     raise Exception
    # r.close()

#-----------------------------------

def domain_shape():
    domain_geometry = shape(domain['config'][0]['config'])
    return domain_geometry

def api_search(item_type, apiKey):
    search_endpoint_request = {
    "item_types": [item_type],
    "filter": domain
    }
    result = \
    requests.post(
        'https://api.planet.com/data/v1/quick-search',
        auth=HTTPBasicAuth(apiKey, ''),
        json=search_endpoint_request)
    return result
    
def downloadable_PlanetIDs(result, domain_geometry):
    geojson_data = result.json()
    gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])

    # Add a new column to 'gdf' with the intersection area
    gdf['intersection_area'] = gdf['geometry'].intersection(domain_geometry).area

    # Calculate the percentage overlap
    gdf['overlap_percentage'] = (gdf['intersection_area'] / domain_geometry.area) * 100
    return geojson_data, gdf

def id_gemoetry_lists(geojson_data, gdf):
    id_list = [feature['id'] for idx, feature in enumerate(geojson_data['features']) if gdf['overlap_percentage'].iloc[idx] >= 99]
    geom_list = [feature['geometry'] for idx, feature in enumerate(geojson_data['features']) if gdf['overlap_percentage'].iloc[idx] >= 99]
    print(len(id_list))
    print(sorted(id_list))
    return (id_list)

#Not sure if this one will work, its commented out in the reference
def order_status(apiKey, item_type, asset_type, id_list):
    for IDD in id_list:
        print(IDD)
        command = 'curl -L -H "Authorization: api-key '+apiKey+'"'
        sublink = " 'https://api.planet.com/data/v1/item-types/"+item_type+"/items/"+IDD+"/assets/' "
        # sublink = " 'https://api.planet.com/data/v2/item-types/"+item_type+"/items/"+IDD+"/assets/' "
        command = command+sublink+'| jq .'+asset_type+'.status'
        status = subprocess.run(command, shell=True)
        print(command)
        # break

def submit_orders(id_list, item_type, bundle_type, apiKey):
    order_urls = pd.DataFrame(columns = ["index","ID_geom", "order_url"])

    # loop through each order payload, and submit
    for idx,IDD in enumerate(id_list):
        print(idx,IDD)
        
        payload = build_payload([IDD],item_type,bundle_type,domain['config'][0]['config']['coordinates'])
        order_url = order_now(payload,apiKey)
        
        order_urls.loc[idx, "index"] = idx        
        order_urls.loc[idx, "ID_geom"] = IDD
        order_urls.loc[idx, "order_url"] = order_url

    return order_urls

def save_data_to_csv(order_urls):
    print(order_urls)
    order_urls.to_csv('urlSaver.csv', index = None)

def download_orders(order_urls, out_direc, apiKey):
    # download the orders once ready
    # outputs of "data not ready yet" mean that the orders need more time to process before downloading
    for url in order_urls.itertuples():
        print(url.index,url.order_url)
        print("start downloading data to".format(), out_direc + url.ID_geom)
        if url.order_url != None:
          try:
            nantest = ~np.isnan(url.order_url)
          except:
            download_results(url.order_url,folder = out_direc + url.ID_geom, apiKey = apiKey)
        # break

def display_image(fp):
    img = rasterio.open(fp)
    show(img)