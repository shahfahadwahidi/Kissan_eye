import fitz  # PyMuPDF
import os
import google.generativeai as genai
import PIL.Image

def load_pdfs_from_folder(folder_path: str) -> tuple:
    """
    Scans every .pdf file in the given folder using PyMuPDF (fitz).
    Extracts all text from every page of every PDF.
    Returns (concatenated_text, pdf_count, pdf_names).
    """
    concatenated_text = ""
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return "", 0, []

    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    
    print(f"Loaded {len(pdf_files)} PDFs.")
    
    for filename in pdf_files:
        file_path = os.path.join(folder_path, filename)
        try:
            doc = fitz.open(file_path)
            for page in doc:
                concatenated_text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            
    return concatenated_text, len(pdf_files), pdf_files

def extract_text_from_images(
    folder_path: str = "data/images/",
    api_key: str = ""
) -> str:
    """
    Sends each image in data/images/ to Gemini Vision
    and asks it to extract all text from the brochure.
    Returns combined extracted text from all images.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return ""

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    all_text = ""
    image_extensions = (".jpg", ".jpeg", ".png", ".jfif", ".webp")

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(image_extensions):
            img_path = os.path.join(folder_path, filename)
            try:
                img = PIL.Image.open(img_path)
                response = model.generate_content([
                    img,
                    """This is an agricultural brochure in Urdu.
                    Extract ALL text from this image exactly as written.
                    Do not translate. Do not summarize.
                    Return the raw extracted text only."""
                ])
                extracted = response.text
                all_text += f"\n\n--- {filename} (image OCR) ---\n"
                all_text += extracted
                print(f"[SUCCESS] Image text extracted: {filename} "
                      f"({len(extracted)} chars)")

            except Exception as e:
                print(f"[ERROR] Failed to extract {filename}: {e}")

    return all_text

def truncate_context(text: str, max_chars: int = 80000) -> str:
    """
    Truncates the text to max_chars to stay inside Gemini's context window.
    Returns the truncated string.
    """
    return text[:max_chars]
