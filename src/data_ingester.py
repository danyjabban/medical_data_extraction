"""
takes in a pdf of an individuals medical history and 
"""
import fitz
import pypdfium2 as pdfium
import numpy as np
from image_to_text_converter import summarize_image
import pytesseract
import io
from PIL import Image
from utils import *

import nltk
from nltk.corpus import words
import re
nltk.download('words')



def ingest_info(file:str):
    """
    take in a pdf file, process each page, store all the information 
    about each page in the page_info_dict dictionary and create a
    "vector database" all_embedding for the entire pdf
    ------
    Args:
        file (str): location of pdf file to parse
    Returns:
        all_embeddings (np.array): embeddings of the chunked text from the pdf
        page_info_dict (dict): dictionary that stores the vocabulary and embedding 
        indexes of each page
    """
    pdf_file = fitz.open(file)
    all_embeddings = []
    page_info_dict = {}
    # iterate through each page
    for page_idx in range(pdf_file.page_count):
        # get text from text on page
        text_from_text = process_text(page_idx, pdf_file, file)
        # get text from images on page
        text_from_image = process_image(page_idx, pdf_file)
        page_text = text_from_text + '\n' + text_from_image

        vocab = get_page_vocab(page_text)
        chunks = chunk_helper(page_text)
        page_embeddings = embedding_helper(chunks)

        # get indexes of all embeddings for given page
        page_embed_idxs = {i for i in range(len(all_embeddings), len(all_embeddings) + len(page_embeddings))}

        all_embeddings = all_embeddings + page_embeddings
        page_info_dict[page_idx] = [vocab, page_embed_idxs]

    all_embeddings = np.array(all_embeddings)
    return all_embeddings, page_info_dict
    

def process_text(page_idx:int, pdf_file, file:str):
    """
    parse text from page. if text is not parsed well convert 
    page to image and apply tesseract ocr to extract info 
    ------
    Args:
        page_idx (int): page index
        pdf_file (pymupdf.Document): pdf object to extract page
        file (str): location of pdf file
    Returns:
        text (str): text extracted from pdf page
    """
    page = pdf_file[page_idx]
    text = page.get_text()
    parsed = is_parsed(text)
    if not parsed:
        pdf = pdfium.PdfDocument(file)
        page = pdf.get_page(page_idx)
        pil_image = page.render(scale = 300/72).to_pil()
        
        text = pytesseract.image_to_string(pil_image, lang='eng')
    return text


def is_parsed(text:str):
    """
    helper function to check if text extracted from pdf page
    is parsed properly or if there were decoding errors
    ------
    Args:
        text (str): text from pdf page
    Returns:
        parsed (bool): boolean whether text was extracted well or not
    """
    word_list = set(words.words())
    processed_text = text.lower()
    processed_text = processed_text.replace('\n', ' ')
    processed_text = clean_text(processed_text)
    processed_text = set(processed_text.split(' '))
    intersection = word_list.intersection(processed_text)
    ratio = len(intersection) / len(processed_text)
    if ratio > .2 or len(text) < 20:
        return True
    return False


def clean_text(text:str):
    """
    helper function to clean text further
    """
    text = re.sub(r'[^A-Za-z0-9\s]+', '', text)
    return text


def process_image(page_idx:int, pdf_file):
    """
    extract text from images in pdf page useing tesseract ocr.
    if tesseract has low confidence get text summary of image from LLM
    ------
    Args:
        page_idx (int):
        pdf_file (pymupdf.Document): pdf object to extract page
    Returns:
        text (str): text extracted or summarized from images 
    """
    page = pdf_file[page_idx]
    image_li = page.get_images()
    text = ''
    if image_li:
        for image_index, img in enumerate(page.get_images(), start=1):
            #get the XREF of the image
            xref = img[0]
            #extract the image bytes
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image, lang='eng')
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            conf = np.mean([numb for numb in data.get('conf') if numb > 0])
            if conf < 75: 
                text = summarize_image(image)
    return text
            


if __name__ == "__main__":
    file = "../../SampleHealthRecord_Redacted.pdf"
    all_embeddings, page_info_dict = ingest_info(file)

    # np.save('embeddings_all.npy', all_embeddings)
    # with open('page_info_dict_all.pickle', 'wb') as handle:
    #     pickle.dump(page_info_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
