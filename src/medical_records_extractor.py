"""
takes in a pdf of an individuals medical history and 
"""
import fitz
import pypdfium2 as pdfium
import numpy as np
from image_to_text_converter import convert_image_to_text2
import pytesseract
import io
from PIL import Image
import json
from embedding_process import get_embedding




def extract_info(file):
    pdf_file = fitz.open(file)
    for page_idx in [86]:#range(pdf_file.page_count):
        process_text(page_idx, pdf_file, file)
        # process_table(page_idx, file)
        # process_image(page_idx, pdf_file)
                

def process_table(page_idx, file):
    # t = page.find_tables()
    # t = t[0]
    # for line in t.extract():  # print cell text for each row
    #     print(line)
    pdf = pdfium.PdfDocument(file)
    page = pdf.get_page(page_idx)

    pil_image = page.render(scale = 300/72).to_pil()

    out = convert_image_to_text2(pil_image)
    str_json = out.replace('```json\n', '').replace('\n```', '')
    print(str_json)
    print(json.loads(str_json))
    

def process_text(page_idx, pdf_file, file):
    page = pdf_file[page_idx]

    text = page.get_text() #.encode("utf8") # get plain text (is in UTF-8)
    # text = text.replace('\n', '')
    parsed = is_parsed(text)
    if not parsed:
        pdf = pdfium.PdfDocument(file)
        page = pdf.get_page(page_idx)

        pil_image = page.render(scale = 300/72).to_pil()
        
        user_prompt = "summerize the information on this medical form"

        text = convert_image_to_text2(pil_image, user_prompt)
        # str_json = out.replace('```json\n', '').replace('\n```', '')
        chunks = text.split('.')
        print(chunks)
        chunk_embeds = []
        for chunk in chunks:
            if chunk == '':
                continue
            chunk_embed = get_embedding(chunk)
            chunk_embeds.append(chunk_embed)
        chunk_embeds = np.array(chunk_embeds)
        
        med_words = get_embedding('medication, dose, dosage, mg, ml, daily, tablet, tab, mg/ml, po, p.o.')
        surgery = get_embedding('surgery')

        sim_med = np.matmul(chunk_embeds, med_words)
        sim_sur = np.matmul(chunk_embeds, surgery)
        print(sim_med)
        print('*******')
        print(sim_sur)


def is_parsed(text):
    ## todo
    return False


def process_image(page_idx, pdf_file):
    page = pdf_file[page_idx]
    image_li = page.get_images()
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
            

            print(text.split('\n'))
            print(len(text.split('\n')))


if __name__ == "__main__":
    file = "../../SampleHealthRecord_Redacted.pdf"
    extract_info(file)
