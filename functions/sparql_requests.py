import requests
import pandas as pd
import io
import re
import time
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np


graphdb_server_url = 'http://localhost:7200'
repository_id = 'geonuts'
select_endpoint_url = f"http://localhost:7200/repositories/{repository_id}"
update_endpoint_url = f"http://localhost:7200/repositories/{repository_id}/statements"

###################################
def optimize_buffer(query):
    if "geof:buffer" not in query:
        return query

    try:
        pattern = r"geof:buffer\((.*?)\)"
        attributes = re.findall(pattern, query)[0].split(", ")
    
        substring = f"geo:asWKT {attributes[0]} ."
        new_line = f"BIND(geof:buffer({attributes[0]}, {attributes[1]}) AS ?buffer)"
    
        query = re.sub(pattern, "?buffer", query)
        query = re.sub(f"^(.*{re.escape(substring)}.*)$", r"\1\n" + new_line, query, flags=re.MULTILINE)
    except:
        print("Got problems with the above query, likely syntatical Errors while calling the buffer function")
        return "USELESS_BUFFER_QUERY_SYNTAX_ERROR_WITH_BUFFER_FUNCTION"
    return query


def check_prefixes(query, ontology):
    namespace_manager = ontology.namespace_manager
    prefixes = {prefix: str(namespace) for prefix, namespace in namespace_manager.namespaces()}    

    for prefix, val in prefixes.items():
        if f"PREFIX {prefix}: " in query:
            pattern = rf'PREFIX {prefix}: <.*?>'
            replacement = f'PREFIX {prefix}: <{val}>'
            query = re.sub(pattern, replacement, query)
    return query

def replace_nutsdefNotation_with_skosNotation(query):
    if "nutsdef:notation" in query:
        print("found nutsdef:notation!, replacing...")

    query = query.replace(r"nutsdef:notation", r"skos:notation")
    if "PREFIX skos:" not in query:
        query = "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n" + query

    return query

def clean_query(text, ontology_full):
    text = text.replace("`", "")

    if "PREFIX" not in text:
        print("No prefixes generated, query will fail")
        return "USELESS_QUERY_NO_PREFIXES"

    if ontology_full is not None:
        text = check_prefixes(text, ontology_full)

    start_idx = text.find("PREFIX")

    # If the query does not start with PREFIX, it is most likely wrapped in some kind of ticks
    if start_idx != 0:
        end_idx = text.rfind("}")
        if "LIMIT 1" in text:
            end_idx = text.rfind("LIMIT 1") + 7

        if end_idx != 0 and end_idx > start_idx:
            text = text[start_idx:end_idx+1]
    
    # print("Prefixes were checked")
    text = replace_nutsdefNotation_with_skosNotation(text)
    return text

def replace_directions_python(row, return_polys=False):
    if type(row) == pd.Series:
        query = row.answers_cleaned
    elif type(row) == str:
        query = row
    else:
        raise ValueError("THE ROW IS NOT A pd.Series... check the replace directions python function!")
    # print(row.name)
    # time.sleep(0.1)
    # try:
    for direction in ["North", "West", "East", "South"]:
        if f"is{direction}Of" not in query:
            continue

        pattern = fr"geof:is{direction}Of\((.*?)\)"
        try:
            attributes = re.findall(pattern, query, flags=re.DOTALL)[0].split(", ")
        except:
            print("Failed to find the direction call, maybe direction called without function")
            return "USELESS_DIRECTION_QUERY_NO_PATTERN_DETECTED"

        if len(attributes) < 2:
            print("Less than two attributes in the direction function call")
            return "USELESS_DIRECTION_QUERY_WRONG_DIRECTION_FUNCTION_CALL"
        
        query_get_wkts = re.sub(r"SELECT.*?WHERE", f"SELECT {attributes[1]} WHERE", query, flags=re.DOTALL)
        query_get_wkts = re.sub(r"ASK.*?{", f"SELECT {attributes[1]} WHERE {{", query_get_wkts, flags=re.DOTALL)
        query_get_wkts = re.sub(rf".*{f'is.*Of'}.*", "", query_get_wkts)
        


        query_get_wkts = re.sub(r"(.*geo:asWKT.*?)(\n|$).*", r"\1", query_get_wkts, flags=re.DOTALL) + "\n} LIMIT 1"
        try:
        # print(query_get_wkts)
            wkts = sparql_select(query_get_wkts, endpoint_url=select_endpoint_url, print_when_fail=True, sleep=0.2).values[0]
        except:
            # print(query_get_wkts)
            return("USELESS_DIRECTION_QUERY_UNABLE_TO_EXECUTE_SPARQL")
        
        try:
            wkts = gpd.GeoDataFrame(["base"], geometry=gpd.GeoSeries.from_wkt(wkts), crs=3035)
        except:
            print("Results cannot be cast to a geo object, maybe no WKTs used in generation?")
            return "USELESS_DIRECTION_QUERY_CANT_GET_GEOMETRY"
        wkts = wkts.to_crs(4326)

        minx2, miny2, maxx2, maxy2 = wkts.geometry[0].bounds

        xinf_pos = 100
        xinf_neg = -100
        yinf_pos = 80
        yinf_neg = -40
        gran = 2 # granularity of the curve in degrees (every [gran] degree a virtual point)

        north_coords = [(xinf_neg, maxy2), (xinf_neg, yinf_pos), (xinf_pos, yinf_pos), (xinf_pos, maxy2)]
        north_coords.extend([(x, maxy2) for x in np.arange(xinf_pos, xinf_neg, -gran)])
        north_poly = Polygon(north_coords)

        west_coords = [(xinf_neg, yinf_neg), (xinf_neg, yinf_pos), (minx2, yinf_pos)]
        west_coords.extend([(minx2, y) for y in np.arange(yinf_pos, yinf_neg, -gran)])
        west_coords.append((minx2, yinf_neg))
        west_poly = Polygon(west_coords)

        east_coords = [(maxx2, yinf_pos), (xinf_pos, yinf_pos), (xinf_pos, yinf_neg), (maxx2, yinf_neg)]
        east_coords.extend([(maxx2, y) for y in np.arange(yinf_neg, yinf_pos, gran)])
        east_poly = Polygon(east_coords)

        south_coords = [(xinf_pos, miny2), (xinf_pos, yinf_neg), (xinf_neg, yinf_neg), (xinf_neg, miny2)]
        south_coords.extend([(x, miny2) for x in np.arange(xinf_neg, xinf_pos, gran)])
        south_poly = Polygon(south_coords)
        
        dir_polys = gpd.GeoSeries([north_poly, west_poly, east_poly, south_poly], crs=4326)
        dir_polys = dir_polys.to_crs(3035)
        
        if return_polys:
            return dir_polys
        # dir_polys.to_file(r"data\temp.geojson")

        wkt_dict = {}
        wkt_dict["North"] = dir_polys[0].wkt
        wkt_dict["West"] = dir_polys[1].wkt
        wkt_dict["East"] = dir_polys[2].wkt
        wkt_dict["South"] = dir_polys[3].wkt

        query = re.sub(fr"geof:is{direction}Of\(.*?\)", f"geof:sfIntersects({attributes[0]}, '{wkt_dict[direction]}')", query, flags=re.MULTILINE)
    # except:
    #     raise ValueError(row.name)
    return query


###################################
def sparql_select(query, endpoint_url=select_endpoint_url, timeout=500, print_when_fail=True, sleep=0.1):
    time.sleep(sleep)
    if "USELESS_" in query:
        return "NO_SPARQL_TO_TRY"
    
    try:
        response = requests.post(f"{endpoint_url}?timeout={timeout}", data={"query": query}, timeout=timeout)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            return df
        else:
            if print_when_fail:
                print("SPARQL request failed with status code:", response.status_code)
            return f"QUERY_FAILED_CODE_{response.status_code}"
    except requests.Timeout:
        print("timed out")
        return f"TIMEOUT{timeout}"
    except:
        print("SOMETHING WENT WRONG IN PYTHON WITH THE SPARQL EXECUTION")
        # print(query)
        # raise ValueError("Problem with the query")
        return "PYTHON_ERROR_FROM_SPARQL_SELECT"

###################################
def sparql_update(query, update_endpoint_url, select_endpoint_url):
    nbefore = sparql_select("SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }", select_endpoint_url).values[0][0]
    headers = {
        "Content-Type": "application/sparql-update",
        "Accept": "application/sparql-results+json"
    }
    
    response = requests.post(update_endpoint_url, data=query, headers=headers)
    if response.status_code == 204:
        print("SUCESSFUL UPDATE")
        nafter = sparql_select("SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }", select_endpoint_url).values[0][0]
        print(f"Statments Delta: {nafter - nbefore}")
    else:
        print("SPARQL update failed with status code:", response.status_code)

    return response
            

    
def insert_ttl(path, update_endpoint_url, select_endpoint_url):
    """
    The function executes an INSERT query on the database from a .ttl file.
    This is because large queries can be too big to execute directy from a string.

    Parameters
    ----------
    path : str
        Path of the .ttl file.
    update_endpoint_url : str
        The URL for the SPARQL update endpoint.
    select_endpoint_url : str
        The URL for the SPARQL select endpoint..

    Returns
    -------
    None.

    """
    nbefore = sparql_select("SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }", select_endpoint_url).values[0][0]
    
    headers = {
        "Content-Type": "text/turtle"
    }

    with open(path, 'rb') as file:
        response = requests.post(update_endpoint_url, headers=headers, data=file)
        
        if response.status_code == 204:
            print("File uploaded successfully.")
            nafter = sparql_select("SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }", select_endpoint_url).values[0][0]
            print(f"Statments Delta: {nafter - nbefore}")
        else:
            print(f"Failed to upload file. Status code: {response.status_code}")
            print(f"Response: {response.text}")
