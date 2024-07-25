from embedding_process import get_embedding
import pypdfium2 as pdfium


def chunk_helper(text:str):
    """
    take text and sepate it into a list of smaller texts
    """
    text = text.replace('.', '\n').replace('?', '\n').replace('!', '\n')
    chunks = text.split('\n')
    return chunks


def embedding_helper(chunks:list):
    """
    take chunks of text and convert them to embeddings
    """
    chunk_embeds = []
    for chunk in chunks:
        if chunk == '':
            continue
        chunk_embed = get_embedding(chunk)
        chunk_embeds.append(chunk_embed)
    return chunk_embeds


def get_page_vocab(text:str):
    """
    get the set of words present in a given text
    """
    text = text.lower()
    text = text.replace('\n', ' ')
    vocab = text.split(' ')
    vocab = set(vocab)
    return vocab


def get_image_of_page(page_idx:int, file:str):
    """
    take in a file and a page number and convert that page to a pil image
    """
    pdf = pdfium.PdfDocument(file)
    page = pdf.get_page(page_idx)
    pil_image = page.render(scale = 300/72).to_pil()
    return pil_image