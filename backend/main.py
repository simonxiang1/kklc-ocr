from src.ocr import run_ocr_pipeline
from src.post_processing import run_data_cleaning_pipeline

def main():
    print("Hello from KKLC-OCR!")

    # uncomment to run the full OCR pipeline: takes about ~30 minutes.
    # run_ocr_pipeline("data/kklc_entries.pdf", "outputs", "outputs/kanji_entries.jsonl")
    
    # data cleaning pipeline
    run_data_cleaning_pipeline(
        ocr_jsonl="outputs/kanji_entries.jsonl",
        source_db="data/db.js",
        output_path="data/complete_kanji_db.json",
    )

    print("All done!")

if __name__ == "__main__":
    main()
