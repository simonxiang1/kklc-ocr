import re

with open('outputs/page_output.txt', 'r') as content_file:
    text = content_file.read()

# Pattern that matches a kanji character followed by anything until the next kanji entry
entry_pattern = r'([一-龯])\n((?:(?![一-龯]\n)[\s\S])+)'

def parse_entries(text):
    entries = []
    matches = re.finditer(entry_pattern, text)
    
    for match in matches:
        kanji = match.group(1)
        content = match.group(2).strip()
        
        # Try to extract the keyword from the first line
        content_lines = content.split('\n')
        keyword = content_lines[0]
        remaining_content = '\n'.join(content_lines[1:]).strip()
        
        entries.append({
            'kanji': kanji,
            'keyword': keyword,
            'content': remaining_content
        })
    
    return entries

# Test it
entries = parse_entries(text)
for entry in entries:
    print("=== New Entry ===")
    print(f"Kanji: {entry['kanji']}")
    print(f"Keyword: {entry['keyword']}")
    print(f"Content: {entry['content'][:1000]}...")
    print()