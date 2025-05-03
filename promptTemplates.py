# knowing that the col {num} has type {cta}
#    You are an expert in table interpretation, specialized in relations identification among columns.
PROMPT_TEMPLATE = """
    ----
    Knowing that this table is about {domain}
    ----
    {table}
    ----
    On the provided table i want you to answer this question: 
    What is the relation between column 0 and column {num}. 
    ----
    ***All the possible relations are in this list {relations}.
    Examine all the possible provided relations and keep the most suitable one!
    Be carefull to only use the list of relations!
    ----
    Example 
    -------
    Knowing that this table is about Book
    ----
    On the table below i want you to answer this queastion: 
    What is the relation between col 0 and col 1
    |0|1|2|3|4|
    |Schaum's Outline of Operating Systems (Schaum's Outline Series)|McGraw-Hill Education|20,39|EUR|9780071364355|
    |Le petit bonhomme de pain d'épices. Niveau 1 (Facile à lire)|Black Cat-Cideb|6,80|EUR|9788853010858|


    Desired output
    publisher 
    -------
    Think step by step 
    1. Locate the 2 columns 
    2. Extract context from the other columns
    3. Identify the most suitable relation from the relation list

    

    Provide only the desired output (1 word) and nothing more! Dont explain yourself and dont provide extra comments!
    ----

"""

PROMPT_TEMPLATE_STRUCTURING = """
    From the following responce i need you to isolate the relation mentioned and provide only that.
    {res}
    The desired output is only a word 
"""

# This for R2
#|0|1|2|3|4|5|6|7|8|
#|"[AZW] \u2713 Free Read \u2606 Ladybugs : by Margaret C. Hall \u21a0"|"Margaret C. Hall"|"Hardcover"|"2020-06-06T05:50:45+00:00"|"9780736825894"|116|"English"|4.9|
#|"BEST PDF \\\"\u00c1 Un tram che si chiama desiderio\\\"|"Tennessee Williams"|"Paperback"|"2020-06-12T14:26:09+00:00"|"8806382403"|431|"English"|4.5|

# This is for R1 
#|0|1|2|3|4|
#|Schaum's Outline of Operating Systems (Schaum's Outline Series)|McGraw-Hill Education|20,39|EUR|9780071364355|
#|Le petit bonhomme de pain d'épices. Niveau 1 (Facile à lire)|Black Cat-Cideb|6,80|EUR|9788853010858|



#    1. Locate the 2 columns 
#    2. Extract context from the other columns
#    3. Identify the most suitable relation from the relation list