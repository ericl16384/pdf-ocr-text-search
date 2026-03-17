import json

import sys

assert len(sys.argv) == 2
INDEX_FILE = sys.argv[1]

def search_problem(query):
    try:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Index file not found. Please run ocr_index_pdf.py first.")
        return

    query = query.lower().strip()
    results = []

    for page_num, content in data.items():
        if query in content.lower():
            results.append(page_num)

    if results:
        print(f"\nMatch found! '{query[:30]}...' is on Page(s): {', '.join(results)}")
    else:
        print("\nNo exact match found. Try a shorter, unique snippet of text.")

if __name__ == "__main__":
    snippet = input("Enter the text snippet to search for: ")
    search_problem(snippet)