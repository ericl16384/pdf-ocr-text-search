import fitz  # PyMuPDF
import pytesseract
import json
import concurrent.futures
import os

import sys

# CONFIGURATION
assert len(sys.argv) == 2
PDF_PATH = sys.argv[1]
OUTPUT_JSON = f"pdf_ocr_{sys.argv[1]}.json"
# If tesseract is not in your PATH, uncomment and set the line below:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_page(page_num, pdf_path):
    """Converts a single page to an image and performs OCR."""
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_num)
        # Higher DPI (300) improves OCR accuracy for small engineering text
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
        
        # Convert PixMap to image and OCR
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(pix.tobytes()))
        text = pytesseract.image_to_string(img)
        
        return page_num + 1, text.strip()
    except Exception as e:
        return page_num + 1, f"Error: {str(e)}"

def build_index():
    doc = fitz.open(PDF_PATH)
    num_pages = len(doc)
    doc.close()
    
    print(f"Indexing {num_pages} pages using multiprocessing...")
    full_index = {}

    # Use ProcessPoolExecutor to run OCR in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(ocr_page, i, PDF_PATH) for i in range(num_pages)]
        
        for future in concurrent.futures.as_completed(futures):
            pg, text = future.result()
            full_index[pg] = text
            if pg % 50 == 0:
                print(f"Processed {pg}/{num_pages} pages...")

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(full_index, f, indent=4)
    
    print(f"Indexing complete! Data saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    build_index()