from embedding_process import get_embedding
import numpy as np
from image_to_text_converter import convert_image_to_text

def data_extractor(embedding_matrix, page_info_dict, queries):
    pages = get_relevent_pages(embedding_matrix, page_info_dict, queries)
    extract_from_pages(pages)


def get_relevent_pages(embedding_matrix, page_info_dict, queries):
    potential_pages = {}
    for query in queries:
        potential_pages[query[0]] = []
        key_terms = query[1]
        key_terms_embed = get_embedding(key_terms)
        key_terms_set = set(key_terms.split(", "))
        similarity = np.matmul(embedding_matrix, key_terms_embed)

        sim_indexes = np.where(similarity > .28)[0]
        indexes_set = set(sim_indexes)
        for k, v in page_info_dict:
            if v[0].intersection(key_terms_set) or v[1].intersection(indexes_set):
                potential_pages[query[0]] = potential_pages[query[0]] + [k]
    

def extract_from_pages(pages:dict):
    extracted_info_dict = {}
    for query, page_idx in pages:
        






