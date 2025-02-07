import time
from src.ocr import convert_pdf_to_jpg, find_jpg_files, gemini_pdf_ocr, clean_jsonl

def main():
    print("Hello from KKLC-OCR!")

    start = time.time()
    # image_paths = convert_pdf_to_jpg("data/kklc_entries.pdf", "outputs", dpi=400)
    image_paths = find_jpg_files("outputs")
    
    for image_path in image_paths:
        gemini_pdf_ocr(image_path, "outputs/kanji_entries.jsonl")

    end = time.time()
    print(f"Done in {(end-start)} seconds.")
    print(f"Cleaning data...")

    clean_jsonl("outputs/kanji_entries.jsonl", "outputs/clean_kanji.jsonl")
    print("Done!")

if __name__ == "__main__":
    main()
