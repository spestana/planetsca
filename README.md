# PyPlanetSCA Python Library

This is a python library for mapping snow covered areas (SCA) from high-resolution PlanetScope images using a Random Forest model. 

Originally modeled from Kehan Yang: https://github.com/KehanGit/High_resolution_snow_cover_mapping/blob/main/01_download_planetscope_images.ipynb

TestPyPi Link: https://test.pypi.org/project/PyPlanetSCA/#description

## Installation

1. To install the python package, use: 

```bash
pip install -i https://test.pypi.org/simple/ PyPlanetSCA
```

2. Install additional packages:
```bash
pip install numpy
pip install pandas
pip install scikit-learn
pip install geopandas
pip install rasterio
pip install matplotlib
pip install joblib
```
## Running the code

1. Import modules
```
from planetsca.data_gathering import data_gathering as dg
from planetsca.data_preparation import data_preparation as dp
from planetsca.model_training import model_training as mt
from planetsca.prediction_evaluation import prediction_evaluation as pe
import numpy as np
```

2. Set Variables and folder locations
```
domainID = '551'
# enter the Planet user API key
apiKey = '_________'
item_type = "PSScene"
asset_type = "ortho_analytic_4b_sr"
bundle_type = "analytic_sr_udm2"
```

3. Data Gathering
```

# data download location
out_direc = '/Users/ianch/PyPlanetSCAPythonLibrary/Test_Files/'
domain_geometry = dg.domain_shape()
print(domain_geometry)
result = dg.api_search(item_type, apiKey)
geojson_data, gdf = dg.downloadable_PlanetIDs(result, domain_geometry)
id_list = dg.id_gemoetry_lists(geojson_data, gdf)
order_urls = dg.submit_orders(id_list, item_type, bundle_type, apiKey)
dg.save_data_to_csv(order_urls)
dg.download_orders(order_urls, out_direc, apiKey)
#dg.display_image(fp)
```

4. Data Preparation
```
df_train = dp.data_labeling("","","", "", 'sample_174k.csv')
dir_model = 'random_forest_20240116_binary_174K.joblib'
dir_score = 'random_forest_20240116_binary_174K_scores.csv'
```

5. Model Training
``` 
mt.train_model(dir_model, dir_score, 10, 10, 4, 1, df_train)
```


7. Prediction Evaluation
```
dir_raster = '20180528_181110_1025_3B_AnalyticMS_SR_clip.tiff'
dir_out = 'SCA'
pe.single_image_evaluation(dir_raster, dir_model, dir_out)
```

## Functions

### data_gathering module

1. build_payload(item_ids, item_type, bundle_type, aoi_coordinates): Builds Payload to send to Planet
   - item_ids: Item ID from Planet
   - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
   - bundle_type: Product Bundle from Planet
   - aoi_coordinates: Area of Interest Coordinates
2. order_now(payload,apiKey): Order using Payload from Planet
   - payload: Payload to send to Planet
   - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
3. download_results(order_url, folder, apiKey, overwrite=False): Download results from Planet using an order_url
   - order_url: order_Urls from Function submit_orders
   - folder: Output folder
   - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
7. domain_shape(): Returns the shape of the domain array
8. api_search(item_type, apiKey): Searches for API Key
   - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
   - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
10. downloadable_PlanetIDs(result, domain_geometry)
    - result: Result Output from api_search Function
    - domain_geometry: Domain_geometry Output from domain_shape Function
12. id_gemoetry_lists(geojson_data, gdf)
    - geojson_data: geojson_data Output from downloadble_PlanetIDs
    - gdf: Array Output from downloadable_PlanetIDs
14. order_status(apiKey, item_type, asset_type, id_list)
    - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
    - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
    - asset_type: Product derived from item's source data
    - id_list: Id List created from id_gemoetry_lists Function
16. submit_orders(id_list, item_type, bundle_type, apiKey)
    - id_list: Id List created from id_gemoetry_lists Function
    - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
    -  bundle_type: Product Bundle from Planet
    - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
18. save_data_to_csv(order_urls)
    - order_url: order_Urls from Function submit_orders
20. download_orders(order_urls, out_direc, apiKey): Downloads the orders once ready, if data is not ready yet, it will display "data not ready yet"
    - order_url: order_Urls from Function submit_orders
    - out_direc: Folder location to download data
    - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
22. display_image(fp): Uses Rasterio to Display Tif Image
    - fp: Tif Image to be displayed
