import argparse
import pandas as pd
from sklearn.metrics import f1_score, precision_recall_fscore_support
import random

class SOTAB_Evaluator:
    
    def __init__(self, ground_truth_filepath, submission_filepath):
        """
        ground_truth_filepath: filepath where csv with ground truth is located.
        submission_filepath: filepath where csv with submission is located.
        """
        self.ground_truth_filepath = ground_truth_filepath
        self.submission_filepath = submission_filepath

    def _evaluate(self):
        """
        Compare submitted annotations with ground truth annotations,
        and calculate precision, recall and macro-f1 and micro-f1 metrics.
        """

        gt = pd.read_csv(self.ground_truth_filepath)

        #sort approprietely 
        gt['table_name'] = pd.Categorical(gt['table_name'], categories=gt['table_name'].unique(), ordered=True)
        gt_sorted = gt.sort_values(by=['table_name', 'column_index'])
        gt = gt_sorted

        gt_labels = gt['label'].tolist()

        submission = pd.read_csv(self.submission_filepath)
        
        cta_labels = list(gt['label'].unique())

        # Number of predictions should equal the number of columns in the ground truth
        if len(submission) != len(gt):
            raise Exception("Some predictions are missing.")

        predictions = []

        sum=0
        for i in range(len(submission)):
            if submission.loc[i, 'label'] not in cta_labels:
                print(submission.loc[i, 'label'])
                #submission.loc[i, 'label'] = random.choice(cta_labels)
                sum += 1
        print("+++",sum)

        for index, row in submission.iterrows():
            # # Prediction should be a label from the "sotab-cta-labels.txt" set.
            # if row['label'] not in cta_labels:
            #     raise Exception("Label out of label space used.")
            # else:
            predictions.append(row['label'])


        precision, recall, f1, _ = precision_recall_fscore_support(gt_labels, predictions, average='macro')
        micro_f1 = f1_score(gt_labels, predictions, average='micro')
        results = {
            'macro_f1': f1,
            'micro_f1': micro_f1,
            'precision': precision,
            'recall': recall
        }

        """
        Do something with your submitted file to come up
        with a score and a secondary score.

        if you want to report back an error to the user,
        then you can simply do :
          `raise Exception("YOUR-CUSTOM-ERROR")`

         You are encouraged to add as many validations as possible
         to provide meaningful feedback to your users
        """
        return results


# if __name__ == "__main__":

#     ground_truth_filepath = ""  # Replace with actual path
#     submission_filepath = ""      # Replace with actual path

#     # ground_truth_filepath = "/home/kpanag/Desktop/cpa-final/random.csv"  # Replace with actual path
#     # submission_filepath = "/home/kpanag/vscode/cpa2/data/llm.csv"      # Replace with actual path

#     # ground_truth_filepath = "/home/kpanag/vscode/cpa2/t1.csv"  # Replace with actual path
#     # submission_filepath = "/home/kpanag/vscode/cpa2/t2.csv"      # Replace with actual path

#     # parser = argparse.ArgumentParser(description='Evaluate submission against groundtruth.')
#     # parser.add_argument(
#     #     'submission_filepath',
#     #     type=str,
#     #     help='path of the submission file'
#     # )
#     # parser.add_argument(
#     #     'ground_truth_filepath',
#     #     type=str,
#     #     help='path of the ground truth file'
#     # )

#     # args = parser.parse_args()
    
#     # Instantiate an evaluator
#     #evaluator = SOTAB_Evaluator(args.ground_truth_filepath, args.submission_filepath)
#     evaluator = SOTAB_Evaluator(ground_truth_filepath, submission_filepath)
#     # Evaluate
#     result = evaluator._evaluate()
#     print(result)
