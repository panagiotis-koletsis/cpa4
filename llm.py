from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from promptTemplates import PROMPT_TEMPLATE, PROMPT_TEMPLATE_STRUCTURING
from files import llm_csv
import numpy as np
import dateutil.parser
import re

#"qwen2.5:14b"   "qwen2.5:32b-instruct-q3_K_L"   qwen2.5:72b-instruct-q2_K        qwen3:14b
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


        #cta = gt['labelcol'][i]



        table = index[table_name]
        if len(table) > 500:
            table = table.iloc[:500]
        
        #print(table.to_json(orient="records"))
        

        #domains && types
        #rels = dom_types(table,domain,domains,num,types,rels)

        
        # co-appearance
        # if not first_iter:
        #     rels = get_coappearance(first_iter,used,coapperances,domain,rels)
        
        if len(rels) == 1:
            print("Only 1 relation")
            #res = rels

        table = table.to_json(orient="records")
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

        #print(f"Domain: {domain}, Num: {num}, Table: {table}, Relations: {rels}")

        #domain=domain,num=num,table=table,relations=rels

        #,cta=cta

        prompt = prompt_template.format(domain=domain,num=num,table=table,relations=rels)
        #print(prompt)
        llm = OllamaLLM(model=model)
        res = f"""{llm.invoke(prompt)}"""

        res = res.replace(" ", "")

        if res == 'addressStreet':
            res = 'streetAddress'

        if model == 'deepseek-r1:14b' or 'qwen3:14b':
            res = re.sub(r"<think>.*?</think>\s*", "", res, flags=re.DOTALL)
        
        #print(res)

        #This is for structuring
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
        
        #This is for co-App
        if first_name == table_name:
            first_iter = False
            if res in rels:
                used.append(res)
        else:
            first_name = table_name
            first_iter = True
            used.clear()
            

        #print("//////////////",res)
        
        llm_gt.loc[i, 'label'] = res
    llm_csv(llm_gt)




def dom_types(table,domain,domains,num,types,rels):
    #---Keep only this for domains only 
    # rels_dom = domains[domain]
    # return rels_dom
    #---

    # #print("-",rels_dom)

    #---Keep only this for types and domain
    rels_dom = domains[domain]
    type  = get_type(table,num)
    if type == 'int/float' or type == 'string' or type == 'date':
        rels_type = types[type]
        #print("---",rels_type)
        intersection = list(set(rels_dom).intersection(set(rels_type)))
        #print("++", intersection)
        #print("-",intersection)
        return intersection
    else: 
        #print("--",rels_dom)
        return rels_dom
    #---

    # #Keep only this for types only
    # type  = get_type(table,num)
    # if type == "None":
    #     return rels
    # rels_type = types[type]
    # #print(rels_type)
    # return rels_type
    # #---



def get_type(table,num):
    detected_type = "None"
    
    el = table[num][0]
    #print(el)
    #print(type(el))
    if isinstance(el, list):  # Correct way to check type
        #i added this for fixing error with list of lists
        #print(el[0])
        if isinstance(el[0], list):
            table.loc[0, num] = el[0][0]
        #print(element)
        else:
        #---
            table.loc[0,num] = table.loc[0,num][0]
  
        #table[num][0] = table[num][0][0]
        #print(table[num][0])
    element = table[num][0]
    if isinstance(element, (np.int64,np.float64)):  # Correct way to check type
        detected_type = "int/float"  
    elif isinstance(element, str):
        try:
            date = dateutil.parser.parse(element)  # Invalid date string
            detected_type = "date"
        except (ValueError, OverflowError) as e:
            detected_type = "string"
    #print(f"type {type}, element {element}")
    #print(detected_type)
    return detected_type



    # detected_type = "None"
    # number_type = 0
    # date_type = 0
    # string_type = 0

    # for i in range(3):
    #     value = table.loc[i, num]  # safer to read once

    #     # Handle list or nested list cases
    #     if isinstance(value, list):
    #         while isinstance(value, list):
    #             if len(value) == 0:
    #                 value = ""  # fallback for empty lists
    #                 break
    #             value = value[0]
    #         table.loc[i, num] = value  # overwrite cleaned value

    #     # Type detection
    #     if isinstance(value, (np.int64, np.float64, int, float)):
    #         number_type += 1
    #     elif isinstance(value, str):
    #         try:
    #             date = dateutil.parser.parse(value)
    #             date_type += 1
    #         except (ValueError, OverflowError):
    #             # if value.isdigit():
    #             #     number_type += 1
    #             # else:
    #             #     string_type += 1
    #             string_type += 1
                

    # # Decide majority type
    # if number_type > date_type and number_type > string_type:
    #     detected_type = "int/float"
    # elif date_type > number_type and date_type > string_type:
    #     detected_type = "date"
    # elif string_type > number_type and string_type > date_type:
    #     detected_type = 'string'

    # return detected_type


    # detected_type = "None"
    # number_type = 0
    # date_type = 0
    # string_type = 0
    # el = table[num]
    # for i in range(3):
    #     el = 
    #     if isinstance(el[i], list):  # Correct way to check type
    #     #i added this for fixing error with list of lists
    #     #print(el[0])
    #         if isinstance(el[i][0], list):
    #             table.loc[0, num] = table.loc[0, num][0]
    #     #print(element)
    #     else:
    #     #---
    #         table.loc[0,num] = table.loc[0,num][0]
    #     if isinstance(table[num][i], (np.int64,np.float64)):  # Correct way to check type
    #         number_type += 1
    #         #typesList[label].append('int/float')   
    #     elif isinstance(table[num][i], str):  # Correct way to check type     
    #         try:
    #             date = dateutil.parser.parse(table[num][i])  # Invalid date string
    #             date_type += 1
    #             #typesList[label].append('date')
    #         except (ValueError, OverflowError) as e:
    #             string_type += 1
    #             #typesList[label].append('string')
    
    # if number_type > date_type and number_type > string_type:
    #     detected_type = "int/float"
    # elif date_type > number_type and date_type > string_type:
    #     detected_type = "date"
    # elif string_type > number_type and string_type > date_type:
    #     detected_type = 'string'
    # return detected_type


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


