import time
import json
from src.ocr import convert_pdf_to_jpg, find_jpg_files, gemini_pdf_ocr, clean_jsonl
from src.post_processing import read_dbjs, read_jsonl, analyze_and_merge

def main():
    print("Hello from KKLC-OCR!")

    # start = time.time()
    # # image_paths = convert_pdf_to_jpg("data/kklc_entries.pdf", "outputs", dpi=400)
    # image_paths = find_jpg_files("outputs")
    
    # for image_path in image_paths:
    #     gemini_pdf_ocr(image_path, "outputs/kanji_entries.jsonl")

    # end = time.time()
    # print(f"Done in {(end-start)/60:0.02f} minutes.")
    print(f"Cleaning data...")
    clean_jsonl("outputs/kanji_entries.jsonl", "data/clean_kanji.jsonl")
    print("Done!")

    db_data = read_dbjs("data/db.js")
    jsonl_data = read_jsonl("data/clean_kanji.jsonl")
    results = analyze_and_merge(jsonl_data, db_data)

    # Print statistics
    print(f"\nStatistics:")
    print(f"Total matches: {results['stats']['total_matches']}")
    print(f"Total extras (only in JSONL): {results['stats']['total_extras']}")
    print(f"Total missing (only in DB.js): {results['stats']['total_missing']}")
    
    # Save results
    with open('merged_data.json', 'w', encoding='utf-8') as f:
        json.dump(results['merged'], f, ensure_ascii=False, indent=2)
    
    # Save analysis results
    with open('analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'extras': results['extras'],
            'missing': results['missing']
        }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
