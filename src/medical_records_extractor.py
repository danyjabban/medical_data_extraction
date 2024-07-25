import typing
from data_ingester import ingest_info
from data_extracter import data_extractor
from post_processer import post_processor

import numpy as np
import pickle
import json
from typing import Optional


def medical_records_extractor(file:str, queries:list[tuple], embedding_path:Optional[str]=None, page_info_dict_path:Optional[str]=None):
    """
    main function, calls data ingestion process, data extraction process, and data cleaning post process
    to answers queries from given pdf
    ------
    Args:
        file (str): path of pdf file
        queries (list[list]): each inner list contains the query and the associated terms 
        with that query, [query:str, query_key_words:str]

    """
    # if data already exisits pull from database
    if embedding_path and page_info_dict_path:
        embedding_matrix = np.load(embedding_path)
        with open(page_info_dict_path, 'rb') as handle:
            page_info_dict = pickle.load(handle)
    # otherwise construct data
    else: 
        embedding_matrix, page_info_dict = ingest_info(file)
        
    answers = data_extractor(embedding_matrix, page_info_dict, queries, file)

    # store answers dictionary midpoint
    with open('result.json', 'w') as fp:
        json.dump(answers, fp)
    
    # clean up data and save to file
    post_processor(answers)




if __name__ == "__main__":
    file = "../../SampleHealthRecord_Redacted.pdf"

    queries = \
    [
        ['What medications has this patient used?', 'medication, dose, dosage, mg, ml, daily, tablet, tab, mg/ml, po, p.o.'],
        ['What surgeries has this patient had?', 'surgery, surgeries'],
        ['What allergies does the patient have?', 'allergy, allergies']
    ]

    embedding_path = 'embeddings_all.npy'
    page_info_dict_all_path = 'page_info_dict_all.pickle'
    medical_records_extractor(file, queries, embedding_path, page_info_dict_all_path)
    # medical_records_extractor(file, queries)