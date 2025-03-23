# # -*- coding: utf-8 -*-
# """
# Created on Fri Dec  6 14:57:55 2024

# @author: arbeit
# """

from sklearn.metrics import precision_score, recall_score, f1_score
from functions.sparql_requests import sparql_select
import pandas as pd
import re

cleaning_regex = r"[^\w']"

all_nuts_codes_query = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?code WHERE {
    ?region a skos:Concept .
    ?region skos:notation ?code .
}"""
all_nuts = sparql_select(all_nuts_codes_query).code.values.tolist()
all_nuts = set(all_nuts)

all_nuts_codes_query = """
PREFIX gn: <https://www.geonames.org/ontology#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?name WHERE {
    ?region a gn:Feature .
    ?region gn:name ?name .
}"""
all_cities = sparql_select(all_nuts_codes_query).name.values.tolist()
all_cities = set(all_cities)
all_cities_clean = {re.sub(cleaning_regex, '', token).lower() for token in all_cities}


all_altnames_query = """
PREFIX gn: <https://www.geonames.org/ontology#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?cityname ?altname WHERE {
    ?region a gn:Feature .
    ?region gn:name ?cityname .
    ?region gn:alternateName ?altname .
}"""
obj = sparql_select(all_altnames_query)
all_altnames = set(obj.altname)

all_altnames_dict_for_clean = {}
for name in all_altnames:
    cleaned = re.sub(cleaning_regex, '', str(name).lower())
    
    if cleaned in all_altnames_dict_for_clean:
        if not all_altnames_dict_for_clean[cleaned][0].lower() == name.lower():
            all_altnames_dict_for_clean[cleaned].append(name)
    else:
        all_altnames_dict_for_clean[cleaned] = [name]
        
gt_correct_name_query = """PREFIX gn: <https://www.geonames.org/ontology#>
SELECT ?name WHERE {
    ?city a gn:Feature .
    ?city gn:name ?name .
    ?city gn:alternateName "ALTNAME"
}"""


# ##### NON RAG FUNCTIONS #####

def detect_codes(row):
    answer = row.non_rag_answers

    pattern = r'(?!NUTS)(?!UTS)(?!TS)[A-Z]{2}[A-Z0-9]{0,3}'
    
    all_detected_nuts = set(re.findall(pattern, answer))
    if len(all_detected_nuts) == 0:
        return [all_detected_nuts, all_detected_nuts, all_detected_nuts]
    
    all_existing = all_detected_nuts & all_nuts
    all_hallucinated = all_detected_nuts - all_nuts

    if len(all_existing) == 0:
        return all_detected_nuts, all_existing, all_hallucinated

    return all_detected_nuts, all_existing, all_hallucinated

def detect_direction(answer):
    directions = {"north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"}
    answer = re.sub('-', '', answer)
    answer = answer.lower()
    words = set(re.findall(r'\b\w+\b', answer))

    all_detected_directions = directions & words

    all_detected_directions = set([x[0].upper() + x[1:] for x in all_detected_directions])
    
    if len(all_detected_directions) == 0:
        return set()

    return all_detected_directions

def detect_bool(answer):
    if ("false" in answer.lower()) & ("true" in answer.lower()):
        raise ValueError("both true and false detected")
    
    if "false" in answer.lower():
        return {False}
    if "true" in answer.lower():
        return {True}

    return set()

def detect_cities(answer):
    """
    in case of an ambigous detection, give the LLM the benefit of the doubt
    unfortunately not possible to get hallucinated cities
    """
    
    answer = answer.lower()
    if "\n" in answer:
        tokens = set(answer.split("\n"))
    else:
        tokens = set(answer.split(","))
    tokens_clean = {re.sub(cleaning_regex, '', token).lower() for token in tokens}
    
    detected_cities = tokens_clean & all_cities_clean
    rest_of_tokens = tokens_clean - all_cities_clean

    cities_detected_via_altnames = set()

    # check for every clean token that is not a cleaned city already
    for token in rest_of_tokens:
        # if it is part of the keys of the all_altnames_dict_for_clean, if yes...
        if token in all_altnames_dict_for_clean:
            # get the uncleaned altname
            altname = all_altnames_dict_for_clean[token]
            # get the first one since in almost all cases it is the same city that is meant by it
            altname = altname[0]
            # send a SPARQL query to get the normal name
            get_normal_name = sparql_select(gt_correct_name_query.replace("ALTNAME", altname))
            normal_names = get_normal_name.name.tolist()
            cleaned_normal_names = [re.sub(cleaning_regex, '', n).lower() for n in normal_names]
            # clean the normal name
            
            if len(get_normal_name) == 0:
                raise ValueError()
            else:
                # insert the retrieved normal names into the detected set. Even if it is two names (we give the LLM the benefit of the doubt)
                cities_detected_via_altnames.update(set(cleaned_normal_names))
        
    return detected_cities, cities_detected_via_altnames

def get_answers_from_non_rag_response(row):
    type_str = row.answer_type
    
    if type_str == "code_iri":
        detected, existing, hallucinated = detect_codes(row)
        hallucination_rate_nuts = len(hallucinated) / len(detected) if len(detected) > 0 else 0

        detected = set(['http://data.europa.eu/nuts/code/'+code for code in detected])
        return [detected, hallucination_rate_nuts]
        
    if (type_str == "single_city") or (type_str == "cities"):
        detected_cities, cities_detected_via_altnames = detect_cities(row.non_rag_answers)
        detected_cities.update(cities_detected_via_altnames)
        return [detected_cities, None]

    if type_str == "direction":
        answers = detect_direction(row.non_rag_answers)
        return [answers, None]

    if type_str == "boolean":
        answers = detect_bool(row.non_rag_answers)
        return [answers, None]

    raise ValueError()  
    
def calculate_metrics_non_rag(row):
    type_str = row.answer_type
    
    gt_df = row.gt_results_from_graph_db
    gt_col = row.gt_results_column
    ground_truth = gt_df[gt_col]
    assert type(ground_truth) == pd.Series
    ground_truth = set(ground_truth)

    if (type_str == "single_city") or (type_str == "cities"):
        ground_truth = set([re.sub(cleaning_regex, '', city).lower() for city in ground_truth])

    if (type_str == "boolean"):
        # if there is True and False in the gt boolean answer, it is true since the city in question is almost surely the correct one
        if len(ground_truth) > 1:
            ground_truth = {True}

    results = row.detected_answers_non_rag
    if type(results) != set:
        raise ValueError()
    
    tp = len(ground_truth & results)
    fp = len(results - ground_truth)
    fn = len(ground_truth - results)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    if (type_str == "direction") & (len(ground_truth) > 0) & (len(results) > 0):
        results = list(results)
        ground_truth = list(ground_truth)
        if (((results[0] == "North") & (ground_truth[0] == "Northwest")) or ((results[0] == "North") & (ground_truth[0] == "Northeast"))) or \
            (((results[0] == "South") & (ground_truth[0] == "Southwest")) or ((results[0] == "South") & (ground_truth[0] == "Southeast"))):
                precision, recall, f1 = 0.5, 0.5, 0.5
            

    return [precision, recall, f1]



##### RAG FUNCTIONS #####

def calculate_metrics(row):
    
    gt_df = row.gt_results_from_graph_db
    gt_col = row.gt_results_column
    results = row.column_to_analyze
    ground_truth = gt_df[gt_col]
    assert type(ground_truth) == pd.Series
    assert type(results) == pd.Series

    ground_truth = set(ground_truth)
    results = set(results)

    if row.answer_type == "direction":
        ground_truth = {s.lower() for s in ground_truth}
        results = {re.sub(cleaning_regex, '', s).lower() for s in results}
        # print(ground_truth, results)


    # print(ground_truth, results)
    tp = len(ground_truth & results)
    fp = len(results - ground_truth)
    fn = len(ground_truth - results)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    if (row.answer_type == "direction") & (len(ground_truth) > 0) & (len(results) > 0):
        results = list(results)
        ground_truth = list(ground_truth)
        if (((results[0] == "North") & (ground_truth[0] == "Northwest")) or ((results[0] == "North") & (ground_truth[0] == "Northeast"))) or \
            (((results[0] == "South") & (ground_truth[0] == "Southwest")) or ((results[0] == "South") & (ground_truth[0] == "Southeast"))):
                precision, recall, f1 = 0.5, 0.5, 0.5

    return (precision, recall, f1)


directions = ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest", "unknown", "same", "within", "other"]
def assess_type(col):
    if col.dtype == 'bool':
        return "boolean"
    if (col.dtype == 'int64') or (col.dtype == 'float64'):
        return "number"
    if all(["http://data.europa.eu/nuts/code/" in elem for elem in col]):
        return "code_iri"
    if any(["http://data.europa.eu/nuts/code/" in elem for elem in col]):
        return "mixed"
    if all(["https://sws.geonames.org/" in elem for elem in col]):
        return "city_iri"

    col_list = col.tolist()
    col_set = set(col_list)

    intersection_nuts = all_nuts & col_set
    if len(intersection_nuts) == len(col_set): # all elements of the column are codes
        return "code"

    intersection_cities = all_cities & col_set
    if len(intersection_cities) == len(col_set): # all elements of the column are cities
        return "city"

    for elem in col:
        if any([direction in elem.lower() for direction in directions]):
            return "direction"

    if "wkt" in col.name.lower():
        return "wkt"

    for nutscode in all_nuts:
        if any([nutscode in elem for elem in col]):
            return "pref_label"

    if all(["http://" in elem for elem in col]):
        return "useless"
        
    raise ValueError("Column type unknown")
        
def get_answer_types_per_column(df):
    types = df.apply(assess_type)
    d = {}
    for column_name, type in zip(types.index, types.values):
        d[type] = column_name
    return d

def get_success_level(row, answer_type):
    gt = row.gt_results_from_graph_db
    answer = row.results_from_graph_db

    if type(answer) == str:
        if "QUERY_FAILED" in answer:
            return "query_failed"
        if "TIMEOUT" in answer:
            return "TIMEOUT"
        if answer == "NO_SPARQL_TO_TRY":
            return "no_sparql_to_try"
        else:
            return "python_error_from_sparql_select"
        
    if type(answer) == pd.DataFrame:
        
        if (len(answer) == 0) & (len(gt) == 0):
            return "both_empty"
            
        elif len(gt) == 0:
            return "gt_empty_answer_not"

        elif len(answer) == 0:
            return "empty_but_not_supposed_to_be"

        gt_answer_type, gt_column = answer_type[row.question_raw]
        gt_answer_type = "city" if (gt_answer_type == "cities") or (gt_answer_type == "single_city") else gt_answer_type
        types_in_generated_df = get_answer_types_per_column(answer)
        # print(gt_answer_type, types_in_generated_df)

        # the correct column type is found in the answer
        if gt_answer_type in types_in_generated_df:
            return "correct_answer_type_in_df", types_in_generated_df[gt_answer_type]
            
        # code instead of code_iri is ok
        if (gt_answer_type == "code_iri") & ("code" in types_in_generated_df):
            return "correct_answer_type_in_df_but_code", types_in_generated_df["code"]
            
        # code prefLabel instead of code_iri is ok
        if (gt_answer_type == "code_iri") & ("pref_label" in types_in_generated_df):
            return "correct_answer_type_in_df_but_pref_label", types_in_generated_df["pref_label"]
            
        # city iri instead of city is only kinda ok
        if (gt_answer_type == "city") & ("city_iri" in types_in_generated_df):
            return "generated_city_iri", types_in_generated_df["city_iri"]

        # mixed is not ok
        if "mixed" in types_in_generated_df:
            return "mixed_colum"

        return "no_correct_type"
    
    
    
def get_columns_for_results(df, relevant_col, success_level, idx):
    if success_level == "correct_answer_type_in_df":
        return df[relevant_col]
        
    if success_level == "correct_answer_type_in_df_but_code":
        col = df[relevant_col]
        col = col.apply(lambda x: "http://data.europa.eu/nuts/code/" + x)
        return col

    if success_level == "correct_answer_type_in_df_but_pref_label":
        col = df[relevant_col]
        col = col.apply(lambda x: "http://data.europa.eu/nuts/code/" + x.split(" ")[0])
        return col
    
def get_gt_column(row, answer_type):
    df = row["gt_results_from_graph_db"]
    direction = row.direction

    if row.intercardinal:
        direction = "DIRECTION"
    else:
        direction = direction[0].upper() + direction[1:].lower()

    col = answer_type[row.question_raw][1].format(direction)

    if type(df) == pd.DataFrame :
        return col
    else:
        print(col, row.name, df, direction)
        return "TO_DROP"
