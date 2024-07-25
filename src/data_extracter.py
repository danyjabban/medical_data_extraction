from embedding_process import get_embedding
import numpy as np
from image_to_text_converter import convert_image_to_text
from utils import get_image_of_page
import pickle
import time


def data_extractor(embedding_matrix, page_info_dict, queries, file):
    pages = get_relevent_pages(embedding_matrix, page_info_dict, queries)
    print(pages)
    res = extract_from_pages(pages, file)
    # print(res)
    return res


def get_relevent_pages(embedding_matrix, page_info_dict, queries):
    """
    embedding_matrix (np.array)
    page_info_dict (dict)
    queries (list[tuple]): (query:str, query_key_words:str)
    """
    potential_pages = {}
    for query in queries:
        potential_pages[query[0]] = []
        key_terms = query[1]
        key_terms_embed = get_embedding(key_terms)
        key_terms_set = set(key_terms.split(", "))
        similarity = np.matmul(embedding_matrix, key_terms_embed)

        sim_indexes = np.where(similarity > .3)[0]
        indexes_set = set(sim_indexes)
        for k, v in page_info_dict.items():
            # print(k)
            # print(v[0].intersection(key_terms_set))
            # print(v[1].intersection(indexes_set))
            # for i in v[1].intersection(indexes_set):
                # print(similarity[i])
            if v[0].intersection(key_terms_set) or v[1].intersection(indexes_set):
                potential_pages[query[0]] = potential_pages[query[0]] + [k]
    return potential_pages
    

def extract_from_pages(pages:dict, file):
    extracted_info_dict = {}
    for query, page_idxs in pages.items():
        prompt = prompt_from_query(query)
        for page_idx in page_idxs:
            image = get_image_of_page(page_idx, file)
            answer = convert_image_to_text(image, prompt)
            time.sleep(20)
            # print(answer)
            processed_answer = process_answer(answer)
            print(processed_answer, page_idx)
            if processed_answer is not None:
                extracted_info_dict[query] = extracted_info_dict.get(query, []) + [[page_idx, processed_answer]]
                # d = extracted_info_dict.get(query, {})
                # d[page_idx] = processed_answer
                # extracted_info_dict[query][] = extracted_info_dict.get(query, {}) + [[page_idx, processed_answer]]

    return extracted_info_dict


def prompt_from_query(query):
    if query == 'surgeries':
        prompt = """identify the surgeries the person has had and the dates they occured if that information is available.
                return as a json where each key the surgery and the value is the date it occured.

                if no information is available return "None"
                
                an example output: 
                {surgery1 : date,
                 surgery2 : date}"""
        return prompt
    elif query == 'medication':
        prompt = """identify the medications the person has used and the dates they started and stopped if that information is available.
                return as a json where each key the medication and the value is a tuple of start and stop date

                if no information is available return "None"
                
                an example output: 
                {medication1 : (start_date, end_date),
                 medication1 : (start_date, end_date)}"""
        return prompt 
    elif query == 'allergies':
        prompt = """identify the allergies the person has had.
                return as a json where each key is an allergy the patient has and the value is "None".

                if no information is available return "None"
                
                an example output: 
                {allergy1 : None,
                 allergy2 : None}"""
        return prompt



def process_answer(text):
    if '{' in text:
        start = text.index('{')
        end = text.index('}')
        text = text[start:end+1]
        text = text.replace('\n', ' ')
        new_text = eval(text)
        if valid_key(new_text):
            return new_text
    return None


def valid_key(d):
    invalid_keys = {'medication', 'medications', 'surgery', 'surgeries', 'allergy', 'allergies', 'none', 'None'}
    for k in d.keys():
        if k in invalid_keys:
            return False
    return True
        
        



if __name__ == "__main__":
    query = 'medication'
    # query = 'surgeries'
    # query = 'allergies'
    idx = [51, 52, 111]
    # idx = [51]
    pages = {query: idx}
    file = "../../SampleHealthRecord_Redacted.pdf"

    embedding_matrix = np.load('embeddings.npy')
    with open('page_info_dict.pickle', 'rb') as handle:
        page_info_dict = pickle.load(handle)

    queries = [['medication', 'medication, dose, dosage, mg, ml, daily, tablet, tab, mg/ml, po, p.o.']]
    data_extractor(embedding_matrix, page_info_dict, queries, file)
    # res = extract_from_pages(pages, file)
    # print(res)






