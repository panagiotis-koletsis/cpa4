import pandas as pd
import json
import numpy as np
import dateutil.parser
from io import StringIO
from urllib.parse import urlparse


class Preprocess:

    #For R2 Dataset 
    DATASET_PATH = '/home/kpanag/Desktop/cpa3/cpa/R2/SOTAB-2023-R2-CPA/Round2-SOTAB-CPA-Tables/'
    GT_PATH = '/home/kpanag/Desktop/cpa3/cpa/R2/SOTAB-2023-R2-CPA/sotab_cpa_train_round2.csv'

    GT_PATH1 = '/home/kpanag/Desktop/cpa3/cpa/R2/SOTAB-2023-R2-CPA/sotab_cpa_train_round2.csv'
    GT_PATH2 = '/home/kpanag/Desktop/cpa3/cpa/R2/SOTAB-2023-R2-CPA/sotab_cpa_validation_round2.csv'


    # For R1 Dataset
    # GT_PATH1 = '/home/kpanag/Desktop/cpa3/cpa/Round1-SOTAB-CPA-Datasets/sotab_cpa_train_round1.csv'
    # GT_PATH2 = '/home/kpanag/Desktop/cpa3/cpa/Round1-SOTAB-CPA-Datasets/sotab_cpa_validation_round1.csv'

    # GT_PATH = '/home/kpanag/Desktop/cpa3/cpa/Round1-SOTAB-CPA-Datasets/sotab_cpa_train_round1.csv'
    # DATASET_PATH = '/home/kpanag/Desktop/cpa3/cpa/Round1-SOTAB-CPA-SCH-Tables/' 

    droptype_percent = 10


    def __init__(self):
        self.get_domains()
        print("Domains extraction completed")
        self.get_types()
        print("Types extraction completed")
        self.get_coappearance()
        print("Coappearance extraction completed")


    def get_types(self):
        df = pd.read_csv(self.GT_PATH)
        typesList = {name: [] for name in df['label'].unique()}
        for i in range(len(df)):
            label = df['label'][i]
            col = df['column_index'][i]
            table_name = df['table_name'][i]


            #read table 
            path = self.DATASET_PATH+table_name
            table_df = pd.read_json(path, compression='gzip', lines=True)
            if len(table_df) > 40:
                table_df = table_df.iloc[:40]
            for j in range(table_df.shape[1]):
                for k in range(len(table_df[j])):

                    #print(type(table_df[j][k]))
                    if isinstance(table_df[j][k], list):  # Correct way to check type
                        table_df.at[k, j] = table_df.at[k, j][0]
            
            # #3 elem type chacking
            # number_type = 0
            # date_type = 0
            # string_type = 0
            # img_type = 0
            # event_type = 0
            # url_type = 0
            # for i in range(3):
            #     if isinstance(table_df[col][i], (np.int64,np.float64)):  # Correct way to check type
            #         number_type += 1
            #         #typesList[label].append('int/float')   
            #     elif isinstance(table_df[col][i], str):  # Correct way to check type     
            #         try:
            #             date = dateutil.parser.parse(table_df[col][i])  # Invalid date string
            #             date_type += 1
            #             #typesList[label].append('date')
            #         except (ValueError, OverflowError) as e:
            #             #string_type += 1
            #             parsed = urlparse(table_df[col][i])
            #             is_url = all([parsed.scheme, parsed.netloc])
            #             if ".img" in table_df[col][i] and not(is_url):
            #                 img_type += 1
            #             if is_url:
            #                 if "https://schema.org/" in table_df[col][i]:
            #                     event_type += 1 
            #                 elif ".img" in table_df[col][i]:
            #                     img_type += 1
            #                 else:
            #                     url_type += 1
            #             if ".img" not in table_df[col][i] and not(is_url):
            #                 string_type += 1
                         

            #             # if table_df[col][i].isdigit():
            #             #     number_type += 1
            #             # else:
            #             #     string_type += 1
            #             #typesList[label].append('string')

            # type_counts = {
            #     'int/float': number_type,
            #     'date': date_type,
            #     'string': string_type,
            #     'image': img_type,
            #     'url': url_type,
            #     'event': event_type
            # }

            # # Get the dominant type (with max occurrences)
            # dominant_type = max(type_counts, key=type_counts.get)
            # typesList[label].append(dominant_type)
            
            # if number_type > date_type and number_type > string_type:
            #     typesList[label].append('int/float')
            # elif date_type > number_type and date_type > string_type:
            #     typesList[label].append('date')
            # elif string_type > number_type and string_type > date_type:
            #     typesList[label].append('string')

            
            # print("number_type",number_type)
            # print("date_type",date_type)
            # print("string_type",string_type)
            #end 3 elem type checking


            #here we take the 1st element
            #print(type(table_df[j][k]))
            if isinstance(table_df[col][0], (np.int64,np.float64)):  # Correct way to check type
                typesList[label].append('int/float')   
            elif isinstance(table_df[col][0], str):  # Correct way to check type     
                try:
                    date = dateutil.parser.parse(table_df[col][0])  # Invalid date string
                    #print(table_df[col][0])
                    typesList[label].append('date')
                except (ValueError, OverflowError) as e:
                    typesList[label].append('string')
            #end 1st elem


        # for key in typesList:
        #     typesList[key] = list(set(typesList[key]))


        #this is for type clearing
        for key in typesList:
            typesList[key] = {t: typesList[key].count(t) for t in set(typesList[key])}
        #print(typesList)


        
        for key, value in typesList.items():
            #print(value)
            for sub_key,sub_value in value.items():
                max_value = max(value.values(), default=-1)
                # max = -1
                # if sub_value > max:
                #     max = sub_value
            #print("-",max_value)
            threshold = self.droptype_percent/100*max_value
            #print(threshold)
            keys_to_remove = []
            for sub_key,sub_value in value.items():
                if sub_value < threshold:
                    keys_to_remove.append(sub_key)
            for sub_key in keys_to_remove:
                value.pop(sub_key, None)
                #print("------",value)

        #print(typesList)

                


        
        
        #print()

        

        inverted_data = {}

        for key, value_list in typesList.items():
            for value in value_list:
                if value not in inverted_data:
                    inverted_data[value] = []
                inverted_data[value].append(key)

        #This is for type clearing
        # for key, value_dict in typesList.items():
        #     for value, count in value_dict.items():
        #         if value not in inverted_data:
        #             inverted_data[value] = []
        #         inverted_data[value].append({key: count})
        # print(inverted_data)

        
        # saving

        file_path = 'data/dict1.json'
        with open(file_path, 'w') as f:
            json.dump(inverted_data, f, indent=4)



    def get_domains(self):
        df1 = pd.read_csv(self.GT_PATH1)
        df2 = pd.read_csv(self.GT_PATH2)

        names = self.get_initial_list(df1)
        self.dict = {name: [] for name in names}

        for i in range(len(df1)):
            self.dict[df1['table_name'][i].split('_')[0]].append(df1['label'][i])

        for i in range(len(df2)):
            self.dict[df2['table_name'][i].split('_')[0]].append(df2['label'][i])

        for key in self.dict:
            self.dict[key] = list(set(self.dict[key]))

        self.write_to_file()



    def get_coappearance(self):
        df = pd.read_csv(self.GT_PATH1)
        with open('data/dict.json', 'r') as file:
            data = json.load(file)
        data = {key: {item: [] for item in value} for key, value in data.items()}

        grouped = df.groupby('table_name')
        for table_name, group in grouped:
            type = table_name.split('_')[0]
            labels = group["label"].tolist()
            for i in range(len(labels)):
                label = labels[i]
                new_labels = labels[:i] + labels[i+1:]
                for j in range(len(new_labels)):
                    data[type][label].append(new_labels[j])
        
        cleaned_data = self.remove_duplicates_from_dict(data)

        file_path = 'data/coappearance.json'
        with open(file_path, 'w') as f:
            json.dump(cleaned_data, f, indent=4)


    def remove_duplicates_from_dict(self, data):
        for category, attributes in data.items():
            for attribute, values in attributes.items():
                # Remove duplicates while preserving order
                data[category][attribute] = list(dict.fromkeys(values))
        return data
    

    def get_initial_list(self, df1):
        nameList = []
        for i in range(len(df1)):
            name = df1['table_name'][i].split('_')[0]
            nameList.append(name)
        nameList = list(set(nameList))    
        return nameList
    
    def write_to_file(self):
        file_path = 'data/dict.json'
        with open(file_path, 'w') as f:
            json.dump(self.dict, f, indent=4)



def main():
    Preprocess()


if __name__ == "__main__":
    main()