## Functions

### data_gathering module

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

 
    

