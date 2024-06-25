import requests
import pandas as pd
import io

graphdb_server_url = 'http://localhost:7200'
repository_id = 'test_geosparql'
select_endpoint_url = "http://localhost:7200/repositories/test_geosparql"
update_endpoint_url = "http://localhost:7200/repositories/test_geosparql/statements"
base_iri_geometry = "http://geonuts.eu/geometry/"

###################################
def sparql_select(query, endpoint_url=select_endpoint_url):
    response = requests.post(endpoint_url, data={"query": query})
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text))
        return df
    else:
        print("SPARQL request failed with status code:", response.status_code)

###################################
def sparql_update(query, update_endpoint_url=update_endpoint_url):
    headers = {
        "Content-Type": "application/sparql-update",
        "Accept": "application/sparql-results+json"
    }
    
    response = requests.post(update_endpoint_url, data=query, headers=headers)
    if response.status_code == 204:
        print("SUCESSFUL UPDATE")
    else:
        print("SPARQL update failed with status code:", response.status_code)

    return response