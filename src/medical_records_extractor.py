import typing
from data_ingester import ingest_info
from data_extracter import data_extractor
from post_processer import post_processor

import numpy as np
import pickle


def medical_records_extractor(file:str, queries:list[tuple]):
    # embedding_matrix, page_info_dict = ingest_info(file)
    embedding_matrix = np.load('embeddings.npy')
    with open('page_info_dict.pickle', 'rb') as handle:
        page_info_dict = pickle.load(handle)
    answers = data_extractor(embedding_matrix, page_info_dict, queries, file)
    post_processor(answers)



if __name__ == "__main__":
    file = "../../SampleHealthRecord_Redacted.pdf"
    queries = [['medication', 'medication, dose, dosage, mg, ml, daily, tablet, tab, mg/ml, po, p.o.']]

    medical_records_extractor(file,queries)