## Functions

### Table of Contents <a name="table_of_contents"></a>

1. [Data Gathering Module](#data_gathering)
2. [Data_Preparation Module](#data_preparation)
3. [Model Training Module](#model_training)
4. [Prediction Evaluation Module](#prediction_evaluation)

<br/><br/>

### data_gathering module <a name="data_gathering"></a>

##### [Table of Contents](#table_of_contents)

**1. build_payload(item_ids, item_type, bundle_type, aoi_coordinates)**

> _Description:_ Builds Payload to send to Planet
>
> _Parameters:_
>
> - item_ids: Item ID from Planet
> - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile
>   [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
> - bundle_type: Product Bundle from Planet
> - aoi_coordinates: Area of Interest Coordinates
>
> _Outputs:_ payload

**2. order_now(payload,apiKey)**

> _Description:_ Order using Payload from Planet
>
> _Parameters:_
>
> - payload: Payload to send to Planet
> - apiKey: Your Personal API Key from Planet
>   [More Info](https://developers.planet.com/quickstart/apis/)
>
> _Outputs:_ Returns Planet Order Link

**3. download_results(order_url, folder, apiKey, overwrite=False)**

> _Description:_ Download results from Planet using an order_url
>
> _Parameters:_
>
> - order_url: order_Urls from Function submit_orders
> - folder: Output folder
> - apiKey: Your Personal API Key from Planet
>   [More Info](https://developers.planet.com/quickstart/apis/)
>
> _Outputs:_ N/A

**4. domain_shape()**

> _Description:_ Returns the shape of the domain array
>
> _Parameters:_ N/A
>
> _Outputs:_ Shape of domain array

**5. api_search(item_type, apiKey)**

> _Description:_ Searches for API Key
>
> _Parameters:_
>
> - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile
>   [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
> - apiKey: Your Personal API Key from Planet
>   [More Info](https://developers.planet.com/quickstart/apis/)
>
> _Outputs:_ Result

**6. downloadable_PlanetIDs(result, domain_geometry)**

> _Description:_ Creates geojson_data and gdf which is the overlap from the
> domain_geometry
>
> _Parameters:_
>
> - result: Result Output from api_search Function
> - domain_geometry: Domain_geometry Output from domain_shape Function
>
> _Outputs:_ geojson_data, gdf

**8. id_gemoetry_lists(geojson_data, gdf)**

> _Description:_ Prints the length and sorted versions of id_list from
> geojson_data and gdf
>
> _Parameters:_
>
> - geojson_data: geojson_data Output from downloadble_PlanetIDs
> - gdf: Array Output from downloadable_PlanetIDs
>
> _Outputs:_ id_list

**9. order_status(apiKey, item_type, asset_type, id_list)**

> _Description:_ Checks the status of a current order using requested Planet
> data
>
> _Parameters:_
>
> - apiKey: Your Personal API Key from Planet
>   [More Info](https://developers.planet.com/quickstart/apis/)
> - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile
>   [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
> - asset_type: Product derived from item's source data
> - id_list: Id List created from id_gemoetry_lists Function
>
> _Outputs:_ N/A

**10. submit_orders(id_list, item_type, bundle_type, apiKey)**

> _Description:_ Submits requested orders to Planet
>
> _Parameters:_
>
> - id_list: Id List created from id_gemoetry_lists Function
> - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile
>   [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
> - bundle_type: Product Bundle from Planet
> - apiKey: Your Personal API Key from Planet
>   [More Info](https://developers.planet.com/quickstart/apis/)
>
> _Outputs:_ order_urls

**11. save_data_to_csv(order_urls)**

> _Description:_ Saves data from order_urls to a csv file
>
> _Parameters:_
>
> - order_url: order_Urls from Function submit_orders
>
> _Outputs:_ N/A

**12. download_orders(order_urls, out_direc, apiKey)**

> _Description:_ Downloads the orders once ready, if data is not ready yet, it
> will display "data not ready yet
>
> _Parameters:_
>
> - order_url: order_Urls from Function submit_orders
> - out_direc: Folder location to download data
> - apiKey: Your Personal API Key from Planet
>   [More Info](https://developers.planet.com/quickstart/apis/)
>
> _Outputs:_ N/A

**13. display_image(fp)**

> _Description:_ Uses Rasterio to Display Tif Image
>
> _Parameters:_
>
> - fp: Tif Image to be displayed
>
> _Outputs:_ N/A

<br/><br/>

### data_preparation module <a name="data_preparation"></a>

##### [Table of Contents](#table_of_contents)

**1. vector_rasterize(dir_vector, dir_raster, dir_out, flag_output)**

> _Description:_
>
> _Parameters:_
>
> - dir_vector: Vector directory (Can be left empty)
> - dir_raster: The directory or the file of planet images (Can be left empty)
> - dir_out: Output directory (Can be left empty)
> - flag_output: Flag output set to true if condition is met to enable raster
>   variable setting
>
> _Outputs:_ rasterized

**2. data_labeling(dir_ROI, dir_raster, dir_ROIraster, dir_samples_root,
dir_samples)**

> _Description:_ Sets up, labels, and cleans up data for training
>
> _Parameters:_
>
> - dir_ROI: ROI directory (Can be left empty)
> - dir_raster: The directory or the file of planet images (Can be left empty)
> - dir_ROIraster: ROIraster directory (Can be left empty)
> - dir_samples_root: samples_root directory (Can be left empty)
> - dir_samples: samples directory
>
> _Outputs:_ df_train

<br/><br/>

### model_training module <a name="model_training"></a>

##### [Table of Contents](#table_of_contents)

**1. train_model(dir_model, dir_score, n_estimators, max_depth, max_features,
random_state, n_splits, n_repeats, df_train)**

> _Description:_ Trains a random forest model for snow covered area evaluations
>
> _Parameters:_
>
> - dir_model: Model directory
> - dir_score: Score directory
> - n_estimators: n_estimators parameter for RandomForestClassifier(Model
>   parameter)
> - max_depth: max_depth parameter for RandomForestClassifier(Model parameter)
> - max_features: max_features parameter for RandomForestClassifier(Model
>   parameter)
> - random_state: random_state parameter for RandomForestClassifier(Model
>   parameter)
> - n_splits: n_splits parameter for RepeatedStratifiedKFold(Evaluation
>   parameter)
> - n_repeats: n_repeats parameter for RepeatedStratifiedKFold(Evaluation
>   parameter)
> - df_train: Training data from data_labeling Function
>
> _Outputs:_ N/A (Saves trained model at dir_model)

<br/><br/>

### prediction_evaluation module <a name="prediction_evaluation"></a>

##### [Table of Contents](#table_of_contents)

**1. run_sca_prediction(dir_raster, dir_out, nodata_flag, model)**

> _Description:_ This function predicts binary snow cover for planet satellite
> images using the pre-trained random forest model
>
> _Parameters:_
>
> - dir_raster: The directory or the file of planet images
> - dir_out: The directory where output snow cover images will be stored
> - nodata_flag: The value used to represent no data in the predicted snow cover
>   image

    default value is 9.

> - model: The model used to predict snow cover
>
> _Outputs:_ N/A

**2. run_sca_prediction_band(f_raster, file_out, nodata_flag, model)**

> _Description:_ Need help on what the difference for these is
>
> _Parameters:_
>
> - f_raster: File of planet images
> - file_out: The directory that will store the output file
> - nodata_flag: The value used to represent no data in the predicted snow cover
>   image

    default value is 9.

> - model: The model used to predict snow cover
>
> _Outputs:_ N/A

**3. run_sca_prediction_fusion(dir_raster, dir_out, nodata_flag, model)**

> _Description:_ Need help on what the difference for these is
>
> _Parameters:_
>
> - dir_raster: The directory or the file of planet images
> - dir_out: The directory where output snow cover images will be stored
> - nodata_flag: The value used to represent no data in the predicted snow cover
>   image

    default value is 9.

> - model: The model used to predict snow cover
>
> _Outputs:_ N/A

**4. run_sca_prediction_meadows(dir_raster, dir_out, nodata_flag, model)**

> _Description:_ Need help on what the difference for these is
>
> _Parameters:_
>
> - dir_raster: The directory or the file of planet images
> - dir_out: The directory where output snow cover images will be stored
> - nodata_flag: The value used to represent no data in the predicted snow cover
>   image

    default value is 9.

> - model: The model used to predict snow cover
>
> _Outputs:_ N/A

**5. single_image_evaluation(dir_raster, dir_model, dir_out)**

> _Description:_ Uses run_sca_prediction for a single image
>
> _Parameters:_
>
> - dir_raster: The directory or the file of planet images
> - dir_model: The directory where the model is stored
> - dir_out: The directory where the output snow cover image will be stored
>
> _Outputs:_ N/A
