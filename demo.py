import os
import itertools
from rdflib import Graph
from openai import OpenAI
from functions.llm_functions import run_client_openai
from functions.sparql_requests import *

template = """
Write a SPARQL SELECT query for querying a graph database.
The ontology schema delimited by triple backticks in Turtle format is:
```
{}
```
Use only the classes and properties provided in the schema to construct the SPARQL query.
Do not use any classes or properties that are not explicitly provided in the SPARQL query.
Include all necessary prefixes.
Do not include any explanations or apologies in your responses.
Do not wrap the query in backticks.
Do not include any text except the SPARQL query generated.
The question delimited by triple backticks is:
```
{}
```
"""

sysmsg = """You are an AI assistant that writes SPARQL queries to a graph database based on a user question and the graphs' ontology. The questions are about the location and topology of the graphs elements. Your answer should only contain the SPARQL query. Keep in mind that geofunctions can only be used with a WKT literal that is attached to a geometry subject: '?geom geo:asWKT ?wkt'"""

graphdb_server_url = 'http://localhost:7200'
repository_id = 'geonuts'
select_endpoint_url = f"http://localhost:7200/repositories/{repository_id}"
update_endpoint_url = f"http://localhost:7200/repositories/{repository_id}/statements"

ontology_full = Graph()
ontology_full = ontology_full.parse("data/ontology_full_v1.ttl", format="turtle")
ontology_full_turtle = ontology_full.serialize(format="turtle")

client = OpenAI(api_key = os.environ['OPENAI1'])
ft_model_name = os.environ.get('FT_MODEL')

    
q = """
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX nutsdef: <http://data.europa.eu/nuts/>

SELECT ?neighborRegion
WHERE {
  ?region skos:notation "AT22" ;
          nutsdef:level ?level ;
          geo:hasGeometry/geo:asWKT ?wkt1 .
  
  ?neighborRegion skos:notation ?neighborNotation ;
                  nutsdef:level ?level ;
                  geo:hasGeometry/geo:asWKT ?wkt2 .
  
  FILTER(?neighborNotation != "AT22")
  FILTER(geof:sfTouches(?wkt1, ?wkt2))
}
"""

examples = ["What is the closest NUTS level 3 region to Munich that is not in Germany?",
            "What are all cities West of Berlin with that have more inhabitants?",
            "For all cities less than 50 km from Vienna, what is the average number of inhabitants? only consider cities with more than 15000 people.",
            "What are all cities with more than 80000 people in France that are closer to Monaco than to Paris?",                # Takes all the cities everywhere -> because country not specified in the ontology
            ]


if __name__ == "__main__":
    while True:
        question = input("""Ask about cities in Europe, NUTS regions and their spatial relationships.
    The questions should be answerable using the classes, relations and functions in the ontology:\n""")
    
        query = run_client_openai(sysmsg, usermsg=template.format(ontology_full_turtle, question),\
                                  model="gpt-4o")
        query = query[0]
        # query = q
        
        query = clean_query(query, ontology_full)
        query = replace_directions_python(query)
        query = optimize_buffer(query)
        
        print(query)
        
        print(sparql_select(query))
        
        y = input("Exit? Y/N")
        if y == "Y":
            break
    