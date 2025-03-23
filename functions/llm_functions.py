# # -*- coding: utf-8 -*-
# """
# Created on Fri Jun  20 14:49:44 2024

# @author: simon-gross
# """
import os
import time
from openai import OpenAI

client = OpenAI(api_key = os.environ['OPENAI1'])
def run_client_openai(sysmsg, usermsg, model="", temperature=0, max_tokens=600, few_shotting=None):
    if model == "gpt-4o":
        time.sleep(7.5)
    else:
        time.sleep(0.12)
        
    if few_shotting is None:
        messages = [
            {"role": "system", "content": sysmsg},
            {"role": "user", "content": usermsg}
        ]
    else:
        messages = few_shotting
        
    completion = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        n=1,
        messages=messages
        )

    return completion.choices[0].message.content, completion.usage.prompt_tokens, completion.usage.completion_tokens
