#https://developers.planet.com/blog/2022/Dec/15/simplifying-your-complex-area-of-interest-a-planet-developers-deep-dive/

import json
import fiona
import shapefile
import tempfile
import os
from shapely.geometry import mapping, shape, Polygon
from shapely import concave_hull, unary_union
import shutil

def vertex_count(shapefile_path) -> int:
    """Count the vertices of a shapefile.
    Parameters
    ----------
    shapefile_path: str
        The file path to the shapefile (without the .shp extension)

    Returns
    -------
    int
        The total number of vertices in the shapefile.
    """
    sf = shapefile.Reader(shapefile_path)
    total_vertices = 0

    for shape_record in sf.shapeRecords():
        shape = shape_record.shape
        if shape.shapeType == shapefile.POLYGON or shape.shapeType == shapefile.POLYLINE:
            for part in shape.parts:
                total_vertices += len(part.points)
        elif shape.shapeType == shapefile.POINT:
            total_vertices += 1

    return total_vertices
   
#Takes geojson file, uses concave_hull to reduce vertexes, UNTESTED
def reduce_vertex(input_shapefile, output_shapefile):
    with fiona.open(input_shapefile, 'r') as input_layer:
        input_crs = input_layer.crs
        schema = input_layer.schema.copy()
        hulls = []

        for feature in input_layer:
            geom = shape(feature['geometry'])
            reduced_geom = concave_hull(geom, ratio=0.4)
            hulls.append(reduced_geom)

        dissolved_hulls = unary_union(hulls)

        with fiona.open(output_shapefile, 'w', driver='ESRI Shapefile', crs=input_crs, schema=schema) as output_layer:
            output_layer.write({
                'properties': {'id': 1},  # Assuming a single feature output, adjust as necessary
                'geometry': mapping(dissolved_hulls)
            })


#Takes shape file, returns true if there is a hole in the shape file, UNTESTED
def has_holes(shapefile_path):
    with fiona.open(shapefile_path, 'r') as input_layer:
        for feature in input_layer:
            geom = shape(feature['geometry'])
            if geom.type == 'Polygon' and len(geom.interiors) > 0:
                return True
            elif geom.type == 'MultiPolygon':
                for poly in geom:
                    if len(poly.interiors) > 0:
                        return True
    return False

def fill_holes(input_shapefile, output_shapefile):
    with fiona.open(input_shapefile, 'r') as input_layer:
        schema = input_layer.schema
        crs = input_layer.crs

        with fiona.open(output_shapefile, 'w', driver='ESRI Shapefile', schema=schema, crs=crs) as output_layer:
            for feature in input_layer:
                geom = shape(feature['geometry'])
                if geom.type == 'Polygon':
                    filled_geom = Polygon(geom.exterior)
                    output_layer.write({
                        'properties': feature['properties'],
                        'geometry': mapping(filled_geom)
                    })
                elif geom.type == 'MultiPolygon':
                    filled_multipolygon = [Polygon(poly.exterior) for poly in geom]
                    output_layer.write({
                        'properties': feature['properties'],
                        'geometry': mapping(filled_multipolygon)
                    })
                else:
                    # If it's not a polygon or multipolygon, just copy the original feature
                    output_layer.write(feature)

#Perhaps not necessary
def count_exterior_rings(shapefile_path):
    exterior_ring_count = 0
    
    with fiona.open(shapefile_path, 'r') as input_shapefile:
        for feature in input_shapefile:
            geom = shape(feature['geometry'])
            
            if geom.type == 'Polygon':
                exterior_ring_count += 1  # A polygon has one exterior ring
            elif geom.type == 'MultiPolygon':
                exterior_ring_count += len(geom.geoms)  # Each polygon in a multipolygon has one exterior ring
    
    return exterior_ring_count

#Checks for overlapping polygons
def has_overlapping_polygons(shapefile_path):
    with fiona.open(shapefile_path, 'r') as input_shapefile:
        for feature in input_shapefile:
            geom = shape(feature['geometry'])
            
            # Check if geometry is a MultiPolygon
            if geom.type == 'MultiPolygon':
                # Compare each polygon with every other polygon in the MultiPolygon
                for i, polygon1 in enumerate(geom):
                    for j, polygon2 in enumerate(geom):
                        if i != j and polygon1.intersects(polygon2):
                            # Check for actual overlap, not just intersection (e.g., touching borders)
                            if polygon1.overlaps(polygon2):
                                return True
    return False

#Combines all polygons into singular polygon thereby eliminating overlaps
def eliminate_overlaps(input_shapefile, output_shapefile):
    with fiona.open(input_shapefile, 'r') as input_shp:
        # Create the output shapefile with the same schema
        with fiona.open(output_shapefile, 'w', driver=input_shp.driver, crs=input_shp.crs, schema=input_shp.schema) as output_shp:
            all_geoms = []
            
            # Collect all geometries
            for feature in input_shp:
                geom = shape(feature['geometry'])
                all_geoms.append(geom)
            
            # Merge all geometries to eliminate overlaps
            merged_geom = unary_union(all_geoms)
            
            # If the result is a MultiPolygon, write each as a separate feature
            if geom.type == 'MultiPolygon':
                for geom in merged_geom:
                    output_shp.write({
                        'properties': feature['properties'],  # Assuming you want to keep the original properties
                        'geometry': mapping(geom)
                    })
            else:
                # If the result is not a MultiPolygon (e.g., a single Polygon), write it directly
                output_shp.write({
                    'properties': feature['properties'],
                    'geometry': mapping(merged_geom)
                })

#Clips anything in the shapefile that is outside the AOI
def clip_shapefile(shapefile_path, aoi_path, output_shapefile_path):
    # Read the AOI geometry
    with fiona.open(aoi_path, 'r') as aoi_file:
        aoi_geom = next(iter(aoi_file))  # Assuming AOI is a single feature
        aoi_shape = shape(aoi_geom['geometry'])
    
    # Setup the output shapefile
    with fiona.open(shapefile_path, 'r') as input_shp:
        # Use the same schema and CRS for the output shapefile
        schema = input_shp.schema
        crs = input_shp.crs
        
        with fiona.open(output_shapefile_path, 'w', driver='ESRI Shapefile', schema=schema, crs=crs) as output_shp:
            for feature in input_shp:
                feature_shape = shape(feature['geometry'])
                # Clip the feature geometry with the AOI
                clipped_shape = feature_shape.intersection(aoi_shape)
                
                # Skip empty geometries
                if not clipped_shape.is_empty:
                    # Write the clipped geometry to the output shapefile
                    output_shp.write({
                        'properties': feature['properties'],
                        'geometry': mapping(clipped_shape)
                    })


def does_shapefile_clip_aoi(shapefile_path, aoi_path):
    # Read the AOI geometry
    with fiona.open(aoi_path, 'r') as aoi_file:
        aoi_geom = next(iter(aoi_file))  # Assuming AOI is a single feature
        aoi_shape = shape(aoi_geom['geometry'])
    
    # Read and check each geometry in the shapefile
    with fiona.open(shapefile_path, 'r') as shapefile:
        for feature in shapefile:
            feature_shape = shape(feature['geometry'])
            # If any part of the feature is outside the AOI, return True
            if not aoi_shape.contains(feature_shape):
                return True
    # If all features are within the AOI, return False
    return False

#Clips anything in the shapefile that is outside the AOI
def clip_shapefile(shapefile_path, aoi_path, output_shapefile_path):
    # Read the AOI geometry
    with fiona.open(aoi_path, 'r') as aoi_file:
        aoi_geom = next(iter(aoi_file))  # Assuming AOI is a single feature
        aoi_shape = shape(aoi_geom['geometry'])
    
    # Setup the output shapefile
    with fiona.open(shapefile_path, 'r') as input_shp:
        # Use the same schema and CRS for the output shapefile
        schema = input_shp.schema
        crs = input_shp.crs
        
        with fiona.open(output_shapefile_path, 'w', driver='ESRI Shapefile', schema=schema, crs=crs) as output_shp:
            for feature in input_shp:
                feature_shape = shape(feature['geometry'])
                # Clip the feature geometry with the AOI
                clipped_shape = feature_shape.intersection(aoi_shape)
                
                # Skip empty geometries
                if not clipped_shape.is_empty:
                    # Write the clipped geometry to the output shapefile
                    output_shp.write({
                        'properties': feature['properties'],
                        'geometry': mapping(clipped_shape)
                    })


def valid_aoi(input_shapefile, output_shapefile, aoi_path):
    #Check Vertex limit
    temp_shapefile = "temp_output.shp"
    if (vertex_count(input_shapefile) > 1500):
        print("Vertex count is too high. Reducing number of vertices.")
        reduce_vertex(input_shapefile, temp_shapefile)
        input_shapefile = temp_shapefile

    #Check holes/Exterior Rings
    if (has_holes(input_shapefile)):
        print("shape_file contains holes and multiple exterior rings. Filling holes.")
        fill_holes(input_shapefile, temp_shapefile)
        input_shapefile = temp_shapefile

    # #Check exterior rings
    # if (count_exterior_rings > 1):
    #     print("shape_file contains exterior rings. Fixing exterior rings.")
    #Check overlaps

    if (has_overlapping_polygons(input_shapefile)):
        print("shape_file contains overlaps. Correcting overlaps.")
        eliminate_overlaps(input_shapefile, temp_shapefile)
        input_shapefile = temp_shapefile

    #Check clipping
    if (does_shapefile_clip_aoi(input_shapefile, aoi_path)):
        print("shape_file contains clipping. Fixing now.")
        clip_shapefile(input_shapefile, aoi_path, temp_shapefile)
        input_shapefile = temp_shapefile

    shutil.copy(temp_shapefile, output_shapefile)

    
def convert_shapefile_to_geojson(shapefile_path, geojson_path):
    # Open the shapefile
    with fiona.open(shapefile_path, 'r') as shapefile:
        # Define the GeoJSON structure
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        
        # Iterate over shapefile features and add them to the GeoJSON structure
        for feature in shapefile:
            geojson['features'].append(feature)
    
    # Write the GeoJSON structure to a file
    with open(geojson_path, 'w') as f:
        json.dump(geojson, f)