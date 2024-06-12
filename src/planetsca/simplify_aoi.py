#https://developers.planet.com/blog/2022/Dec/15/simplifying-your-complex-area-of-interest-a-planet-developers-deep-dive/

import json
import fiona
from shapely.geometry import mapping, shape
from shapely import concave_hull, unary_union

def vertex_count(obj) -> int:
   """"Count the vertices of a GeoJSON-like geometry object.
   Parameters
   ----------
   obj: a GeoJSON-like mapping or an object that provides __geo_interface__

   Returns
   -------
   int

   """
   shp = shape(obj)
   if hasattr(shp, "geoms"):
       return sum(vertex_count(part) for part in shp.geoms)
   elif hasattr(shp, "exterior"):
       return vertex_count(shp.exterior) + sum(vertex_count(rng) for rng in shp.interiors)
   else:
       return len(shp.coords)
   
import json

import fiona
from shapely.geometry import mapping, shape
from shapely import concave_hull, unary_union

#Takes shape file, uses concave_hull to reduce vertexes, UNTESTED
def reduce_vertex(shape_file):
    with fiona.open(shape_file) as collection:
        hulls = [concave_hull(shape(feat["geometry"]), ratio=0.4) for feat in collection]

    dissolved_hulls = unary_union(hulls)

    feat = dict(type="Feature", properties={}, geometry=mapping(dissolved_hulls))

    with open(
    "dissolved-concave-hulls.geojson",
    "w",
    ) as f:
        collection = json.dump({"type": "FeatureCollection", "features": [feat]}, f)

def valid_aoi(obj):
    #Check Vertex limit
    if (vertex_count(obj) > 20000 ):
        print("Vertex count is too high! Reducing number of vertices.")
        reduce_vertex(obj)