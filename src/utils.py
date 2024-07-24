from embedding_process import get_embedding
import pypdfium2 as pdfium


def chunk_helper(text):
    text = text.replace('.', '\n').replace('?', '\n').replace('!', '\n')
    text = text.split('\n')
    return text


def embedding_helper(chunks):
    chunk_embeds = []
    for chunk in chunks:
        if chunk == '':
            continue
        chunk_embed = get_embedding(chunk)
        chunk_embeds.append(chunk_embed)
    return chunk_embeds


def get_page_vocab(text):
    text = text.lower()
    text = text.replace('\n', ' ')
    vocab = text.split(' ')
    vocab = set(vocab)
    return vocab


def get_image_of_page(page_idx, file):
    pdf = pdfium.PdfDocument(file)
    page = pdf.get_page(page_idx)
    pil_image = page.render(scale = 300/72).to_pil()
    return pil_image