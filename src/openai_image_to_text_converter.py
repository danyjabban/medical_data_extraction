from openai import OpenAI
import base64
import json
from utils import get_image_of_page
from io import BytesIO
f = open("secrets.json")
api_keys = json.load(f)
client = OpenAI(api_key=api_keys["openai_api_key_new"])


def convert_image_to_text_openai(image, user_content:str):
    """
    Takes image and prompt and returns a text based response
    ------
    Args:
        image (pil.image): image to be analyzed by LLM
        user_content (str): prompt to the LLM
    Returns:
        res (str): text response to the image and prompt
    """
    image = convert_img_to_base64(image)
    image_url = f"data:image/jpeg;base64,{image}"
    sys_content = get_system_prompt()
    res = call_model(image_url, sys_content, user_content)
    return res


def get_system_prompt():
    system_prompt = """
                You are a specialist in comprehending medical documents.
                Input images in the form of medical documents will be provided to you,
                and your task is to respond to questions based on the content of the input image.
                """
    return system_prompt


def call_model(image_url:str, sys_content:str, user_content:str):
    """
    call openai vision model
    ------
    Args:
        image_url (str): image to feed llm
        sys_content (str): prompt for llm system
        user_content (str): prompt for llm user
    Returns:
        json_string (str): string version of json response
    """
    response = client.chat.completions.create(
        model='gpt-4o', 
        messages=[
            {
                "role": "system",
                "content": sys_content
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_content},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ],
            }
        ],
        max_tokens=2000,
    )
    json_string = response.choices[0].message.content
    json_string = json_string.replace("```json\n", "").replace("\n```", "")
    return json_string


def convert_img_to_base64(img):
    """
    convert pil image to base64
    ------
    Args:
        img (pil.image): pil image to convert to base64
    Returns:
        img_base64 (base64): version of initial image 
    """
    buffer = BytesIO()
    # Save the image to the BytesIO object
    img.save(buffer, format="PNG")
    # Get the binary data
    img_binary = buffer.getvalue()
    # Encode the binary data to base64
    img_base64 = base64.b64encode(img_binary).decode("utf-8")
    return img_base64


    


if __name__ == "__main__":
    file = "../../SampleHealthRecord_Redacted.pdf"
    page_idx = 5
    image = get_image_of_page(page_idx, file)
    print(type(image))
    system_prompt = """
                You are a specialist in comprehending medical documents.
                Input images in the form of medical documents will be provided to you,
                and your task is to respond to questions based on the content of the input image.
                """
    user_prompt = """identify the medications the person has used and the dates they started and stopped if that information is available.
                return as a json where each key the medication and the value is a tuple of start and stop date

                if no information is available return "None"
                
                an example output: 
                {medication1 : (start_date, end_date),
                 medication1 : (start_date, end_date)}"""
    
    convert_image_to_text_openai(image, system_prompt, user_prompt)