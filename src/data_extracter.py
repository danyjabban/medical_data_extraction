from embedding_process import get_embedding
import numpy as np
from image_to_text_converter import convert_image_to_text
from utils import get_image_of_page


def data_extractor(embedding_matrix, page_info_dict, queries, file):
    pages = get_relevent_pages(embedding_matrix, page_info_dict, queries)
    res = extract_from_pages(pages, file)
    print(res, 'res')


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
    

def extract_from_pages(pages:dict, file):
    extracted_info_dict = {}
    for query, page_idxs in pages.items():
        prompt = prompt_from_query(query)
        for page_idx in page_idxs:
            image = get_image_of_page(page_idx, file)

            answer = convert_image_to_text(image, prompt)
            processed_answer = process_answer(answer)
            print(type(processed_answer), processed_answer)
            if processed_answer is not None:
                extracted_info_dict[query] = extracted_info_dict.get(query, []) + [processed_answer]
    # print('end of func', extracted_info_dict)
    return extracted_info_dict


def prompt_from_query(query):
    if query == 'surgeries':
        return ''
    elif query == 'medication':
        prompt = """identify the medications the person has used and the dates they started and stopped if that information is available.
                return as a json where each key the medication and the value is a tuple of start and stop date

                if no information is available return "None"
                
                an example output: 
                {medication1 : (start_date, end_date),
                 medication1 : (start_date, end_date)}"""
        return prompt 
    elif query == 'allergies':
        return ''



def process_answer(text):
    if '{' in text:
        start = text.index('{')
        end = text.index('}')
        text = text[start:end+1]
        text = text.replace('\n', ' ')
        new_text = eval(text)
        return new_text
    else:
        return None



if __name__ == "__main__":
    query = """identify the medications the person has used and the dates they started and stopped if that information is available.
                return as a json where each key the medication and the value is a tuple of start and stop date

                if no information is available return "None"
                
                an example output: 
                {medication1 : (start_date, end_date),
                 medication1 : (start_date, end_date)}"""
    
    # query = """identify the allergies the person has if available.
    #             return as a json where each key the medication and the value is a tuple of start and stop date
                
    #             an example output: 
    #             {medication1 : (start_date, end_date),
    #              medication1 : (start_date, end_date)}"""
    
    # query = """identify the medications the person has used and the dates they started and stopped if that information is available.
    #             return each medication on a new line, with its start date and end date if available all seperated by commmas"""
    #             # return as a python list of tuples where each key the medication and the value is a tuple of start and stop date"""


    # query = """identify the medications the person has used and the dates they started and stopped if that information is available.
    #             each line should include a medication, and if available, the start and end date of the medication otherwise return 'none'. seperate these by comma"""

    # query = """identify the medications the person has used and the dates they started and stopped if that information is available.
    #             return as a python where each key the medication and the value is a tuple of start and stop date"""

    # query = """identify the medications the person has used and the dates they started and stopped if that information is available.
    #             return as a list of lists where each list has the medication the start and the stop date

    #             if the start or stop date is not specified then replace it with "none"
                
    #             an example output: 
    #             [
    #             [medication1, start_date, end_date],
    #              medication2, start_date, end_date]
    #              ]"""

    query = 'medication'
    idx = [51, 52, 111]
    pages = {query: idx}
    file = "../../SampleHealthRecord_Redacted.pdf"
    res = extract_from_pages(pages, file)
    print(res)






