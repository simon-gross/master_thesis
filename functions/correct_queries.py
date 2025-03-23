# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 22:30:37 2024

@author: arbeit
"""

correct_graphdb_requests = [
"""PREFIX geo: <http://www.opengis.net/ont/geosparql#> 
PREFIX geof: <http://www.opengis.net/def/function/geosparql/> 
PREFIX gn: <https://www.geonames.org/ontology#> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 

SELECT ?nutsRegion
WHERE { 
  ?city a gn:Feature ; 
        gn:name "CITY" ; 
        geo:hasGeometry ?cityGeom . 
  ?nutsRegion a skos:Concept ;
    	skos:notation ?code;
        geo:hasGeometry ?nutsGeom . 
  ?nutsGeom geo:asWKT ?nutsWKT . 
  ?cityGeom geo:asWKT ?cityWKT . 
  FILTER(geof:sfContains(?nutsWKT, ?cityWKT)) 
}""",

"""PREFIX geo: <http://www.opengis.net/ont/geosparql#> 
PREFIX geof: <http://www.opengis.net/def/function/geosparql/> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 

SELECT ?otherRegion 
WHERE { 
  ?region geo:hasGeometry ?geom . 
  ?region a skos:Concept .
  ?geom geo:asWKT ?wkt . 
  ?region skos:notation "CODE" . 
  ?otherRegion a skos:Concept .
  ?otherRegion geo:hasGeometry ?otherGeom . 
  ?otherGeom geo:asWKT ?otherWkt . 
  FILTER(geof:sfWithin(?otherWkt, ?wkt)) 
}""",

"""PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?bordering WHERE {
  ?region1 a skos:Concept ;
           skos:notation "CODE" ;
           geo:hasGeometry ?geom1 .
  ?region2 a skos:Concept ;
           skos:notation "CODE" ;
           geo:hasGeometry ?geom2 .
  ?geom1 geo:asWKT ?wkt1 .
  ?geom2 geo:asWKT ?wkt2 .
  BIND(geof:sfTouches(?wkt1, ?wkt2) AS ?bordering)
}""",

"""PREFIX geo: <http://www.opengis.net/ont/geosparql#> 
PREFIX geof: <http://www.opengis.net/def/function/geosparql/> 
PREFIX nutsdef: <http://data.europa.eu/nuts/> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 

SELECT ?neighbor 
WHERE { 
  ?region a skos:Concept ; 
          nutsdef:level ?level ; 
          skos:notation "CODE" ;
    	  geo:hasGeometry ?geomRegion .
  ?neighbor a skos:Concept ; 
            nutsdef:level ?level ; 
            geo:hasGeometry ?geomNeighbor . 
  ?geomRegion geo:asWKT ?regionWKT .
  ?geomNeighbor geo:asWKT ?neighborWKT .
  FILTER(geof:sfTouches(?regionWKT, ?neighborWKT)) 
}""",

"""PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX nutsdef: <http://data.europa.eu/nuts/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/> 

SELECT DISTINCT ?secondOrderNeighbor
WHERE {
  ?region skos:notation "CODE" .
  ?region nutsdef:level ?level .
  
  ?region geo:hasGeometry ?geom1 .
  ?geom1 geo:asWKT ?wkt1 .
  
  ?firstOrderNeighbor nutsdef:level ?level .
  ?firstOrderNeighbor geo:hasGeometry ?geom2 .
  ?geom2 geo:asWKT ?wkt2 .
  
  FILTER(geof:sfTouches(?wkt1, ?wkt2))
  
  ?firstOrderNeighbor geo:hasGeometry ?geom3 .
  ?geom3 geo:asWKT ?wkt3 .
  
  ?secondOrderNeighbor nutsdef:level ?level .
  ?secondOrderNeighbor geo:hasGeometry ?geom4 .
  ?geom4 geo:asWKT ?wkt4 .
  
  FILTER(geof:sfTouches(?wkt3, ?wkt4))
  FILTER(?secondOrderNeighbor != ?region)
}""",

("""PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX nutsdef: <http://data.europa.eu/nuts/>

SELECT ?isDIRECTIONOf WHERE {
  ?regionA skos:notation "CODE" .
  ?regionB skos:notation "CODE" .
  ?regionA geo:hasGeometry ?geometryA .
  ?regionB geo:hasGeometry ?geometryB .
  ?geometryA geo:asWKT ?wktA .
  ?geometryB geo:asWKT ?wktB .
  BIND(geof:isDIRECTIONOf(?wktA, ?wktB) AS ?isDIRECTIONOf)
}
""",
 """
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX nutsdef: <http://data.europa.eu/nuts/>

SELECT ?isDIRECTIONOf WHERE {
  ?regionA skos:notation "CODE" .
  ?regionB skos:notation "CODE" .
  ?regionA geo:hasGeometry ?geometryA .
  ?regionB geo:hasGeometry ?geometryB .
  ?geometryA geo:asWKT ?wktA .
  ?geometryB geo:asWKT ?wktB .
    BIND(IF(geof:isDIRECTION1Of(?wktA, ?wktB) && geof:isDIRECTION2Of(?wktA, ?wktB), "True"^^xsd:boolean, "False"^^xsd:boolean) AS ?isDIRECTIONOf)
}
"""),

("""
PREFIX geo: <http://www.opengis.net/ont/geosparql#> 
PREFIX geof: <http://www.opengis.net/def/function/geosparql/> 
PREFIX gn: <https://www.geonames.org/ontology#> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 

SELECT ?isDIRECTIONOf WHERE {
  ?nutsRegion a skos:Concept ;
              skos:notation "CODE" ;
              geo:hasGeometry ?geomNuts .
  ?city gn:name "CITY" ;
        geo:hasGeometry ?geomCity .
  ?geomNuts geo:asWKT ?wktNuts .
  ?geomCity geo:asWKT ?wktCity .
  BIND(geof:isDIRECTIONOf(?wktNuts, ?wktCity) AS ?isDIRECTIONOf)
}""",
 """PREFIX geo: <http://www.opengis.net/ont/geosparql#> 
PREFIX geof: <http://www.opengis.net/def/function/geosparql/> 
PREFIX gn: <https://www.geonames.org/ontology#> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 

SELECT ?isDIRECTIONOf WHERE {
  ?nutsRegion a skos:Concept ;
              skos:notation "CODE" ;
              geo:hasGeometry ?geomNuts .
  ?city gn:name "CITY" ;
        geo:hasGeometry ?geomCity .
  ?geomNuts geo:asWKT ?wktNuts .
  ?geomCity geo:asWKT ?wktCity .
  BIND(IF(geof:isDIRECTION1Of(?wktNuts, ?wktCity) && geof:isDIRECTION2Of(?wktNuts, ?wktCity), "True"^^xsd:boolean, "False"^^xsd:boolean) AS ?isDIRECTIONOf)
}"""),

"""
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX gn: <https://www.geonames.org/ontology#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?direction WHERE {
  ?city1 gn:name "CITY" .
  ?city2 gn:name "CITY" .
  ?city1 geo:hasGeometry ?geom1 .
  ?city2 geo:hasGeometry ?geom2 .
  ?geom1 geo:asWKT ?wkt1 .
  ?geom2 geo:asWKT ?wkt2 .
  BIND(geof:isEastOf(?wkt1, ?wkt2) AS ?east)
  BIND(geof:isNorthOf(?wkt1, ?wkt2) AS ?north)
  BIND(geof:isSouthOf(?wkt1, ?wkt2) AS ?south)
  BIND(geof:isWestOf(?wkt1, ?wkt2) AS ?west)
  
  BIND(
    IF(?north && ?east, "Northeast"^^xsd:string,
    IF(?north && ?west, "Northwest"^^xsd:string,
    IF(?south && ?east, "Southeast"^^xsd:string,
    IF(?south && ?west, "Southwest"^^xsd:string,
    IF(?north, "North"^^xsd:string,
    IF(?south, "South"^^xsd:string,
    IF(?east, "East"^^xsd:string,
    IF(?west, "West"^^xsd:string,
    "Unknown"^^xsd:string))))))))
    AS ?direction)
}""",
"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX gn: <https://www.geonames.org/ontology#>
PREFIX nutsdef: <http://data.europa.eu/nuts/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?direction WHERE {
  ?region skos:notation "CODE" .
  ?location gn:name "CITY" .
  
  ?region geo:hasGeometry ?regionGeom .
  ?location geo:hasGeometry ?locationGeom .
  
  ?regionGeom geo:asWKT ?regionWKT .
  ?locationGeom geo:asWKT ?locationWKT .
  
  BIND(geof:isEastOf(?locationWKT, ?regionWKT) AS ?east)
  BIND(geof:isNorthOf(?locationWKT, ?regionWKT) AS ?north)
  BIND(geof:isSouthOf(?locationWKT, ?regionWKT) AS ?south)
  BIND(geof:isWestOf(?locationWKT, ?regionWKT) AS ?west)

  BIND(IF(?north && ?east, "Northeast"^^xsd:string, 
           IF(?north && ?west, "Northwest"^^xsd:string, 
           IF(?south && ?east, "Southeast"^^xsd:string, 
           IF(?south && ?west, "Southwest"^^xsd:string, 
           IF(?north, "North"^^xsd:string, 
           IF(?south, "South"^^xsd:string, 
           IF(?east, "East"^^xsd:string, 
           IF(?west, "West"^^xsd:string, 
           "Unknown"^^xsd:string)))))))) AS ?direction)
}""",
"""
PREFIX geo: <http://www.opengis.net/ont/geosparql#> 
PREFIX geof: <http://www.opengis.net/def/function/geosparql/> 
PREFIX gn: <https://www.geonames.org/ontology#> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 

SELECT ?isWithin 
WHERE {
  ?city gn:name "CITY" .
  ?city geo:hasGeometry ?geomCity .
  ?nutsRegion geo:hasGeometry ?geomNuts .
  ?nutsRegion skos:notation "CODE" .
  
  ?geomCity geo:asWKT ?wktCity .
  ?geomNuts geo:asWKT ?wktNuts .
  
  BIND(geof:buffer(?wktNuts, SMALLDISTANCE000) AS ?buffer)
  BIND(geof:sfWithin(?wktCity, ?buffer) AS ?isWithin)
}""",
"""
PREFIX geo: <http://www.opengis.net/ont/geosparql#> 
PREFIX geof: <http://www.opengis.net/def/function/geosparql/> 
PREFIX gn: <https://www.geonames.org/ontology#> 

SELECT ?cityName WHERE {
    ?city a gn:Feature ;
        gn:name ?cityName ;
        geo:hasGeometry ?geom .
    ?geom geo:asWKT ?wkt .
    
    ?city2 a gn:Feature ;
        gn:name "CITY" ;
        gn:name ?city1Name ;
        geo:hasGeometry ?geom2 .
    ?geom2 geo:asWKT ?wkt2 .
    
    FILTER(?cityName != ?city1Name)
    BIND(geof:buffer(?wkt2, SMALLDISTANCE000) AS ?buffer)
    FILTER(geof:sfWithin(?wkt, ?buffer))
}""",
"""
PREFIX geo: <http://www.opengis.net/ont/geosparql#> 
PREFIX geof: <http://www.opengis.net/def/function/geosparql/> 
PREFIX gn: <https://www.geonames.org/ontology#> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 

SELECT ?city ?cityName ?population
WHERE {
  ?city a gn:Feature ;
        gn:population ?population ;
    	gn:name ?cityName ;
        geo:hasGeometry ?cityGeom .
  ?region a skos:Concept ;
          skos:notation "CODE" ;
          geo:hasGeometry ?regionGeom .
  ?cityGeom geo:asWKT ?cityWKT .
  ?regionGeom geo:asWKT ?regionWKT .
  FILTER(?population CCONDITION)
  FILTER(geof:distance(?cityWKT, ?regionWKT) < BIGDISTANCE000)
}""",

"""
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX gn: <https://www.geonames.org/ontology#>
PREFIX nutsdef: <http://data.europa.eu/nuts/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?cityName
WHERE {
  ?nutsRegion skos:notation "CODE" ;
              geo:hasGeometry ?nutsGeom .
  ?nutsGeom geo:asWKT ?nutsWKT .
  
  ?city a gn:Feature ;
        gn:name ?cityName ;
        gn:population ?population ;
        geo:hasGeometry ?cityGeom .
  ?cityGeom geo:asWKT ?cityWKT .
  
  BIND(geof:envelope(?nutsWKT) AS ?envelope)
  FILTER(geof:sfWithin(?cityWKT, ?envelope))
} ORDER BY DESC(?population) LIMIT 1""",

"""
PREFIX dcterms: <http://purl.org/dc/terms/> 
PREFIX fno: <https://w3id.org/function/ontology#> 
PREFIX geo: <http://www.opengis.net/ont/geosparql#> 
PREFIX geof: <http://www.opengis.net/def/function/geosparql/> 
PREFIX gn: <https://www.geonames.org/ontology#> 
PREFIX nutsdef: <http://data.europa.eu/nuts/> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 

SELECT ?cityName WHERE {
  ?region a skos:Concept ;
          skos:notation "CODE" ;
          geo:hasGeometry ?regionGeom .
  ?city a gn:Feature ;
        geo:hasGeometry ?cityGeom ;
    	gn:name ?cityName ;
        gn:population ?population .
  ?regionGeom geo:asWKT ?regionWKT .
  ?cityGeom geo:asWKT ?cityWKT .
  BIND(geof:buffer(?regionWKT, BIGDISTANCE000) AS ?buffer)
  FILTER(geof:sfWithin(?cityWKT, ?buffer))
} ORDER BY DESC(?population) LIMIT 1""",

("""
PREFIX dcterms: <http://purl.org/dc/terms/> 
PREFIX fno: <https://w3id.org/function/ontology#> 
PREFIX geo: <http://www.opengis.net/ont/geosparql#> 
PREFIX geof: <http://www.opengis.net/def/function/geosparql/> 
PREFIX gn: <https://www.geonames.org/ontology#> 
PREFIX nutsdef: <http://data.europa.eu/nuts/> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 

SELECT ?cityName WHERE {
  ?nutsRegion a skos:Concept ;
              skos:notation "CODE" ;
              geo:hasGeometry ?nutsGeom .
  ?city a gn:Feature ;
        gn:name ?cityName ;
        geo:hasGeometry ?cityGeom .
  ?nutsGeom geo:asWKT ?nutsWKT .
  ?cityGeom geo:asWKT ?cityWKT .
  BIND(geof:buffer(?nutsWKT, SMALLDISTANCE000) AS ?buffer)
  FILTER(geof:sfWithin(?cityWKT, ?buffer) && geof:isDIRECTIONOf(?cityWKT, ?nutsWKT))
}
""",
 """
PREFIX dcterms: <http://purl.org/dc/terms/> 
PREFIX fno: <https://w3id.org/function/ontology#> 
PREFIX geo: <http://www.opengis.net/ont/geosparql#> 
PREFIX geof: <http://www.opengis.net/def/function/geosparql/> 
PREFIX gn: <https://www.geonames.org/ontology#> 
PREFIX nutsdef: <http://data.europa.eu/nuts/> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 

SELECT ?cityName WHERE {
  ?nutsRegion a skos:Concept ;
              skos:notation "CODE" ;
              geo:hasGeometry ?nutsGeom .
  ?city a gn:Feature ;
        gn:name ?cityName ;
        geo:hasGeometry ?cityGeom .
  ?nutsGeom geo:asWKT ?nutsWKT .
  ?cityGeom geo:asWKT ?cityWKT .
  BIND(geof:buffer(?nutsWKT, SMALLDISTANCE000) AS ?buffer)
  FILTER(geof:sfWithin(?cityWKT, ?buffer) && geof:isDIRECTION1Of(?cityWKT, ?nutsWKT) && geof:isDIRECTION2Of(?cityWKT, ?nutsWKT))
}"""),

("""
PREFIX dcterms: <http://purl.org/dc/terms/> 
PREFIX fno: <https://w3id.org/function/ontology#> 
PREFIX geo: <http://www.opengis.net/ont/geosparql#> 
PREFIX geof: <http://www.opengis.net/def/function/geosparql/> 
PREFIX gn: <https://www.geonames.org/ontology#> 
PREFIX nutsdef: <http://data.europa.eu/nuts/> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 

SELECT ?cityName WHERE {
  ?cityBase a gn:Feature ;
              gn:name "CITY" ;
              gn:name ?city1Name ;
              geo:hasGeometry ?cityBaseGeom .
  ?city a gn:Feature ;
        gn:name ?cityName ;
        geo:hasGeometry ?cityGeom .
  ?cityBaseGeom geo:asWKT ?cityBaseWKT .
  ?cityGeom geo:asWKT ?cityWKT .
  FILTER(?cityName != ?city1Name)
  BIND(geof:buffer(?cityBaseWKT, SMALLDISTANCE000) AS ?buffer)
  FILTER(geof:sfWithin(?cityWKT, ?buffer) && geof:isDIRECTIONOf(?cityWKT, ?cityBaseWKT))
}
""",
 """
PREFIX dcterms: <http://purl.org/dc/terms/> 
PREFIX fno: <https://w3id.org/function/ontology#> 
PREFIX geo: <http://www.opengis.net/ont/geosparql#> 
PREFIX geof: <http://www.opengis.net/def/function/geosparql/> 
PREFIX gn: <https://www.geonames.org/ontology#> 
PREFIX nutsdef: <http://data.europa.eu/nuts/> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 

SELECT ?cityName WHERE {
  ?cityBase a gn:Feature ;
              gn:name "CITY" ;
              gn:name ?city1Name ;
              geo:hasGeometry ?cityBaseGeom .
  ?city a gn:Feature ;
        gn:name ?cityName ;
        geo:hasGeometry ?cityGeom .
  ?cityBaseGeom geo:asWKT ?cityBaseWKT .
  ?cityGeom geo:asWKT ?cityWKT .
  FILTER(?cityName != ?city1Name)
  BIND(geof:buffer(?cityBaseWKT, SMALLDISTANCE000) AS ?buffer)
  FILTER(geof:sfWithin(?cityWKT, ?buffer) && geof:isDIRECTION1Of(?cityWKT, ?cityBaseWKT) && geof:isDIRECTION2Of(?cityWKT, ?cityBaseWKT))
}"""),

("""
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX nutsdef: <http://data.europa.eu/nuts/>

SELECT ?region WHERE {
  ?region a skos:Concept ;
          nutsdef:level ?level ;
          geo:hasGeometry ?geom .
  ?geom geo:asWKT ?regionWKT .
  
  ?targetRegion a skos:Concept ;
                skos:notation "CODE" ;
                nutsdef:level ?level ;
                geo:hasGeometry ?targetGeom .
  ?targetGeom geo:asWKT ?targetWKT .
  
  FILTER(geof:isDIRECTIONOf(?regionWKT, ?targetWKT))
  FILTER(geof:sfTouches(?regionWKT, ?targetWKT))
}""",
 """
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX nutsdef: <http://data.europa.eu/nuts/>

SELECT ?region WHERE {
  ?region a skos:Concept ;
          nutsdef:level ?level ;
          geo:hasGeometry ?geom .
  ?geom geo:asWKT ?regionWKT .
  
  ?targetRegion a skos:Concept ;
                skos:notation "CODE" ;
                nutsdef:level ?level ;
                geo:hasGeometry ?targetGeom .
  ?targetGeom geo:asWKT ?targetWKT .
  
  FILTER(geof:isDIRECTION1Of(?regionWKT, ?targetWKT))
  FILTER(geof:isDIRECTION2Of(?regionWKT, ?targetWKT))
  FILTER(geof:sfTouches(?regionWKT, ?targetWKT))
}
"""),

("""
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX gn: <https://www.geonames.org/ontology#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX nutsdef: <http://data.europa.eu/nuts/>

SELECT ?cityName ?distance
WHERE {
  ?nutsRegion skos:notation "CODE" ;
              geo:hasGeometry ?nutsGeom .
  ?nutsGeom geo:asWKT ?nutsWKT .
  
  ?city a gn:Feature ;
        gn:name ?cityName ;
        geo:hasGeometry ?cityGeom .
  ?cityGeom geo:asWKT ?cityWKT .
  
  FILTER(geof:isDIRECTIONOf(?cityWKT, ?nutsWKT))
  
  BIND(geof:distance(?nutsWKT, ?cityWKT) AS ?distance)
}
ORDER BY ?distance
LIMIT 1""",
 """
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX gn: <https://www.geonames.org/ontology#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX nutsdef: <http://data.europa.eu/nuts/>

SELECT ?cityName ?distance
WHERE {
  ?nutsRegion skos:notation "CODE" ;
              geo:hasGeometry ?nutsGeom .
  ?nutsGeom geo:asWKT ?nutsWKT .
  
  ?city a gn:Feature ;
        gn:name ?cityName ;
        geo:hasGeometry ?cityGeom .
  ?cityGeom geo:asWKT ?cityWKT .
  
  FILTER(geof:isDIRECTION1Of(?cityWKT, ?nutsWKT))
  FILTER(geof:isDIRECTION2Of(?cityWKT, ?nutsWKT))
  
  BIND(geof:distance(?nutsWKT, ?cityWKT) AS ?distance)
}
ORDER BY ?distance
LIMIT 1""")
]

def get_gt_queries():
    return correct_graphdb_requests
