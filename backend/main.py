import time
import os
from src.ocr import convert_pdf_to_jpg, find_jpg_files, gemini_pdf_ocr
from src.post_processing import clean_jsonl, read_dbjs, read_jsonl, merge_jsonl_and_db

def main():
    print("Hello from KKLC-OCR!")

    # start = time.time()
    # # image_paths = convert_pdf_to_jpg("data/kklc_entries.pdf", "outputs", dpi=400)
    # image_paths = find_jpg_files("outputs")
    
    # for image_path in image_paths:
    #     gemini_pdf_ocr(image_path, "outputs/kanji_entries.jsonl")

    # end = time.time()
    # print(f"Done in {(end-start)/60:0.02f} minutes.")
    
    # data cleaning
    print(f"Cleaning data...")
    clean_jsonl(input_file="outputs/kanji_entries.jsonl", output_file="data/clean_kanji.jsonl")
    print("Done!")

    # merging dbs 
    db_data = read_dbjs("data/db.js")
    jsonl_data = read_jsonl("data/clean_kanji.jsonl")
    _ = merge_jsonl_and_db(jsonl_data, db_data, "data/complete_kanji_db.json")
    os.remove("data/clean_kanji.jsonl")

if __name__ == "__main__":
    main()
