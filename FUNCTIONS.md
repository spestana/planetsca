## Functions

### data_gathering module

1. build_payload(item_ids, item_type, bundle_type, aoi_coordinates): Builds Payload to send to Planet
   - item_ids: Item ID from Planet
   - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
   - bundle_type: Product Bundle from Planet
   - aoi_coordinates: Area of Interest Coordinates
   - Return:

2. order_now(payload,apiKey): Order using Payload from Planet
   - payload: Payload to send to Planet
   - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
   - 

3. download_results(order_url, folder, apiKey, overwrite=False): Download results from Planet using an order_url
   - order_url: order_Urls from Function submit_orders
   - folder: Output folder
   - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)

4. domain_shape(): Returns the shape of the domain array

5. api_search(item_type, apiKey): Searches for API Key
   - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
   - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
     
7. downloadable_PlanetIDs(result, domain_geometry)
    - result: Result Output from api_search Function
    - domain_geometry: Domain_geometry Output from domain_shape Function
   
8. id_gemoetry_lists(geojson_data, gdf)
    - geojson_data: geojson_data Output from downloadble_PlanetIDs
    - gdf: Array Output from downloadable_PlanetIDs
   
9. order_status(apiKey, item_type, asset_type, id_list)
    - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)
    - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
    - asset_type: Product derived from item's source data
    - id_list: Id List created from id_gemoetry_lists Function
   
10. submit_orders(id_list, item_type, bundle_type, apiKey)
    - id_list: Id List created from id_gemoetry_lists Function
    - item_type: Item Type from the Planet Catalog, ex: PSScene OR REOrthoTile [More Info](https://developers.planet.com/docs/apis/data/items-assets/)
    -  bundle_type: Product Bundle from Planet
    - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)

11. save_data_to_csv(order_urls)
    - order_url: order_Urls from Function submit_orders

12. download_orders(order_urls, out_direc, apiKey): Downloads the orders once ready, if data is not ready yet, it will display "data not ready yet"
    - order_url: order_Urls from Function submit_orders
    - out_direc: Folder location to download data
    - apiKey: Your Personal API Key from Planet [More Info](https://developers.planet.com/quickstart/apis/)

13. display_image(fp): Uses Rasterio to Display Tif Image
    - fp: Tif Image to be displayed

