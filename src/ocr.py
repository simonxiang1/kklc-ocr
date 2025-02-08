import os
import glob
import re
import time
import json

from pathlib import Path
from pdf2image import convert_from_path

import vertexai
from vertexai.generative_models import GenerativeModel, Part

def convert_pdf_to_jpg(pdf_path: str, output_dir: str, dpi: int = 300) -> list[str]:
    """
    Convert a PDF file to JPG images, one per page.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the JPG files
        dpi: Resolution for the output images (default 300)
    
    Returns:
        List of paths to the generated JPG files
    """

    # validate input path
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # convert PDF to images
    print(f"PDF {pdf_path} has been read successfully. Converting to JPG...")
    start = time.time()
    try:
        # convert_from_path returns a list of PIL Image objects
        pages = convert_from_path(
            pdf_path,
            dpi=dpi,
            fmt='jpg',
            thread_count=os.cpu_count() - 2  # use all but 2 CPU cores
        )
    except Exception as e:
        raise Exception(f"Error converting PDF: {str(e)}")
    
    # save each page as a JPG
    print(f"Successfully converted {pdf_path} to JPG. Saving pages...")
    output_paths = []
    for i, page in enumerate(pages, start=1):
        # format page number with leading zeros (001, 002, etc.)
        output_filename = f"{i:03d}.jpg"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            # save with high quality (98 out of 100)
            page.save(output_path, "JPEG", quality=98, optimize=True)
            output_paths.append(output_path)
        except Exception as e:
            raise Exception(f"Error saving page {i}: {str(e)}")
    end = time.time()
    
    print(f"Done in {(end-start):.03f} seconds!")
    # returns list of paths
    return output_paths


def find_jpg_files(dir: str) -> list[str]:
    """
    Find all .jpg files in the specified directory.
    
    Args:
        directory (str): Path to the directory to search
        
    Returns:
        list: List of paths to .jpg files
    """
    # search using glob on pattern
    pattern = os.path.join(dir, "*.jpg")
    return sorted(glob.glob(pattern))
    

def gemini_pdf_ocr(image_path: str, write_path: str) -> str:
    """
    Makes an API call to Gemini 2.0 Flash to transcribe the text.
        
    Args:
        image_path: Path to the image to be transcribed.
        write_path: Path to the file where transcriptions will be stored.

    Returns:
        Returns the file name write_path.
    """

    PROJECT_ID = "mimetic-fulcrum-450000-u4"
    vertexai.init(project=PROJECT_ID, location="us-central1")
    model = GenerativeModel("gemini-2.0-flash-001")

    # send data to gemini
    prompt = (
        "Please transcribe this page from a bilingual Japanese-English document as you see it."
        "This document contains entries and definitions for kanji characters: for each entry, "
        "output a single JSON object on one line containing the following content: "
        "The kanji being defined (with key \"kanji\"), its keywords (with key \"keywords\") in a "
        "single string separated by commas within the string, and then only the mnemonic, "
        "(with key \"mnemonic\"). "
        "Please remove all references to any associated kanji trailing the mnemonic within the mnemonic tag."
        "However, do not remove any text from the mnemonic itself, transcribe every part of it."
        "Do not include any markdown formatting or JSON tags, only output the raw JSON."

        "Take extra care to output the correct kanji and radicals when they appear."
        "Pay special attention to any radicals in parentheses - these are essential "
        "kanji components that must be preserved exactly as they appear in the original text. "
        "For example, if you see a man radical 亻 or a sword radical 刂, transcribe them "
        "exactly with their proper Unicode characters, not as letters or approximations. "
    )
    # helper function to format the image
    def image_to_part(image_path):
        with open(image_path, 'rb') as f:
            image_data = f.read()
        return Part.from_data(data=image_data, mime_type="image/jpeg")
    
    # calling on gemini to transcribe the image
    print(f"Received image {image_path}. Transcribing content...")
    start = time.time()
    response = model.generate_content(contents=[image_to_part(image_path), prompt])
    end = time.time()

    # makes write file if it doesn't exist, then writes transcriptions to it
    print(f"Done in {(end-start):.03f} seconds! Content written to {write_path}.")
    path = Path(write_path)
    path.touch()  
    with path.open('a') as file:
        file.write(response.text.strip() + "\n")

    # returns write path
    return write_path


def clean_jsonl(input_file: str, output_file: str) -> None:
    """
    Clean a JSONL file by fixing common issues:
    1. Ensure each JSON object is on its own line.
    2. Remove stray markdown tags.
    3. Correctly escape only incorrect quotes in the "mnemonic" field.

    Args:
        input_file (str): Path to input JSONL file.
        output_file (str): Path to output JSONL file.

    Returns:
        None
    """
    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        data = infile.read()
        
        # ensure each JSON object is on its own line
        data = data.replace('}{', '}\n{')  # Insert newline between JSON objects
        
        # remove stray markdown tags
        data = re.sub(r'```json', '', data)
        data = re.sub(r'```', '', data)
        
        for line in data.splitlines():
            line = line.strip()
            if not line:
                continue
            
            try:
                obj = json.loads(line)
                
                # fix unescaped quotes in the "mnemonic" field without double escaping
                if "mnemonic" in obj:
                    obj["mnemonic"] = re.sub(r'(?<!\\)"', '\\"', obj["mnemonic"])  # escape only incorrect quotes
                    obj["mnemonic"] = obj["mnemonic"].replace('\\', '')  # remove double-escaped backslashes

                
                outfile.write(json.dumps(obj, ensure_ascii=False) + "\n")
            except json.JSONDecodeError:
                continue  # skip invalid JSON lines