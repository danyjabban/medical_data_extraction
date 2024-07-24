import typing
from data_ingester import ingest_info
from data_extracter import data_extractor
from post_processer import post_processor


def medical_records_extractor(file:str, queries:list[tuple]):
    embedding_matrix, page_info_dict = ingest_info(file)
    answers = data_extractor(embedding_matrix, page_info_dict, queries, file)
    post_processor(answers)



if __name__ == "__main__":
    user_prompt = """identify the medications the person has used and the dates they started and stopped if that information is available.
                return as a json where each key the medication and the value is a tuple of start and stop date"""
    