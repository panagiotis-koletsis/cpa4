from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from promptTemplates import PROMPT_TEMPLATE, PROMPT_TEMPLATE_STRUCTURING
from files import llm_csv
import numpy as np
import dateutil.parser
import re

#"qwen2.5:14b"   "qwen2.5:32b-instruct-q3_K_L"
model = "qwen2.5:32b-instruct-q3_K_L"
def llm(index, gt, domains, types, coapperances , rels):
    llm_gt = gt 
    used = []
    first_name = gt['table_name'][0]
    first_iter = True



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
        #initial_rels = rels
        # if not first_iter:
        #     rels = get_coappearance(first_iter,used,coapperances,domain,rels)
        
        if len(rels) == 1:
            print("Only 1 relation")

        table = table.to_json(orient="records")
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

        #print(f"Domain: {domain}, Num: {num}, Table: {table}, Relations: {rels}")

        #domain=domain,num=num,table=table,relations=rels
        prompt = prompt_template.format(domain=domain,num=num,table=table,relations=rels)
        #print(prompt)
        llm = OllamaLLM(model=model)
        res = f"""{llm.invoke(prompt)}"""

        res = res.replace(" ", "")

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
        
        if first_name == table_name:
            first_iter = False
            if res in rels:
                used.append(res)
        else:
            first_name = table_name
            first_iter = True
            used.clear()
            

        #print(res)
        
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


def get_coappearance(first_iter,used,coapperances,domain,rels):
    #remove already chooses relations
    # print("-rels",rels)
    # print("--used",used)
    new_rels = [item for item in rels if item not in used]
    #print("---newrels",new_rels)
    rels = new_rels

    #coappearance 
    if len(used) != 0: 
        first_item =  used[0]
        try:
            coapp = coapperances[domain][first_item]
        except KeyError:
            coapp = rels
        # print("-coapp",coapp)
        # print("--rels",rels)

        intersection = list(set(rels).intersection(set(coapp)))

        # print("---intersection",intersection)
        rels = intersection
    return rels




model_structuring = 'qwen2:7b'
def llm_structuring(res):
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE_STRUCTURING)

    prompt = prompt_template.format(res=res)
    #print(prompt)
    llm = OllamaLLM(model=model_structuring)
    res = f"""{llm.invoke(prompt)}"""
    #print("+",res)
    return res


