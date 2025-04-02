import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM







class CTA:

    DATASET_PATH = '/home/kpanag/Desktop/cpa3/cpa/Round1-SOTAB-CPA-SCH-Tables/'  
    GT_PATH = '/home/kpanag/Desktop/cpa3/cpa/Round1-SOTAB-CPA-Datasets/random.csv'
    LABELS = "/home/kpanag/Desktop/cpa3/cta/Round1-SOTAB-CTA-Datasets/cta_labels_round1.txt"
    #"qwen2.5:32b-instruct-q3_K_L"
    model = "qwen2.5:14b"

    PROMPT_CTA = """
    ----
    Knowing that this table is about {domain}
    ----
    {table}
    ----
    On the provided table i want you to answer this question: 
    What is the label of column {num}
    ----
    ***All the possible relations are in this list {relations}.
    Provide only the desired output (1 word) and nothing more! Dont explain yourself and dont provide extra comments! 
    """ 

    def __init__(self):
        
        self.cta()
        print("cta extraction completed")


    
    def cta(self):
        # Read CSV file
        gt = pd.read_csv(self.GT_PATH)
        gt["labelcol"] = "DefaultValue"

        # Open and read the text file
        with open(self.LABELS, "r") as file:
            labels = file.read().splitlines()  # Read lines and remove newline characters
        dataframes, fn = self.read_datasets()
        index = dict(zip(fn, dataframes))
        #len(index)
        cta_gt = gt 

        for i in range(len(gt)): 
            print(i)   
            table_name = gt['table_name'][i]
            domain = table_name.split('_')[0]
            num =  gt['column_index'][i]
            table = index[table_name]
            table = table.to_json(orient="records")
            prompt_template = ChatPromptTemplate.from_template(self.PROMPT_CTA)
            prompt = prompt_template.format(domain=domain,num=num,table=table,relations=labels)
            #print(prompt)
            llm = OllamaLLM(model=self.model)
            res = f"""{llm.invoke(prompt)}"""
            #print(res)
            cta_gt.loc[i, 'labelcol'] = res

            res = res.replace(" ", "")
        
        self.llm_csv(cta_gt)


    def llm_csv(self, gt):
        # Specify the file name
        filename = 'data/llm1.csv'
        # Writing to a CSV file
        #gt['label'] = 'test'
        
        #print(gt)
        #need to change the llm output
        gt.to_csv(filename, index=False)



    def read_datasets(self):
        gt = self.read_gt()
        # Get distinct table_name values
        distinct_values = gt['table_name'].unique()
        #print(distinct_values)
        
        # Folder path where the files are stored
        folder_path = self.DATASET_PATH
        
        df = []

        # Loop over the distinct values and try to read the corresponding files
        for table_name in distinct_values:
            path = folder_path+table_name
            table_df = pd.read_json(path, compression='gzip', lines=True)
            df.append(table_df)
        #len(df)
        return df, distinct_values

    def read_gt(self):
        file_path = self.GT_PATH
        gt = pd.read_csv(file_path)

        #sort approprietely 
        gt['table_name'] = pd.Categorical(gt['table_name'], categories=gt['table_name'].unique(), ordered=True)
        gt_sorted = gt.sort_values(by=['table_name', 'column_index'])
        gt = gt_sorted
        #print(gt)

        return gt




def main():
    CTA()


if __name__ == "__main__":
    main()