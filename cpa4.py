from files import read_datasets, read_gt, relations_domain, relations_types , llm_csv, relations_file, eval, relations_coappearance
from llm import llm
from evaluator import SOTAB_Evaluator
import time


def main():
    start_time = time.time()
    dataframes, fn = read_datasets()
    # print(dataframes)
    # print(fn)
    gt = read_gt()
    # print(gt)
    # print(len(dataframes), len(fn))
    # print(len(gt))
    domains = relations_domain()
    types = relations_types()
    coapperance = relations_coappearance()
    # print(len(domains))
    # print(len(types))

    llm_csv(gt)

    index = dict(zip(fn, dataframes))


    rels = relations_file()
    llm(index, gt, domains, types, coapperance ,rels)

    eval()

    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")

    



    

    

    















if __name__ == "__main__":
    main()
