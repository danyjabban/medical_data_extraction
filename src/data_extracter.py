from embedding_process import get_embedding
import numpy as np
from image_to_text_converter import convert_image_to_text
from utils import get_image_of_page
import pickle
import time
from openai_image_to_text_converter import convert_image_to_text_openai



def data_extractor(embedding_matrix:np.array, page_info_dict:dict, queries:list[list], file:str):
    """
    takes in all information about each page of pdf, embeddings of each chunk, and questions
    asked about the documents and returns a dictionary of answers
    ------
    Args:
        embedding_matrix (np.array): (num_chunks x embedding_dim) matrix of each of the chunks
        extracted from the document
        page_info_dict (dict): dictionary that stores information about each page such as
        page vocabulary, indexes of associated embeddings
        queries (list[list]): each inner list contains the query and the associated terms 
        with that query, [query:str, query_key_words:str]
        file (str): path of pdf file
    Returns:
        res (dict): dictionary of results storing all answers to all questions
    """
    pages = get_relevent_pages(embedding_matrix, page_info_dict, queries) 
    res = extract_from_pages(pages, file)
    return res


def get_relevent_pages(embedding_matrix:np.array, page_info_dict:dict, queries:list[list]):
    """
    get the relevent pages to prompt the LLM for each of the queries
    ------
    Args:
        embedding_matrix (np.array): (num_chunks x embedding_dim) matrix of each of the chunks
        extracted from the document
        page_info_dict (dict): dictionary that stores information about each page such as
        page vocabulary, indexes of associated embeddings
        queries (list[list]): each inner list contains the query and the associated terms 
        with that query, [query:str, query_key_words:str]
    Returns:
        potential_pages
    """
    potential_pages = {}
    # iterate through queries
    for query in queries:
        potential_pages[query[0]] = []
        key_terms = query[1]
        key_terms_embed = get_embedding(key_terms)
        key_terms_set = set(key_terms.split(", "))
        # get similarity between vector_db and query key terms
        similarity = np.matmul(embedding_matrix, key_terms_embed)
        # get indexes above similarity threshold
        sim_indexes = np.where(similarity > .3)[0] 
        indexes_set = set(sim_indexes)
        # iterate through pages
        for k, v in page_info_dict.items():
            # get pages that include key words or have high enough similarity
            if v[0].intersection(key_terms_set) or v[1].intersection(indexes_set):
                potential_pages[query[0]] = potential_pages[query[0]] + [k]
    return potential_pages
    

def extract_from_pages(pages:dict, file:str):
    """
    for each query, pass pages that are relevent to LLM (openai or gemini) and store responses
    ------
    Args:
        pages (dict): dictionary that maps each query to a list of relevent pages
        file (str): path to pdf file
    Returns:
        extracted_info_dict (dict): dictionary that stores all the answers to each query
    """
    extracted_info_dict = {}
    for query, page_idxs in pages.items():
        prompt = prompt_from_query(query)
        for page_idx in page_idxs:
            image = get_image_of_page(page_idx, file)
            answer = convert_image_to_text_openai(image, prompt)
            processed_answer = process_answer(answer)
            print(processed_answer, page_idx)
            if processed_answer is not None:
                extracted_info_dict[query] = extracted_info_dict.get(query, []) + [[page_idx, processed_answer]]
    return extracted_info_dict


def prompt_from_query(query:str):
    """
    temporary solution, map query to prompt to get the llm to provide response in the desired format
    """
    if query == 'What surgeries has this patient had?':
        prompt = """identify the surgeries the person has had and the dates they occured if that information is available.
                return as a json where each key the surgery and the value is the date it occured.

                if no information is available return "None"
                
                an example output: 
                {surgery1 : date,
                 surgery2 : date}"""
        return prompt
    elif query == 'What medications has this patient used?':
        prompt = """identify the medications the person has used and the dates they started and stopped if that information is available.
                return as a json where each key the medication and the value is a tuple of start and stop date

                if no information is available return "None"

                only list surgeries if you are certain not other medical procedures
                
                an example output: 
                {medication1 : (start_date, end_date),
                 medication1 : (start_date, end_date)}"""
        return prompt 
    elif query == 'What allergies does the patient have?':
        prompt = """identify the allergies the person has had.
                return as a json where each key is an allergy the patient has and the value is "None".

                if no information is available return "None"
                
                an example output: 
                {allergy1 : None,
                 allergy2 : None}"""
        return prompt


def process_answer(text:str):
    """
    helper function to process answer into a readable dictionary format
    """
    if '{' in text and '}' in text:
        start = text.index('{')
        end = text.index('}')
        text = text[start:end+1]
        text = text.replace('\n', ' ')
        text = text.replace('null', 'None').replace('Null', 'None')
        try:
            new_text = eval(text)
        except:
            return None
        else:
            if not isinstance(new_text, dict):
                return None
            if valid_key(new_text):
                return new_text
    return None


def valid_key(d:dict):
    """
    helper function to check if answer is not a valid word
    """
    # common issues to handle
    invalid_keys = {'medication', 'medications', 'surgery', 'surgeries', 'allergy', 'allergies', 'none', 
                    'None', 'medication1', 'medication2', 'surgery1', 'surgery2', 'allergy1', 'allergy2'}
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

    embedding_matrix = np.load('embeddings_all.npy')
    with open('page_info_dict_all.pickle', 'rb') as handle:
        page_info_dict = pickle.load(handle)

    queries = [['medication', 'medication, dose, dosage, mg, ml, daily, tablet, tab, mg/ml, po, p.o.']]

    queries = \
    [
        ['What medications has this patient used?', 'medication, dose, dosage, mg, ml, daily, tablet, tab, mg/ml, po, p.o.'],
        ['What Surgeries has this patient had?', 'surgery, surgeries'],
        ['What allergies does the patient have?', 'allergy, allergies']
    ]
    data_extractor(embedding_matrix, page_info_dict, queries, file)
    # res = extract_from_pages(pages, file)
    # print(res)
    





