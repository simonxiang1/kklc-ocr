from google import genai
from PIL import Image

import os
from dotenv import load_dotenv

def gemini_pdf_ocr(image_path):
    """Makes an API call to Gemini 2.0 Flash to transcribe the text.
        Returns a JSON object."""

    load_dotenv()
    key = os.environ.get('GEMINI_API_KEY')
    client = genai.Client(api_key=key)

    image = Image.open(image_path)
    prompt = "Please transcribe this page from a bilingual Japanese-English document as you see it. This document contains entries and definitions for kanji characters: for each entry, output in JSON format just the kanji being defined (with key \"kanji\"), its keywords (with key \"keywords\") in a single string separated by commas within the string, and then only the mnemonic (without the associated kanji following the mnemonic) with proper punctuation and correct radicals (with key \"mnemonic\"). Output only the relevant JSON objects and nothing else. Make sure to use the correct kanji."
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[image, prompt])
    print(response.text)

