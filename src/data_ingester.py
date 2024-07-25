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
import pickle
import time



def ingest_info(file):
    pdf_file = fitz.open(file)
    all_embeddings = []
    page_info_dict = {}
    for page_idx in range(100):#[42]: #[86]:#range(pdf_file.page_count):
        # text_from_text = process_text(page_idx, pdf_file, file)
        text_from_text = ''
        text_from_image = process_image(page_idx, pdf_file)
        page_text = text_from_text + '\n' + text_from_image

        vocab = get_page_vocab(page_text)
        chunks = chunk_helper(page_text)
        page_embeddings = embedding_helper(chunks)

        page_embed_idxs = {i for i in range(len(all_embeddings), len(all_embeddings) + len(page_embeddings))}

        all_embeddings = all_embeddings + page_embeddings
        page_info_dict[page_idx] = [vocab, page_embed_idxs]

    all_embeddings = np.array(all_embeddings)
    return all_embeddings, page_info_dict
                

def process_table(page_idx, file):
    pdf = pdfium.PdfDocument(file)
    page = pdf.get_page(page_idx)

    pil_image = page.render(scale = 300/72).to_pil()

    text = summarize_image(pil_image)
    return text
    

def process_text(page_idx, pdf_file, file):
    page = pdf_file[page_idx]
    text = page.get_text()
    parsed = is_parsed(text)
    if not parsed:
        pdf = pdfium.PdfDocument(file)
        page = pdf.get_page(page_idx)
        pil_image = page.render(scale = 300/72).to_pil()
        text = summarize_image(pil_image)
    return text


def is_parsed(text):
    ## todo
    return False


def process_image(page_idx, pdf_file):
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
            # print(text)
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            conf = np.mean([numb for numb in data.get('conf') if numb > 0])
            print(page_idx)
            print('ocr', conf)
            if conf < 75:
                # time.sleep(10)
                print('summary')
                text = summarize_image(image)

    return text
            


if __name__ == "__main__":
    file = "../../SampleHealthRecord_Redacted.pdf"
    all_embeddings, page_info_dict = ingest_info(file)

    # np.save('embeddings.npy', all_embeddings)
    # with open('page_info_dict.pickle', 'wb') as handle:
    #     pickle.dump(page_info_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
