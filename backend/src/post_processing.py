import os
import json
import re
import requests
import time
from time import sleep

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

def read_jsonl(file_path: str) -> dict:
    """
    Reads in JSONL file and returns dict with kanji as key.
    Cleans up the comma keyword spacing too.

    Args:
        file_path (str): A path to the JSONL db.

    Returns:
        dict: A dict containing the JSONL db contents.
    """

    data = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line.strip())
            if 'keywords' in entry:
                entry['keywords'] = re.sub(r',\s*', ', ', entry['keywords'])
            data[entry['kanji']] = entry
    return data

def read_source_db(file_path: str) -> dict:
    """
    Reads in a JSON source db (DB.js file) and returns dict with kanji as key.

    Args:
        file_path (str): Path to the source db JSON.

    Returns:
        dict: A dict containing the db JSON contents.
    """

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # remove the "var database = " prefix and any trailing semicolons
        content = content.replace('var database = ', '').strip().rstrip(';')
        # parse the remaining JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error parsing DB.js: {e}")
            return {}

def merge_jsonl_and_source(
        jsonl_data: dict,
        source_data: dict,
        save_merged: str,
        save_extras: str = None,
        save_missing: str = None,
        logging: bool = True
    ) -> None:
    """
    Merges the OCR JSONL and source dictionaries and saves it to a specified path. Returns None.
    Here the `source_data` is the reference DB, but we keep the "keyword" field from the JSONL db.
    Make sure to check the artifacts (`extras`, `missing`) at `save_path`.
    IMPORTANT! Manually clean the raw JSONL file, then simply run the pipeline again.

    Args:
        jsonl_data (dict): A dictionary containing the JSONL objects.
        db_data (dict): A dictionary containing KKLC characters with IDs and page numbers.
        save_path (str): A path to save the merged db (as JSON).
        logging (bool): Whether or not to log the merge statistics.

    Returns:
        None
    """

    jsonl_keys = set(jsonl_data.keys())
    db_keys = set(source_data.keys())
    
    # find matches, extras, and missing, and sort on ID
    matches = sorted(jsonl_keys.intersection(db_keys), 
                    key=lambda x: int(source_data[x]['id']))
    extras = jsonl_keys - db_keys
    missing = db_keys - jsonl_keys
    
    # merge
    merged_data = {}
    for kanji in matches:
        merged_data[kanji] = {
            **jsonl_data[kanji],
            'id': source_data[kanji]['id'],
            'page': source_data[kanji]['page']
        }
    
    # store dict
    results = {
        'merged': merged_data,
        'stats': {
            'total_matches': len(matches),
            'total_extras': len(extras),
            'total_missing': len(missing)
        },
        'extras': {k: jsonl_data[k] for k in extras},
        'missing': {k: source_data[k] for k in missing}
    }

    # logging
    if logging:
        print(f"\nStatistics:")
        print(f"Total matches: {results['stats']['total_matches']}")
        print(f"Total extras (only in JSONL): {results['stats']['total_extras']}")
        print(f"Total missing (only in DB.js): {results['stats']['total_missing']}")

    # writing merged db to file
    with open(save_merged, 'w', encoding='utf-8') as f:
        json.dump(results['merged'], f, ensure_ascii=False, indent=2)

    # writing extras to file
    if save_extras:
        with open(save_extras, 'w', encoding='utf-8') as f:
            json.dump(results['extras'], f, ensure_ascii=False, indent=2)

    # writing missing entries to file
    if save_missing:
        with open(save_missing, 'w', encoding='utf-8') as f:
            json.dump(results['missing'], f, ensure_ascii=False, indent=2)

    return 

def enrich_kanji_data(input_file: str, delay: float=0.05) -> None:
    """
    Enrich kanji data with readings and JLPT level from kanjiapi.dev.
    Overwrites the input file in place.
    
    Args:
        input_file (str): Path to input JSON file
        delay (float): Delay between API calls in seconds
    
    Returns:
        None
    """
    
    # load kanji
    with open(input_file, 'r', encoding='utf-8') as f:
        kanji_data = json.load(f)
    
    # loop through thee kanji
    for kanji in kanji_data.keys():
        try:
            # hit kanjiapi.kanji
            response = requests.get(f"https://kanjiapi.dev/v1/kanji/{kanji}")
            if response.status_code == 200:
                api_data = response.json()
                
                # append new fields
                kanji_data[kanji].update({
                    'jlpt': api_data.get('jlpt'),
                    'kun_readings': api_data.get('kun_readings'),
                    'on_readings': api_data.get('on_readings')
                })
                print(f"Processing {kanji} (ID: {kanji_data[kanji].get('id')})...")
            else:
                print(f"Error with {kanji}: {response.status_code}")
            
            # attempted kindess to the API
            sleep(delay)

        except Exception as e:
            print(f"Failed on {kanji}: {str(e)}")
            break
    
    # overwrite input file
    print("Done!")
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(kanji_data, f, ensure_ascii=False, indent=2)


def run_data_cleaning_pipeline(
    ocr_jsonl: str,
    source_db: str,
    output_path: str,
    merge_logging: bool = True,
    merge_extras_path: str = None,
    merge_missing_path: str = None,
    run_api: bool = True,
    api_delay: float = 0,
):
    """
    Runs the data cleaning pipeline (...)
    Requires a source JSON (`data/db.js`) containing all KKLC entries with IDs and page numbers.
    This file acts as a "source of truth", as OCR can be messy (wrong kanji transcribed).

    IMPORTANT! Manually clean the raw JSONL file, then simply run the pipeline again until issues are resolved.

    Args:
        ocr_jsonl (str): Path to the OCR outputs in JSONL format (not cleaned).
        source_db (str): Path to the "source of truth" JSON file.
        output_path (str): Where to save the final output. 
        merge_logging (bool): Whether or not to log merge results to the console (recommended).
        merge_extras_path (str): Where to save the extra entries (OCR side) found in the merge.
            Defaults to None, which means extras won't be written anywhere.
        merge_missing_path (str): Where to save the missing entries (OCR side) found in the merge.
            Defaults to None, which means missing entries won't be written anywhere.
        run_api (bool): Whether or not to run the API calls to kanjiapi.dev.
        api_delay (float): How long to wait between each API call to kanjiapi.dev.
            Defaults to 0 (there is a delay in processing anyway).
        
    Returns:
        None
    """

    start = time.time()
    print("Cleaning the raw OCR data...")
    clean_jsonl(ocr_jsonl, "clean.jsonl")

    print("Merging with reference DB...")
    merge_jsonl_and_source(
        jsonl_data=read_jsonl("clean.jsonl"), 
        source_data=read_source_db(source_db), 
        save_merged=output_path,
        save_extras=merge_extras_path,
        save_missing=merge_missing_path,
        logging=merge_logging
    )
    os.remove("clean.jsonl")

    if run_api:
        print("Done! Quering kanjiapi.dev for readings...")
        enrich_kanji_data(output_path, api_delay)

    end = time.time()
    print(f"Done in {(end - start)/60:0.03f} minutes!")

    return

