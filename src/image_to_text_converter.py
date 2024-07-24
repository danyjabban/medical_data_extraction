import google.generativeai as genai
import json
api_keys = json.load("secrets.json")
GOOGLE_API_KEY = api_keys["googleai_api_key"]
genai.configure(api_key=GOOGLE_API_KEY)
from pathlib import Path


MODEL_CONFIG = {
    "temperature":0.2,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096
}

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=MODEL_CONFIG)


def convert_image_to_text(image_path, system_prompt, user_prompt):
    image_info = image_format(image_path)
    input_prompt= [system_prompt, image_info[0], user_prompt]
    response = model.generate_content(input_prompt)
    return response.text


def convert_image_to_text2(image, user_prompt):
    system_prompt = """
                You are a specialist in comprehending medical documents.
                Input images in the form of medical documents will be provided to you,
                and your task is to respond to questions based on the content of the input image.
                """
    # user_prompt = """identify the medications the person has used and the dates they started and stopped if that information is available.
    #             return as a json where each key the medication and the value is a tuple of start and stop date"""
    
    input_prompt= [system_prompt, image, user_prompt]
    response = model.generate_content(input_prompt)
    return response.text


def image_format(image_path):
    img = Path(image_path)

    if not img.exists():
        raise FileNotFoundError(f"Could not find image: {img}")

    image_parts = [
        {
            "mime_type": "image/png", ## Mime type are PNG - image/png. JPEG - image/jpeg. WEBP - image/webp
            "data": img.read_bytes()
        }
    ]
    return image_parts

if __name__ == "__main__":
    system_prompt = """
                You are a specialist in comprehending medical documents.
                Input images in the form of medical documents will be provided to you,
                and your task is to respond to questions based on the content of the input image.
                """

    image_path = "../../all_info.png"


    # user_prompt = "what allergies does the patient have?"
    # user_prompt = "what surgeries has the patient had? return the resposne in the following json format: {'surgery':'data of surgery'}"
    # user_prompt = """identify the surgeries the patient has had and the dates they took place if that information is available.
    # return as a json where each key the surgery and the value is the date it occurred"""
    # user_prompt = "what surgeries has the patient had? provide as a python list. no preamble"

    user_prompt = """identify the medications the person has used and the dates they started and stopped if that information is available.
    return as a json where each key the medication and the value is a tuple of start and stop date"""
    # user_prompt = "what is the patient's name, provider's name, data"
    # user_prompt = "summerize the information on this medical form"

    out = convert_image_to_text(image_path, system_prompt, user_prompt)
    print(out)

