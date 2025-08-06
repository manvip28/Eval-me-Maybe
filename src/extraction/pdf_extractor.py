# # src/extraction/pdf_extractor.py
# import pdfplumber
# import re
# from collections import OrderedDict
# def is_topic_header(text):
#     pattern = r"^\d+(\.\d+)*\s+.+$"
#     return bool(re.match(pattern, text.strip()))

# def clean_header(text):
#     """
#     Cleans section headers like '1.1.   Cloud Computing' → '1.1 Cloud Computing'
#     """
#     text = text.strip()

#     # Fix common issue: '1.1.' → '1.1'
#     if re.match(r"^\d+(\.\d+)*\.\s", text):
#         text = re.sub(r"^(\d+(?:\.\d+)*)(\.)\s+", r"\1 ", text)
#     else:
#         text = re.sub(r"\s+", " ", text)  # remove weird extra spaces

#     # Final regex to parse clean header
#     match = re.match(r"^(\d+(?:\.\d+)*)(?:\.)?\s+(.+)$", text)
#     if match:
#         section_number, title = match.groups()
#         return f"{section_number} {title.strip()}"
#     return text
# def extract_topics(pdf_path):
#     with pdfplumber.open(pdf_path) as pdf:
#         content = {}
#         current_topic = ""
#         for page in pdf.pages:
#             text = page.extract_text()
#             # Add logic to detect topic headers (regex/position-based)
#             for tex in text.split('\n'):
#                 if is_topic_header(tex):
#                     current_topic = clean_header(tex)
#                     content[current_topic] = ""
#                 elif current_topic:
#                     content[current_topic] += tex + "\n"
#     return OrderedDict(content)  # Maintain section order

# # import pdfplumber
# # import io
# # import os
# # from PIL import Image
# # from collections import OrderedDict
# # from typing import Dict, List, Tuple
# # import re

# # class PDFExtractor:
# #     def __init__(self, pdf_path: str):
# #         self.pdf_path = pdf_path
# #         base_dir = os.path.dirname(os.path.abspath(pdf_path)) or "."
# #         self.image_dir = os.path.join(base_dir, "extracted_images")
# #         os.makedirs(self.image_dir, exist_ok=True)
# #         print(f"Images will be saved to: {self.image_dir}")

# #     def extract_content(self) -> Dict[str, Dict]:
# #         """Fixed and improved content extraction"""
# #         content = OrderedDict()
# #         current_topic = None
        
# #         with pdfplumber.open(self.pdf_path) as pdf:
# #             for page_num, page in enumerate(pdf.pages, start=1):
# #                 print(f"Processing page {page_num}/{len(pdf.pages)}")
                
# #                 # Extract images
# #                 page_images = self._extract_page_images(page, page_num)
                
# #                 # Extract text
# #                 page_text = page.extract_text() or ""
                
# #                 # Process each line of text
# #                 for line in page_text.split('\n'):
# #                     line = line.strip()
# #                     if not line:
# #                         continue
                    
# #                     # Check if this line is a topic header
# #                     if self._is_topic_header(line):
# #                         current_topic = self._clean_header(line)
# #                         if current_topic not in content:
# #                             content[current_topic] = {
# #                                 "text": "",
# #                                 "images": [],
# #                                 "pages": [page_num],
# #                                 "chunks": OrderedDict()
# #                             }
# #                         else:
# #                             # Topic spans multiple pages
# #                             content[current_topic]["pages"].append(page_num)
# #                         continue
                    
# #                     # Add content to current topic
# #                     if current_topic:
# #                         content[current_topic]["text"] += line + "\n"
                
# #                 # Process chunks for the page
# #                 if current_topic:
# #                     chunks = self._chunk_text(content[current_topic]["text"])
# #                     for chunk_id, chunk_text in enumerate(chunks, start=1):
# #                         chunk_key = f"chunk_{chunk_id}"
# #                         if chunk_key not in content[current_topic]["chunks"]:
# #                             content[current_topic]["chunks"][chunk_key] = {
# #                                 "text": chunk_text,
# #                                 "contains_images": self._chunk_has_images(chunk_text, page_images)
# #                             }
                    
# #                     # Associate images with topic
# #                     content[current_topic]["images"].extend(
# #                         img for img in page_images 
# #                         if self._image_belongs_to_topic(img, content[current_topic]["text"])
# #                     )
        
# #         return content

# #     def _extract_page_images(self, page, page_num: int) -> List[str]:
# #         """Improved image extraction with error handling"""
# #         images = []
# #         if hasattr(page, 'images'):
# #             for img_index, img in enumerate(page.images, start=1):
# #                 try:
# #                     img_data = img['stream'].get_data()
# #                     if not img_data:
# #                         continue
                        
# #                     img_obj = Image.open(io.BytesIO(img_data))
# #                     img_path = os.path.join(self.image_dir, f"page{page_num}_img{img_index}.png")
# #                     img_obj.save(img_path)
# #                     images.append(img_path)
# #                     print(f"  - Extracted image: {os.path.basename(img_path)}")
# #                 except Exception as e:
# #                     print(f"  Error saving image: {e}")
# #         return images

# #     def _is_topic_header(self, line: str) -> bool:
# #         """Check if line is a topic header"""
# #         patterns = [
# #             r'^\d+(\.\d+)*\s+[A-Z]',  # 1.1 Introduction
# #             r'^CHAPTER\s+\d+',          # CHAPTER 1
# #             r'^[A-Z]{3,}\s*$',          # ALL CAPS HEADERS
# #             r'^Section\s+\d+',          # Section 1
# #             r'^[IVXLCDM]+\.'            # Roman numerals: I., II., etc.
# #         ]
# #         return any(re.match(p, line) for p in patterns)

# #     def _clean_header(self, header: str) -> str:
# #         """Clean and normalize section headers"""
# #         # Remove numbering prefixes (e.g., "1.1. ")
# #         header = re.sub(r'^(\d+\.)+\s*', "", header)
# #         # Remove trailing punctuation
# #         header = header.strip(" :.-")
# #         # Title case normalization
# #         return " ".join(word for word in header.split())

# #     def _chunk_text(self, text: str, max_chunk_size: int = 1000) -> List[str]:
# #         """Better chunking that preserves paragraphs"""
# #         chunks = []
# #         current_chunk = ""
        
# #         # Split by paragraphs first
# #         paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
# #         for para in paragraphs:
# #             # If paragraph is too big, split into sentences
# #             if len(para) > max_chunk_size:
# #                 sentences = re.split(r'(?<=[.!?])\s+', para)
# #                 for sentence in sentences:
# #                     if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
# #                         chunks.append(current_chunk.strip())
# #                         current_chunk = ""
# #                     current_chunk += sentence + " "
# #             else:
# #                 if len(current_chunk) + len(para) > max_chunk_size and current_chunk:
# #                     chunks.append(current_chunk.strip())
# #                     current_chunk = ""
# #                 current_chunk += para + "\n\n"
        
# #         if current_chunk:
# #             chunks.append(current_chunk.strip())
            
# #         return chunks

# #     def _chunk_has_images(self, chunk_text: str, page_images: List[str]) -> bool:
# #         """Check if chunk references images"""
# #         if not page_images:
# #             return False
# #         image_keywords = ["figure", "diagram", "image", "illustration", "table", "photo"]
# #         return any(keyword in chunk_text.lower() for keyword in image_keywords)

# #     def _image_belongs_to_topic(self, image_path: str, topic_text: str) -> bool:
# #         """Improved image-topic association"""
# #         img_name = os.path.basename(image_path)
        
# #         # Try to match figure numbers
# #         fig_match = re.search(r'fig(\d+)', img_name, re.IGNORECASE)
# #         if fig_match and f"figure {fig_match.group(1)}" in topic_text.lower():
# #             return True
            
# #         # Match based on common keywords
# #         return any(
# #             kw in img_name.lower() or kw in topic_text.lower()
# #             for kw in ["fig", "diagram", "illustration", "table", "image"]
# #         )


# # # Usage example
# # if __name__ == "__main__":
# #     import sys
# #     if len(sys.argv) < 2:
# #         print("Usage: python pdf_extractor.py <pdf-file>")
# #         sys.exit(1)
    
# #     extractor = PDFExtractor(sys.argv[1])
# #     content = extractor.extract_content()
    
# #     # Print results
# #     print("\nExtracted Content:")
# #     for topic, data in content.items():
# #         print(f"\nTopic: {topic}")
# #         print(f"Pages: {data['pages']}")
# #         print(f"Text: {data['text'][:100]}...")
# #         print(f"Images: {len(data['images'])}")
# #         print(f"Chunks: {len(data['chunks'])}")
        
# #         for chunk_id, chunk in data['chunks'].items():
# #             print(f"  - {chunk_id}: {chunk['text'][:50]}...")
import fitz
import pytesseract
import io
import os
import re
import json
from PIL import Image
from collections import OrderedDict
from datetime import datetime

# --- CONFIG ---
PDF_PATH = "path/to/your/textbook.pdf"  # Change this
OUTPUT_JSON = "extracted_content.json"
IMAGES_DIR = "images"
CHUNK_SIZE = 800  # Approximate max characters per chunk

os.makedirs(IMAGES_DIR, exist_ok=True)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update if needed

# --- HELPERS ---
def is_topic_header(text):
    return bool(re.match(r"^\d+(\.\d+)*\s+.+$", text.strip()))

def clean_header(text):
    text = re.sub(r'\s+', ' ', text.strip())
    match = re.match(r"^(\d+(?:\.\d+)*)(?:\.)?\s+(.+)$", text)
    if match:
        section, title = match.groups()
        return f"{section} {title.strip()}"
    return text

def ocr_page_image(pixmap_bytes):
    try:
        img = Image.open(io.BytesIO(pixmap_bytes)).convert("L")
        return pytesseract.image_to_string(img)
    except Exception as e:
        print(f"OCR failed: {e}")
        return ""

def extract_nonpage_images(page, page_num):
    paths = []
    for img_index, img_info in enumerate(page.get_images(full=True), start=1):
        try:
            xref = img_info[0]
            base_image = page.parent.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]
            path = os.path.join(IMAGES_DIR, f"page{page_num}_img{img_index}.{ext}")
            with open(path, "wb") as f:
                f.write(image_bytes)
            paths.append(path)
        except Exception as e:
            print(f"❌ Error extracting image: {e}")
    return paths

def chunk_text(text, max_len=CHUNK_SIZE):
    words = text.split()
    chunks = []
    current = []
    size = 0

    for word in words:
        if size + len(word) > max_len:
            chunks.append(" ".join(current))
            current = [word]
            size = len(word)
        else:
            current.append(word)
            size += len(word) + 1
    if current:
        chunks.append(" ".join(current))
    return chunks

def detect_relevant_images(images, text):
    keywords = ["figure", "chart", "diagram", "illustration", "graph", "table"]
    text_lower = text.lower()
    relevant = []
    for img in images:
        if any(kw in text_lower for kw in keywords):
            relevant.append({"path": img, "relevant": True})
        else:
            relevant.append({"path": img, "relevant": False})
    return relevant

# --- MAIN EXTRACTION ---
doc = fitz.open(PDF_PATH)
content = OrderedDict()
current_topic = None

for page_num, page in enumerate(doc, start=1):
    print(f"📄 Processing page {page_num}/{len(doc)}")
    ocr_text = ocr_page_image(page.get_pixmap(dpi=300).tobytes("png"))
    images = extract_nonpage_images(page, page_num)

    for line in ocr_text.split('\n'):
        line = line.strip()
        if is_topic_header(line):
            current_topic = clean_header(line)
            if current_topic not in content:
                content[current_topic] = {
                    "pages": [page_num],
                    "text": "",
                    "chunks": OrderedDict(),
                    "images": []
                }
        elif current_topic:
            content[current_topic]["text"] += line + " "

    if current_topic:
        content[current_topic]["pages"].append(page_num)
        content[current_topic]["images"].extend(images)

# --- POST PROCESSING ---
for topic, data in content.items():
    chunks = chunk_text(data["text"])
    for i, ch in enumerate(chunks, start=1):
        data["chunks"][f"chunk_{i}"] = {
            "text": ch,
            "contains_images": any(kw in ch.lower() for kw in ["figure", "diagram", "image", "table"])
        }

    # Attach image metadata
    data["images"] = detect_relevant_images(data["images"], data["text"])

# --- SAVE OUTPUT ---
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(content, f, indent=2, ensure_ascii=False)

print(f"\n✅ Extraction complete. JSON saved to `{OUTPUT_JSON}`")
