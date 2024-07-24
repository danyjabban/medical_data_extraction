import typing
from data_ingester import ingest_info
from data_extracter import data_extractor
from post_processer import post_processor


def medical_records_extractor(file:str, queries:list[tuple]):
    embedding_matrix, page_info_dict = ingest_info(file)
    answers = data_extractor(embedding_matrix, page_info_dict, queries)
    post_processor(answers)

