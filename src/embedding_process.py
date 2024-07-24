from openai import OpenAI
client = OpenAI(api_key='sk-proj-65KZmzkViEnxNZrV23qmT3BlbkFJ2Wo4v86ZAdv5X9pell2l')
import tiktoken
import numpy as np


def get_embedding(text:str, model:str="text-embedding-3-large", max_tok:int=8192):
    '''
    Calls OpenAI to create an embedding for a single document
    ------
    Args: 
        text (str): article to convert to embedding
        model (str): model version
        max_tok (int): maximum number of tokens to use when creating embedding
    Returns:
        embedding (list[float]): embedding for given document
    '''
    encoding = tiktoken.get_encoding("cl100k_base")
    text = text.replace("\n", " ").replace("<p>", " ").replace("</p>", " ")
    tokens = encoding.encode(text)
    embedding = client.embeddings.create(input = [tokens[:max_tok]], model=model).data[0].embedding
    return np.array(embedding)