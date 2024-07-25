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

safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=MODEL_CONFIG, safety_settings=safety_settings)


def convert_image_to_text(image, user_prompt):
    system_prompt = """
                You are a specialist in comprehending medical documents.
                Input images in the form of medical documents will be provided to you,
                and your task is to respond to questions based on the content of the input image.
                """
    
    input_prompt= [system_prompt, image, user_prompt]
    response = model.generate_content(input_prompt)
    return response.text


def summarize_image(image):
    user_prompt = "summerize the information on this medical form"
    summary = convert_image_to_text(image, user_prompt)
    return summary

