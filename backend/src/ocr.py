import os
import glob
import time
from pathlib import Path
from pdf2image import convert_from_path

import vertexai
from vertexai.generative_models import GenerativeModel, Part

def convert_pdf_to_jpg(pdf_path: str, output_dir: str, dpi: int = 400) -> list[str]:
    """
    Convert a PDF file to JPG images, one per page.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory to save the JPG files
        dpi (int): Resolution for the output images (default 300)
    
    Returns:
        list[str]: List of paths to the generated JPG files
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
        list[str]: List of paths to .jpg files
    """
    # search using glob on pattern
    pattern = os.path.join(dir, "*.jpg")
    return sorted(glob.glob(pattern))
    

def gemini_pdf_ocr(image_path: str, write_path: str) -> str:
    """
    Makes an API call to Gemini 2.0 Flash to transcribe the text.
        
    Args:
        image_path (str): Path to the image to be transcribed.
        write_path (str): Path to the file where transcriptions will be stored.

    Returns:
        str: The write path of the content.
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

def run_ocr_pipeline(
        kklc_entries_path: str, 
        output_folder_path: str,
        output_file_path: str,
        dpi: int = 400
    ) -> None:
    """
    Runs the entire OCR pipeline from start to finish (~30 min).
    Make sure you're authenticated with Google Cloud.
    Requires a PDF copy of KKLC to live at `kklc_entries_path`. (Ideally just the entry pages.)
    Writes all data to a JSONL file at `output_file_path`. 
    The data will be messy (~0.5-1% will error), which will require some manual cleaning. 

    Args:
        kklc_entries_path (str): Path to the PDF file containing all KKLC entries.
        output_folder_path (str): Path to the folder where the PDF -> image conversions should live.
        output_file_path (str): Path to the file where the post OCR JSONL should live.
        dpi (int): The resolution of the image ouputs from PDF -> image conversions.

    Returns:
        None
    """
    start = time.time()

    # converting images
    image_paths = convert_pdf_to_jpg(kklc_entries_path, output_folder_path, dpi)
    
    # sends each image to gemini and writes to output_file_path
    for image_path in image_paths:
        gemini_pdf_ocr(image_path, output_file_path)
    end = time.time()

    print(f"Done in {(end-start)/60:0.02f} minutes.")

    return