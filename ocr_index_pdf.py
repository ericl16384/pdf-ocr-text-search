import fitz  # pip PyMuPDF
import pytesseract
import json
import concurrent.futures
import os
import sys

# If tesseract is not in your PATH, uncomment and set the line below:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

TESSERACT_WARNING_TEXTS = {
    r"Error: tesseract is not installed or it's not in your PATH. See README file for more information.",
    r"Error: C:\\Program Files\\Tesseract-OCR\\tesseract.exe is not installed or it's not in your PATH. See README file for more information.",
}

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

def build_index(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    doc.close()
    
    print(f"Indexing {num_pages} pages using multiprocessing...")
    full_index = {}

    # Use ProcessPoolExecutor to run OCR in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(ocr_page, i, pdf_path) for i in range(num_pages)]
        
        for future in concurrent.futures.as_completed(futures):
            pg, text = future.result()
            full_index[pg] = text
            if text in TESSERACT_WARNING_TEXTS:
                print(text)
            if pg % 10 == 0:
                print(f"Processed {pg}/{num_pages} pages...")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(full_index, f, indent=4)
    
    print(f"Indexing complete! Data saved to {output_path}")

if __name__ == "__main__":
    assert len(sys.argv) == 2
    pdf_path = sys.argv[1]
    output_path = f"index_{sys.argv[1]}.json"
    build_index(pdf_path, output_path)
    