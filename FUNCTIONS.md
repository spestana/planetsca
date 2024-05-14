## Functions

### Table of Contents <a name="table_of_contents"></a>
1. [Data Gathering Module](#data_gathering)
2. [Data_Preparation Module](#data_preparation)
3. [Model Training Module](#model_training)
4. [Prediction Evaluation Module](#prediction_evaluation)



### data_gathering module <a name="data_gathering"></a> 
##### [Table of Contents](#table_of_contents)

**1. build_payload(item_ids, item_type, bundle_type, aoi_coordinates)** 
>*Description:* Builds Payload to send to Planet
>
>*Parameters:*
>   - item_ids: Item ID from Planet
>   - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
>   - bundle_type: Product Bundle from Planet
>   - aoi_coordinates: Area of Interest Coordinates
>
>*Outputs:* payload

**2. order_now(payload,apiKey)**
>*Description:* Order using Payload from Planet
>
>*Parameters:*
>  - payload: Payload to send to Planet
>  - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
>
>*Outputs:* Returns Planet Order Link

**3. download_results(order_url, folder, apiKey, overwrite=False)**
>*Description:* Download results from Planet using an order_url
>
>*Parameters:*
>  - order_url: order_Urls from Function submit_orders
>  - folder: Output folder
>  - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
>
>*Outputs:* N/A

**4. domain_shape()** 
>*Description:* Returns the shape of the domain array
>
>*Parameters:* N/A
>
>*Outputs:* Shape of domain array

**5. api_search(item_type, apiKey)** 
>*Description:* Searches for API Key
>
>*Parameters:*
>  - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
>  - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
>
>*Outputs:* Result

**6. downloadable_PlanetIDs(result, domain_geometry)** 
>*Description:* Creates geojson_data and gdf which is the overlap from the domain_geometry
>
>*Parameters:*
>  - result: Result Output from api_search Function
>  - domain_geometry: Domain_geometry Output from domain_shape Function
>
>*Outputs:* geojson_data, gdf

**8. id_gemoetry_lists(geojson_data, gdf)** 
>*Description:* Prints the length and sorted versions of id_list from geojson_data and gdf
>
>*Parameters:*
>  - geojson_data: geojson_data Output from downloadble_PlanetIDs
>  - gdf: Array Output from downloadable_PlanetIDs
>
>*Outputs:* id_list

**9. order_status(apiKey, item_type, asset_type, id_list)** 
>*Description:* Checks the status of a current order using requested Planet data
>
>*Parameters:*
> - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
> - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
> - asset_type: Product derived from item's source data
> - id_list: Id List created from id_gemoetry_lists Function
>
>*Outputs:* N/A

**10. submit_orders(id_list, item_type, bundle_type, apiKey)** 
>*Description:* Submits requested orders to Planet
>
>*Parameters:*
> - id_list: Id List created from id_gemoetry_lists Function
> - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
> - bundle_type: Product Bundle from Planet
> - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
>
>*Outputs:* order_urls

**11. save_data_to_csv(order_urls)** 
>*Description:* Saves data from order_urls to a csv file
>
>*Parameters:*
> - order_url: order_Urls from Function submit_orders
>
>*Outputs:* N/A

**12. download_orders(order_urls, out_direc, apiKey)** 
>*Description:* Downloads the orders once ready, if data is not ready yet, it will display "data not ready yet
>
>*Parameters:*
> - order_url: order_Urls from Function submit_orders
> - out_direc: Folder location to download data
> - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
>
>*Outputs:* N/A

**13. display_image(fp)** 
>*Description:* Uses Rasterio to Display Tif Image
>
>*Parameters:*
> - fp: Tif Image to be displayed
>
>*Outputs:* N/A



### data_preparation module <a name="data_preparation"></a>
##### [Table of Contents](#table_of_contents)
    
**1. vector_rasterize(dir_vector, dir_raster, dir_out, flag_output)** 
>*Description:* 
>
>*Parameters:*
> - dir_vector: Vector directory (Can be left empty)
> - dir_raster: The directory or the file of planet images (Can be left empty)
> - dir_out: Output directory (Can be left empty)
> - flag_output: Flag output set to true if condition is met to enable raster variable setting
>
>*Outputs:* rasterized

**2. data_labeling(dir_ROI, dir_raster, dir_ROIraster, dir_samples_root, dir_samples)** 
>*Description:* Sets up, labels, and cleans up data for training
>
>*Parameters:*
> - dir_ROI: ROI directory (Can be left empty)
> - dir_raster: The directory or the file of planet images (Can be left empty)
> - dir_ROIraster: ROIraster directory (Can be left empty)
> - dir_samples_root: samples_root directory (Can be left empty)
> - dir_samples: samples directory
>
>*Outputs:* df_train



### model_training module <a name="model_training"></a>
##### [Table of Contents](#table_of_contents)

**1. train_model(dir_model, dir_score, n_estimators, max_depth, max_features, random_state, n_splits, n_repeats, df_train)**
>*Description:* Trains a random forest model for snow covered area evaluations
>
>*Parameters:*
> - dir_model: Model directory
> - dir_score: Score directory
> - n_estimators: n_estimators parameter for RandomForestClassifier(Model parameter)
> - max_depth: max_depth parameter for RandomForestClassifier(Model parameter)
> - max_features: max_features parameter for RandomForestClassifier(Model parameter)
> - random_state: random_state parameter for RandomForestClassifier(Model parameter)
> - n_splits: n_splits parameter for RepeatedStratifiedKFold(Evaluation parameter)
> - n_repeats: n_repeats parameter for RepeatedStratifiedKFold(Evaluation parameter)
> - df_train: Training data from data_labeling Function
>
>*Outputs:* N/A (Saves trained model at dir_model)



### prediction_evaluation module <a name="prediction_evaluation"></a>
##### [Table of Contents](#table_of_contents)

**1. run_sca_prediction(dir_raster, dir_out, nodata_flag, model)**
>*Description:* This function predicts binary snow cover for planet satellite images using the pre-trained random forest model
>
>*Parameters:*
> - dir_raster: The directory or the file of planet images
> - dir_out: The directory where output snow cover images will be stored
> - nodata_flag: The value used to represent no data in the predicted snow cover image
    defult value is 9.
> - model: The model used to predict snow cover
>
>*Outputs:* N/A

**2. run_sca_prediction_band(f_raster, file_out, nodata_flag, model)**
>*Description:* Need help on what the difference for these is
>
>*Parameters:*
> - f_raster: File of planet images
> - file_out: The directory that will store the output file
> - nodata_flag: The value used to represent no data in the predicted snow cover image
    defult value is 9.
> - model: The model used to predict snow cover
>
>*Outputs:* N/A

**3. run_sca_prediction_fusion(dir_raster, dir_out, nodata_flag, model)**
>*Description:* Need help on what the difference for these is
>
>*Parameters:*
> - dir_raster: The directory or the file of planet images
> - dir_out: The directory where output snow cover images will be stored
> - nodata_flag: The value used to represent no data in the predicted snow cover image
    defult value is 9.
> - model: The model used to predict snow cover
>
>*Outputs:* N/A

**4. run_sca_prediction_meadows(dir_raster, dir_out, nodata_flag, model)**
>*Description:* Need help on what the difference for these is
>
>*Parameters:*
> - dir_raster: The directory or the file of planet images
> - dir_out: The directory where output snow cover images will be stored
> - nodata_flag: The value used to represent no data in the predicted snow cover image
    defult value is 9.
> - model: The model used to predict snow cover
>
>*Outputs:* N/A

**5. single_image_evaluation(dir_raster, dir_model, dir_out)**
>*Description:* Uses run_sca_prediction for a single image
>
>*Parameters:*
> - dir_raster: The directory or the file of planet images
> - dir_model: The directory where the model is stored
> - dir_out: The directory where the output snow cover image will be stored
>
>*Outputs:* N/A
