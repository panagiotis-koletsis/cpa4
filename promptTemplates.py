PROMPT_TEMPLATE = """
    ----
    Knowing that this table is about {domain}
    ----
    {table}
    ----
    On the provided table i want you to answer this question: 
    What is the relation between column 0 and column {num}
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