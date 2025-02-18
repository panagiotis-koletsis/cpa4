from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from promptTemplates import PROMPT_TEMPLATE, PROMPT_TEMPLATE_STRUCTURING
from files import llm_csv
import numpy as np
import dateutil.parser
import re

#"qwen2.5:14b"
model = "qwen2.5:14b"
def llm(index, gt, domains, types, rels):



    for i in range(len(gt)):
        print(i)
        #print(index)
        table_name = gt['table_name'][i]
        domain = table_name.split('_')[0]
        #print(type(domain))
        num =  gt['column_index'][i]
        #print(num)
        # print(domain)
        # print(table_name)
        # print(index[table_name])
        table = index[table_name]
        if len(table) > 500:
            table = table.iloc[:500]
        
        #print(table.to_json(orient="records"))
        

        #domains && types
        rels = dom_types(table,domain,domains,num,types)

        table = table.to_json(orient="records")
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

        #print(f"Domain: {domain}, Num: {num}, Table: {table}, Relations: {rels}")

        #domain=domain,num=num,table=table,relations=rels
        prompt = prompt_template.format(domain=domain,num=num,table=table,relations=rels)
        #print(prompt)
        llm = OllamaLLM(model=model)
        res = f"""{llm.invoke(prompt)}"""

        if model == 'deepseek-r1:14b':
            res = re.sub(r"<think>.*?</think>\s*", "", res, flags=re.DOTALL)

        tr = 0
        while (res not in rels) and tr < 2:
            #print(res)
            #print('----trying again')
            res = llm_structuring(res)
            if res not in rels:
                llm = OllamaLLM(model=model)
                res = f"""{llm.invoke(prompt)}"""
            tr +=1
        if res not in rels:
            print("---res out", res)
            

        #print(res)
        llm_gt = gt 
        llm_gt.loc[i, 'label'] = res
    llm_csv(llm_gt)




def dom_types(table,domain,domains,num,types):
    rels_dom = domains[domain]
    #print("-",rels_dom)
    type  = get_type(table,num)
    if type == 'int/float' or type == 'string' or type == 'date':
        rels_type = types[type]
        #print("---",rels_type)
        intersection = list(set(rels_dom).intersection(set(rels_type)))
        #print("++", intersection)
        return intersection
    else: 
        return rels_dom



def get_type(table,num):
    type = "None"
    
    if isinstance(table[num][0], list):  # Correct way to check type
        #print(element)
        table.loc[0,num] = table.loc[0,num][0]
        #table[num][0] = table[num][0][0]
        #print(table[num][0])
    element = table[num][0]
    if isinstance(element, (np.int64,np.float64)):  # Correct way to check type
        type = "int/float"  
    elif isinstance(element, str):
        try:
            date = dateutil.parser.parse(element)  # Invalid date string
            type = "date"
        except (ValueError, OverflowError) as e:
            type = "string"
    #print(f"type {type}, element {element}")
    return type

model_structuring = 'qwen2:7b'
def llm_structuring(res):
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE_STRUCTURING)

    prompt = prompt_template.format(res=res)
    #print(prompt)
    llm = OllamaLLM(model=model_structuring)
    res = f"""{llm.invoke(prompt)}"""
    #print("+",res)
    return res


