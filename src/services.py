import os
import json
import openai
import pytesseract
from PIL import Image

# Set up your Tesseract and OpenAI config
pytesseract.pytesseract.tesseract_cmd = os.getenv(
    "TESSERACT_PATH", 
    r"D:\Program Files\Tesseract-OCR\tesseract.exe" #Make sure to change this to where your tesseract is installed.
)
openai.api_key = os.getenv("OPENAI_API_KEY")


# Functions schema for function calling
FUNCTIONS_SCHEMA = [
    {
        "name": "extract_receipt_data",
        "description": (
            "Extract the purchases, their prices, quantities, and the total amount from the receipt text. "
            "If there are two items with the same price, combine them and increase their quantity. "
            "Always provide a 'quantity' field."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "quantity": {"type": "number"},
                            "price": {"type": "number"}
                        },
                        "required": ["description", "quantity", "price"]
                    }
                },
                "total": {
                    "type": "number",
                    "description": "The total amount for the purchase"
                }
            },
            "required": ["items", "total"]
        }
    }
]


def extract_text_from_image(image_path: str) -> str:
    """
    Use PIL + Tesseract to extract text from the given image path.
    """
    image = Image.open(image_path)
    extracted_text = pytesseract.image_to_string(image)
    return extracted_text


def get_receipt_data_from_gpt(receipt_text: str) -> dict:

    # System prompt explaining the requirement
    system_prompt = (
        "You are a helpful assistant that extracts a structured table (items and total) "
        "from a receipt text. If there are two items with the same price, combine them and "
        "increase their quantity. Always provide a 'quantity' field. Return only valid JSON."
    )

    # Prepare the chat messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": receipt_text},
    ]

    # Call GPT with function calling
    response = openai.chat.completions.create(
        model="gpt-4-0613",  
        messages=messages,
        functions=FUNCTIONS_SCHEMA,
        function_call="auto"
    )

    function_call = response.choices[0].message.function_call
    if not function_call:
        raise ValueError("GPT did not return a function call.")
    
    args_str = function_call.arguments
    data = json.loads(args_str)
    return data
