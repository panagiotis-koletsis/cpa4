from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from promptTemplates import PROMPT_TEMPLATE, PROMPT_TEMPLATE_STRUCTURING
from files import llm_csv
import numpy as np
import dateutil.parser
import re
from urllib.parse import urlparse
from files import desc_file

#"qwen2.5:14b"   "qwen2.5:32b-instruct-q3_K_L"   qwen2.5:72b-instruct-q2_K        qwen3:14b
model = "qwen2.5:32b-instruct-q3_K_L"
def llm(index, gt, domains, types, coapperances , rels):
    llm_gt = gt 
    used = []
    first_name = gt['table_name'][0]
    first_iter = True
    #for r2
    #first_rels_to_coapp = ["isbn", "genre", "email", "review", "itemCondition", "currenciesAccepted", "amenityFeature", "datePosted", "director", "contentRating", "countryOfOrigin", "numTracks", "nationality", "color", "releaseDate", "recipeIngredient", "recipeInstructions", "cookingMethod", "servesCuisine"]
    #first_rels_to_coapp = ["inLanguage", "availability", "isbn", "bookFormat", "numberOfPages", "copyrightYear", "review", "image", "email", "priceRange", "addressCountry", "postalCode", "currenciesAccepted", "paymentAccepted", "amenityFeature", "availableLanguage", "faxNumber", "dayOfWeek", "contentRating", "countryOfOrigin", "numTracks", "nationality", "birthPlace", "honorificSuffix", "gender", "measurements", "color", "releaseDate", "recipeInstructions", "cookingMethod", "servesCuisine"]
    
    #for r1
    first_rels_to_coapp = ["image", "numberOfPages", "inLanguage", "author", "publisher", "genre", "endDate", "email", "priceRange", "streetAddress", "faxNumber", "contentRating", "byArtist", "inAlbum", "gender", "releaseDate"]
    first_rel = ""



    for i in range(len(gt)):
        print(i)
        table_name = gt['table_name'][i]
        domain = table_name.split('_')[0]
        num =  gt['column_index'][i]

        table = index[table_name]
        if len(table) > 500:
            table = table.iloc[:500]

        #domains && types
        rels = dom_types(table,domain,domains,num,types,rels)

        # #add description part
        # desc_dict = desc_file()
        # filtered_descriptions = {key: desc_dict[key] for key in rels if key in desc_dict}
        #end add descr

        
        # co-appearance
        # if not first_iter:
        #     if first_rel in first_rels_to_coapp:
        #         rels = get_coappearance(first_iter,used,coapperances,domain,rels,first_rel)
        
        if len(rels) == 1:
            print("Only 1 relation")
            #res = rels

        table = table.to_json(orient="records")
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

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
        while (res not in rels) and tr < 2 :
            #print(res)
            #print('----trying again')
            res = llm_structuring(res)
            if res not in rels:
                llm = OllamaLLM(model=model)
                res = f"""{llm.invoke(prompt)}"""
            tr +=1
        if res not in rels:
            print("---res out", res)

        if first_iter == True:
            first_rel = res
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
    if type == 'int/float' or type == 'string' or type == 'date' :
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
    if isinstance(el, list):  
        if isinstance(el[0], list):
            table.loc[0, num] = el[0][0]
        #print(element)
        else:
            table.loc[0,num] = table.loc[0,num][0]
    element = table[num][0]
    if isinstance(element, (np.int64,np.float64)):  # Correct way to check type
        detected_type = "int/float"  
    elif isinstance(element, str):
        try:
            date = dateutil.parser.parse(element)  # Invalid date string
            detected_type = "date"
        except (ValueError, OverflowError) as e:
            if element.isdigit():
                detected_type ="int/float"
            else:    
                parsed = urlparse(element)
                is_url = all([parsed.scheme, parsed.netloc])
                if is_url:
                    if "https://schema.org/" in element:
                        detected_type ="url_has_schema"
                    else:
                        detected_type ="url"
                else:              
                    detected_type = "string"
    return detected_type



def get_coappearance(first_iter,used,coapperances,domain,rels,first_rel):
    #remove already chooses relations
    new_rels = [item for item in rels if item not in used]
    rels = new_rels

    #coappearance 
    if len(used) != 0: 
        #first_item =  used[0]
        first_item = first_rel
        try:
            coapp = coapperances[domain][first_item]
        except KeyError:
            coapp = rels

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






# this is for get_type it was tested a majority vote based on the 3 first cells but decreased performance...
# detected_type = "none"
# none_type = 0
# int_type = 0
# float_type = 0
# date_type = 0
# string_type = 0
# event_type = 0
# url_type = 0

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

#     if value is None:  # Correct way to check type
#         none_type += 1
#     # Type detection
#     if isinstance(value, (np.int64)):
#         int_type += 1
#     elif isinstance(value, (np.float64)):
#         float_type += 1
#     elif isinstance(value, str):
#         try:
#             date = dateutil.parser.parse(value)
#             date_type += 1
#         except (ValueError, OverflowError):
#             try:
#                 parsed = urlparse(value.strip())
#                 is_url = all([parsed.scheme, parsed.netloc])
#             except (ValueError, OverflowError):
#                 is_url = False

#             if is_url:
#                 if "https://schema.org/" in value:
#                     event_type += 1
#                 else:
#                     url_type += 1
#             else:
#                 string_type += 1

# type_counts = {
#             'none': none_type,
#             'int': int_type,
#             'float': float_type,
#             'date': date_type,
#             'string': string_type,
#             'url': url_type,
#             'url_has_schema': event_type
#         }

# detected_type = max(type_counts, key=type_counts.get)
# #print(detected_type)

# return detected_type