import os
from openai import OpenAI
from functions.sparql_requests import sparql_select, sparql_update

def raw_api(client, sysmsg_raw, usermsg, few_shot=True):
    print("Sending raw API call...")
    
    messages = [
        {"role": "system", "content": sysmsg_raw},
        {"role": "user", "content": usermsg},
            ]
    
    if few_shot:
        messages = [
            {"role": "system", "content": sysmsg_raw},
            
            {"role": "user", "content": "Give me all nuts regions that share a border with the region DE71 and have the same nuts level"},
            {"role": "assistant", "content": "['DE26', 'DEB1', 'DEB3', 'DE12', 'DE72', 'DE73']"},
            
            {"role": "user", "content": "Give me all nuts regions that share a border with the region PT16 and have the same nuts level"},
            {"role": "assistant", "content": "['PT17', 'PT18', 'ES41', 'ES43', 'PT11']"},
            
            {"role": "user", "content": "Give me all nuts regions that share a border with the region HR02 and have the same nuts level"},
            {"role": "assistant", "content": "['SI03', 'HU23', 'HR03', 'HR06', 'HU33']"},
            
            {"role": "user", "content": "This was very good! Please continue like this!"},
            {"role": "assistant", "content": "You're welcome! If you have any more questions, feel free to ask"},
            
            {"role": "user", "content": usermsg}
                ]
        
    completion_raw = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=messages,
        max_tokens=500

    )
    
    answer_raw = completion_raw.choices[0].message.content
    used_tokens = completion_raw.usage.total_tokens
    
    return answer_raw, used_tokens
    
def compare_answers_neighbors(nutscode, skip_parsing=True):
    print("Setting up client...")
    client = OpenAI(api_key = os.environ['OPENAI1'])
    used_tokens = 0
    
    usermsg = f"Give me all nuts regions that share a border with the region {nutscode} and have the same nuts level"

    ####
    sysmsg_raw = "You are a helpful AI assistant that answers questions about european NUTS regions. Give only the relevant information."
    answer_raw, tokens = raw_api(client, sysmsg_raw, usermsg)
    used_tokens += tokens
    
    ####
    if not skip_parsing:
        print("Sending parsing API call...")
        sysmsg_parsing = "You are a parsing engine. The user will ask a question about NUTS regions. Ignore the question and only return the NUTS code from the users question, nothing else."
        
        completion_parsing = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[
                {"role": "system", "content": sysmsg_parsing},
                {"role": "user", "content": usermsg}
            ]
        )
    
        parsed = completion_parsing.choices[0].message.content
        used_tokens += completion_parsing.usage.total_tokens
    else:
        print("Parsing skipping is enabled")
        parsed = nutscode
    
    
    
    ####
    print("Getting neighbors from GraphDB")
    with open("sparql/get_all_neighborhoods_same_level.sparql", "r") as f:
        query_allNeighborhoodsSameLevel = f.read()
        
    query_allNeighborhoodsSameLevel = query_allNeighborhoodsSameLevel.replace("PLACEHOLDER", parsed)
    df = sparql_select(query_allNeighborhoodsSameLevel)
    
    answer = ""
    for elem in df[df.columns[0]].values.tolist():
        answer += elem
        answer += "\n"
    answer = answer[:-1]
    
    
    
    ####
    print("Sending RAG API call...")
    sysmsg_rag = "You are a helpful assistant that answers a users questions about the european NUTS regions based only on the provided context. If you do not know the answer just say that you dont know it. Do not make anything up. Only give the NUTS codes in your answer. Format your answer as a python list."
    usermsg_rag = f"""The user asked the following question:
    
    {usermsg}
    
    This is the answer retrieved from a Graph-database:
    {answer}
    
    """
    
    completion_rag = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {"role": "system", "content": sysmsg_rag},
            {"role": "user", "content": usermsg_rag}
        ]
    )
    
    answer_rag = completion_rag.choices[0].message.content
    used_tokens += completion_rag.usage.total_tokens
    
    print(f"Total tokens used: {used_tokens}")
    
    return answer_raw, answer_rag
