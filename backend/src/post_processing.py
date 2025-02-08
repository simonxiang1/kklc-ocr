import json
import re

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

def read_dbjs(file_path: str) -> dict:
    """
    Reads in DB.js file and returns dict with kanji as key.

    Args:
        file_path (str): Path to the DB.js file.

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

def merge_jsonl_and_db(
        jsonl_data: str,
        db_data: str,
        save_path: str = None,
        logging: bool = True
    ) -> None:
    """
    Merges the JSONL and db.js files and saves it to a specified path. Returns None.
    Here the db.js is the reference DB, but we keep the "keyword" field from the JSONL file.

    Args:
        jsonl_data (str): A path to the JSONL db.
        db_data (str): A path to the reference db.
        save_path (str): A path to save the merged db (as JSON).
        logging (bool): Whether or not to log the merge statistics.

    Returns:
        None
    """

    jsonl_keys = set(jsonl_data.keys())
    db_keys = set(db_data.keys())
    
    # find matches, extras, and missing, and sort on ID
    matches = sorted(jsonl_keys.intersection(db_keys), 
                    key=lambda x: int(db_data[x]['id']))
    extras = jsonl_keys - db_keys
    missing = db_keys - jsonl_keys
    
    # merge
    merged_data = {}
    for kanji in matches:
        merged_data[kanji] = {
            **jsonl_data[kanji],
            'id': db_data[kanji]['id'],
            'page': db_data[kanji]['page']
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
        'missing': {k: db_data[k] for k in missing}
    }

    # logging
    if logging:
        print(f"\nStatistics:")
        print(f"Total matches: {results['stats']['total_matches']}")
        print(f"Total extras (only in JSONL): {results['stats']['total_extras']}")
        print(f"Total missing (only in DB.js): {results['stats']['total_missing']}")

    # writing to file
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(results['merged'], f, ensure_ascii=False, indent=2)

    return