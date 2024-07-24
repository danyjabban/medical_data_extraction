import google.generativeai as genai
import json
f = open("secrets.json")
api_keys = json.load(f)
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


def convert_image_to_text(image, user_prompt):
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


def summarize_image(image):
    user_prompt = "summerize the information on this medical form"
    convert_image_to_text(image, user_prompt)

