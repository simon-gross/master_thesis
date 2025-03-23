# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 17:45:16 2024

@author: arbeit
"""
import re
import geopandas as gpd
from functions.sparql_requests import sparql_select

query = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX nutsdef: <http://data.europa.eu/nuts/> 

SELECT ?code ?wkt WHERE {
    ?region a geo:Feature ;
        geo:hasGeometry ?geom ;
     	owl:versionInfo "2024" ;
        nutsdef:level "LEVEL" ;
        skos:notation ?code .
    ?region geo:hasGeometry ?geom .
    ?geom geo:asWKT ?wkt .
}"""

gdfs = []

query_cities = """
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX gn: <https://www.geonames.org/ontology#>
SELECT ?name ?population ?wkt WHERE {
    ?city a gn:Feature .
    ?city gn:name ?name .
    ?city gn:population ?population .
    ?city geo:hasGeometry ?geom .
    ?geom geo:asWKT ?wkt .
}
"""

cities = sparql_select(query_cities, sleep=1)
cities = gpd.GeoDataFrame(cities, geometry=gpd.GeoSeries.from_wkt(cities.wkt), crs=3035)


for i in range(0, 4):
    q = query.replace("LEVEL", str(i))
    # print(q)
    df = sparql_select(q, sleep=1)

    df = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df.wkt), crs=3035)
    gdfs.append(df)
    
q = query.replace('nutsdef:level "LEVEL" ;', "####")
df = sparql_select(q)

df = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df.wkt), crs=3035)
gdfs.append(df)


def get_two_rand_codes(level=None, only_cities_bigger_than=None, get_city_instead_of_code2=False):
    
    if level is None:
        level = 4
        
    buffersizes = [5000000, 750000, 250000, 100000, 250000]
    buffersize = buffersizes[level]

    while True:
        gdf = gdfs[i]
        sam = gdf.sample(1)
        code = sam.code.values[0]
        wkt = sam.geometry.values[0]
        idx = sam.index[0]
        
        if get_city_instead_of_code2:
            temp = cities[cities.geometry.distance(wkt) < buffersize]
            
            if only_cities_bigger_than is not None:
                temp = temp[temp.population > only_cities_bigger_than]
            if len(temp) > 0:  
                code2 = temp.name.sample(1).values[0]
                return [code, code2]
            
                
        temp = gdf[gdf.geometry.distance(wkt) < buffersize]
        temp = temp.drop(idx)
        
        if len(temp) > 0:  
            code2 = temp.code.sample(1).values[0]
            return [code, code2]
        else:
            print(f"FOUND NO CODE NEARBY CODE {code}, REINTERATING...")
            


def get_two_rand_cities(only_cities_bigger_than=None):
    temp = cities
    if only_cities_bigger_than is not None:
        temp = temp[temp.population > only_cities_bigger_than]
        
    ret = cities.name.sample(2).values.flatten().tolist()
    
    return ret
        