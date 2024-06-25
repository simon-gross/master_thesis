# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 14:49:44 2024

@author: arbeit
"""

import shapely
from shapely.geometry import shape
import requests
import json


def test_feature_lenght(features):
    if len(features) != 1:
        raise ValueError("TOO MANY FEATURES WHAT IS WRONG?")
        
def test_nuts_codes(code1, code2):
    if not code1 == code2:
        raise ValueError(f"NOT THE SAME NUTS CODES: {code1} - {code2}")
    else:
        pass
        #print("success!")
  
def get_geojson(row):
    url = row['link']
    nuts_code = row['nutscode']
    
    response = requests.get(url)
    
    if response.status_code == 200:
        string = response.text
        features = json.loads(string)['features']
        test_feature_lenght(features)

        nuts_code_response = features[0]['properties']['NUTS_ID']
        test_nuts_codes(nuts_code, nuts_code_response)

        geom = features[0]['geometry']
        geom_shape = shape(geom)
        
        
        return geom_shape
            
    else:
      print(f"Error downloading GeoJSON: {response.status_code}")
      print(row['nutscode'])
      #raise RuntimeError()

def get_geom_build_query(row):
    nutscode = row['nutscode']
    scale = row['scale']
    projection = row['projection']

    geom = row['geometry']
    
    polygon_WKT= str(geom)
    
    if geom is None:
        "EMPTY"
    
    new_geo_object = f":{nutscode}_{scale}_{projection}" #TODO: Write geom behind it
    
    is_empty = "true" if shapely.is_empty(geom) else "false"
    
    query_createGeometryObjects = f"""
PREFIX : <http://geonuts.eu/geometry/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

INSERT DATA {{
    <http://data.europa.eu/nuts/code/{nutscode}> geo:hasGeometry {new_geo_object} .
    {new_geo_object} rdf:type geo:Geometry ;
    				 geo:asWKT "{polygon_WKT}" ;
    				 geo:isEmpty {is_empty}.
}}
    """
    
    return query_createGeometryObjects
    
