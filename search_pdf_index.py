import json
import sys



def search_problem(index_file, query):
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
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
    assert len(sys.argv) == 3

    index_file = sys.argv[1]
    snippet = sys.argv[1]
    search_problem(index_file, snippet)
