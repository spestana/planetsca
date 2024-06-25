#https://developers.planet.com/blog/2022/Dec/15/simplifying-your-complex-area-of-interest-a-planet-developers-deep-dive/

import json

import fiona
from shapely.geometry import mapping, shape
from shapely import concave_hull, unary_union

def vertex_count_from_geojson(file_path: str) -> int:
    """
    Count the vertices of a GeoJSON-like geometry object.

    Parameters:
    - file_path: The path to the GeoJSON file.

    Returns:
    - int: The total number of vertices.
    """
    with open(file_path) as f:
        data = json.load(f)

    features = data["features"]
    total_vertices = 0

    for feature in features:
        geometry = feature["geometry"]
        shp = shape(geometry)
        total_vertices += count_vertices(shp)

    return total_vertices


def count_vertices(shp) -> int:
    """
    Helper function to count the vertices of a Shapely geometry object.

    Parameters:
    - shp: A Shapely geometry object.

    Returns:
    - int: The number of vertices.
    """
    if hasattr(shp, "geoms"):
        return sum(count_vertices(part) for part in shp.geoms)
    elif hasattr(shp, "exterior"):
        return count_vertices(shp.exterior) + sum(count_vertices(rng) for rng in shp.interiors)
    else:
        return len(shp.coords)
   


def simplify_geojson(input_file, output_file, ratio=0.4):
    with fiona.open(input_file) as collection:
        hulls = [concave_hull(shape(feat["geometry"]), ratio=ratio) for feat in collection]

    dissolved_hulls = unary_union(hulls)

    feat = dict(type="Feature", properties={}, geometry=mapping(dissolved_hulls))

    with open(output_file, "w") as f:
        json.dump({"type": "FeatureCollection", "features": [feat]}, f)
