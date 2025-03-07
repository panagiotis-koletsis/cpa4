import pandas as pd
import os
import csv
import json
#from eval import process
from evaluator import SOTAB_Evaluator
#from eval import calculate_metrics


#These needs to be changed
DATASET_PATH = '/home/kpanag/Desktop/cpa3/cpa/Round1-SOTAB-CPA-SCH-Tables/'  
GT_PATH = '/home/kpanag/Desktop/cpa3/cpa/Round1-SOTAB-CPA-Datasets/sotab_cpa_validation_round1.csv'
RELATIONS_FILE = '/home/kpanag/Desktop/cpa3/cpa/Round1-SOTAB-CPA-Datasets/cpa_labels_round1.txt'
#GT_PATH = '/home/kpanag/Desktop/cpa3/cpa/Round1-SOTAB-CPA-Datasets/random.csv'
#GT_PATH = '/home/kpanag/Desktop/cpa3/cpa/Round1-SOTAB-CPA-Datasets/sotab_cpa_test_round1.csv'



def read_datasets():
    gt = read_gt()
    # Get distinct table_name values
    distinct_values = gt['table_name'].unique()
    #print(distinct_values)
    
    # Folder path where the files are stored
    folder_path = DATASET_PATH
    
    df = []

    # Loop over the distinct values and try to read the corresponding files
    for table_name in distinct_values:
        path = folder_path+table_name
        table_df = pd.read_json(path, compression='gzip', lines=True)
        df.append(table_df)
    #len(df)
    return df, distinct_values

def read_gt():
    file_path = GT_PATH
    gt = pd.read_csv(file_path)

    #sort approprietely 
    gt['table_name'] = pd.Categorical(gt['table_name'], categories=gt['table_name'].unique(), ordered=True)
    gt_sorted = gt.sort_values(by=['table_name', 'column_index'])
    gt = gt_sorted

    return gt

def relations_domain():
    # Open and load JSON from a file
    with open("data/dict.json", "r") as file:
        data = json.load(file)  # Use json.load() for file

    # Print the loaded data
    return data

def relations_types():
    # Open and load JSON from a file
    with open("data/dict1.json", "r") as file:
        data = json.load(file)  # Use json.load() for file

    # Print the loaded data
    return data

def relations_coappearance():
    with open("data/coappearance.json", "r") as file:
        data = json.load(file)  # Use json.load() for file
    return data

def llm_csv(gt):
    # Specify the file name
    filename = 'data/llm.csv'
    # Writing to a CSV file
    #gt['label'] = 'test'
    
    #print(gt)
    #need to change the llm output
    gt.to_csv(filename, index=False)
    



def relations_file():
    # Initialize an empty list to store all the values
    attributes_list = []

# Open the CSV file
    with open(RELATIONS_FILE, mode='r') as file:
        reader = csv.reader(file)
    
        # Iterate over each row in the CSV file
        for row in reader:
            # Each row contains a single attribute inside a list, so we append it to the attributes list
            attributes_list.extend(row)
    return attributes_list


def eval():
    ground_truth_filepath =  GT_PATH
    submission_filepath = 'data/llm.csv'

    evaluator = SOTAB_Evaluator(ground_truth_filepath, submission_filepath)
    result = evaluator._evaluate()
    
    print(result)