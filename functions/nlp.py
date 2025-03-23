# # -*- coding: utf-8 -*-
# """
# Created on Sun Nov 17 10:22:22 2024

# @author: arbeit
# """

from functions.query_collection import *
from functions.sparql_requests import *

cconditions = ["that have more than 100 thousand inhabitants", "that have more than 150000 residents", "with more than a 120 k people", "that are bigger than 99,999"]
cconditions_code = ["> 100000", "> 150000", "> 120000", "> 99999"]

def populate_question(row):
    # if row.name % 70 == 0:
    #     print(row.name) 
    question = row.question_raw

    inputs = {}

    question = question.replace("DIRECTION", row["direction"])

    if "DIRECTION" in row.variables:
        if row.intercardinal:
            gt_query = row.gt_query_raw[1]
            
            dir1 = "South"
            if "north" in row['direction']:
                dir1 = "North"
            dir2 = "West"
            if "east" in row["direction"]:
                dir2 = "East"
    
            gt_query = gt_query.replace("DIRECTION1", dir1, 1)
            gt_query = gt_query.replace("DIRECTION2", dir2, 1)
    
        else:
            gt_query = row.gt_query_raw[0]
            dir1 = row["direction"][0].upper() + row["direction"][1:]
            gt_query = gt_query.replace("DIRECTION", dir1)

    else:
        gt_query = row.gt_query_raw
    
    # if the question asks about a city and a region these should also not be too far apart
    if "CITY" in row["variables"] and "CODE" in row["variables"]:
        code, city = get_two_rand_codes(level=row["NUTS level"], only_cities_bigger_than=row["min inhabitants city"], get_city_instead_of_code2=True)
        question = question.replace("CODE", code)
        question = question.replace("CITY", city)

        gt_query = gt_query.replace("CODE", code)
        gt_query = gt_query.replace("CITY", city)
        inputs['CODE'] = code
        inputs['CITY'] = city
        
    # get two NUTS codes based on the specified NUTS level for this example
    if 'CODE' in question:
        two_codes = get_two_rand_codes(row['NUTS level'])
        question = question.replace("CODE", two_codes[0], 1) # replace only one code
        gt_query = gt_query.replace("CODE", two_codes[0], 1) # replace only one code
        
        inputs['CODE'] = two_codes[0]
        
        if 'CODE' in question:
            question = question.replace("CODE", two_codes[1], 1) # replaces the second code (if there is one)
            gt_query = gt_query.replace("CODE", two_codes[1], 1) # replaces the second code (if there is one)
            
            inputs['CODE'] = two_codes

    
    
    if 'CITY' in question:
        two_cities = get_two_rand_cities(row["min inhabitants city"])
        question = question.replace("CITY", two_cities[0], 1)
        gt_query = gt_query.replace("CITY", two_cities[0], 1)

        inputs['CITY'] = two_cities[0]
        
        if 'CITY' in question:
            question = question.replace("CITY", two_cities[1], 1)
            gt_query = gt_query.replace("CITY", two_cities[1], 1)

            inputs['CITY'] = two_cities


    question = question.replace("SMALLDISTANCE", str(row["small_distance"]))
    gt_query = gt_query.replace("SMALLDISTANCE", str(row["small_distance"]))

    question = question.replace("BIGDISTANCE", str(row["big_distance"]))
    gt_query = gt_query.replace("BIGDISTANCE", str(row["big_distance"]))

    if "CCONDITION" in question:
        question = question.replace("CCONDITION", row["city_condition"])
    
        idx = cconditions.index(row["city_condition"])
        gt_query = gt_query.replace("CCONDITION", cconditions_code[idx])

    # print(gt_query)
    gt_query = replace_directions_python(gt_query)
    
    return question, gt_query, inputs

