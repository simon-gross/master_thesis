# # -*- coding: utf-8 -*-
# """
# Created on Fri Jun  7 15:49:20 2024

# @author: simon-gross
# """
import json
import requests
from shapely.geometry import shape

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
    """
    The function uses a row of a dataframe with columns corresponding to the download link
    'link' and the NUTS code 'nutscode' to download the actual geojson geometries and saves their
    WKT representations.

    Parameters
    ----------
    row : pd.Series
        a row of a dataframe containing at least a 'link' and a 'nutscode'

    Returns
    -------
    geom_shape : shapely.geometry
        the WKT representation of the downloaded geometry

    """
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
    """
    The functions creates a SPARQL query to create GeoSPARQL geo:Geometry 
    triples from the row, containing the geodata.

    Parameters
    ----------
    row : pd.Series
        The row containing all data associated with one NUTS region

    Returns
    -------
    query_createGeometryObjects : str
        The part of the SPARQL query that creates the triples for one NUTS region.

    """
    nutscode = row['nutscode']
    scale = row['scale']
    projection = row['projection']

    geom = row['geometry']
    
    polygon_WKT = str(geom)
    
    if geom is None:
        polygon_WKT = "EMPTY"
    
    new_geo_object = f":{nutscode}_{scale}_{projection}_geom"
    
    
    query_createGeometryObjects = f"""
<http://data.europa.eu/nuts/code/{nutscode}> geo:hasGeometry {new_geo_object} .
{new_geo_object} rdf:type geo:Geometry ;
 				 geo:asWKT "{polygon_WKT}"^^geo:wktLiteral .

    """
    
    return query_createGeometryObjects

def get_geom_build_query_geonames(row):
    """
    The function generates the triples for a single geo:Geometry object
    for one geonames object.

    Parameters
    ----------
    row : pd.Series
        The row in the DataFrame containing the geoinformation.

    Returns
    -------
    query_createGeometryObjects : str
        The part of the query for this object.

    """
    geonameid = row['geonameid']

    geom = row['geometry']
    
    
    
    polygon_WKT = str(geom)
    
    if geom is None:
        polygon_WKT = "EMPTY"
    
    new_geo_object = f":gn_{geonameid}_geom"

    query_createGeometryObjects = f"""
<https://sws.geonames.org/{geonameid}/> geo:hasGeometry {new_geo_object} .
{new_geo_object} rdf:type geo:Geometry ;
 				 geo:asWKT "{polygon_WKT}"^^geo:wktLiteral .
    """
    
    return query_createGeometryObjects


def df_add_geom_triples_geonames(df, path='data/triples.ttl'):
    """
    This function adds the triples to each geo:Geometry object associated
    with a specific geoname object.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the geospatial information for each geoname object.
    path : str, optional
        The path where to store the INSERT query as a .ttl file.
        The default is 'data/triples.ttl'.

    Returns
    -------
    None.

    """
    query = """
    PREFIX : <http://geonuts.eu/geometry/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    """
    
    with open(path, 'w', encoding='utf-8') as file:
        file.write(query)
    
    sparql_updates = df.apply(get_geom_build_query_geonames, axis=1)
    
    with open(path, 'a', encoding='utf-8') as file:
        for i, ext in enumerate(sparql_updates):
            file.write(ext)
            
            
def define_triples_from_table(row):
    """
    The function generates the SPARQL triples for a specific row of geonames data.

    Parameters
    ----------
    row : pd.Series
        A row in a dataframe containing information about geonames.

    Returns
    -------
    query : str
        The part of a SPARQL update query that adds the triples for this row.

    """
    query = """"""

    subject = "<https://sws.geonames.org/NUMBER/>".replace("NUMBER", str(row["geonameid"]))
    
    query += ("\n"+subject)
    query += ("\n"+	"rdf:type gn:Feature;")

    if type(row['name']) == str:
        name = row['name'].replace('"', '')
        query += f'\ngn:name "{name}";'

    if type(row['alternatenames']) == str:
        names = row['alternatenames'].split(",")
        for name in names:
            name = name.replace('"', '')
            query += f'\ngn:alternateName "{name}";'

    if type(row['country code']) == str:
        query += f"\ngn:countryCode '{row['country code']}';"

    if type(row['population']) == int:
        query += f"\ngn:population '{str(row['population'])}'^^xsd:integer;"
        
    if type(row['geonameid']) == int:
        query += f"\ngn:geonamesID '{str(row['geonameid'])}';"

    query = query[:-1] + "."
    return query
      


def df_define_triples_from_table_as_ttl(df, path='data/triples.ttl'):
    """
    The function takes a full dataframe and transforms each row into
    the relevant triples. The resulting full query is saved as a .ttl file.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containg all relevant information.
    path : str, optional
        The path to save the .ttl file. The default is 'data/triples.ttl'.

    Returns
    -------
    None.

    """
    query = """PREFIX gn: <https://www.geonames.org/ontology#>
PREFIX wgs: <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

"""

    with open(path, 'w', encoding='utf-8') as file:
        file.write(query)
    
    extentions = df.apply(define_triples_from_table, axis=1)

        
    with open(path, 'a', encoding='utf-8') as file:
        for i, ext in enumerate(extentions):
            file.write(ext)
    
