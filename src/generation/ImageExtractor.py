import os
import re
import fitz  # PyMuPDF
from PIL import Image
from typing import List, Dict, Optional, Tuple
import io
from datetime import datetime
import pytesseract
from collections import defaultdict
import logging

class TextbookImageExtractor:
    def __init__(self, pdf_path: str, min_image_size: Tuple[int, int] = (50, 50)):
        """
        Initialize with enhanced error handling and real-world considerations
        
        Args:
            pdf_path: Path to the textbook PDF file
            min_image_size: Minimum (width, height) for images to be processed
        """
        self.pdf_path = pdf_path
        self.min_image_size = min_image_size
        self.logger = self._setup_logger()
        
        # Validate PDF exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")
            
        # Create output directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.image_dir = os.path.join(
            os.path.dirname(pdf_path), 
            f"extracted_images_{timestamp}"
        )
        os.makedirs(self.image_dir, exist_ok=True)
        
        try:
            self.image_index = self._index_textbook_images()
        except Exception as e:
            self.logger.error(f"Failed to index textbook images: {str(e)}")
            raise

    def _setup_logger(self):
        """Configure logging for the extractor"""
        logger = logging.getLogger("TextbookImageExtractor")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    def _index_textbook_images(self) -> Dict[str, Dict]:
        image_index = defaultdict(dict)
        try:
            doc = fitz.open(self.pdf_path)
        except Exception as e:
            self.logger.error(f"Failed to open PDF: {str(e)}")
            raise

        for page_num in range(len(doc)):
            try:
                page = doc.load_page(page_num)
                pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


            # Render the page as an image (scanned PDF compatibility)
                pix = page.get_pixmap(dpi=300)
                image_bytes = pix.tobytes("png")
                img_path = os.path.join(self.image_dir, f"page_{page_num + 1}.png")

                with open(img_path, "wb") as f:
                    f.write(image_bytes)
                
                ocr_text = self._extract_image_text(image_bytes)
                detected_topic = self._detect_topic(ocr_text)
                print("ocr_text:", ocr_text)
                print("detected_topic:", detected_topic)

                image_index[img_path] = {
                        "page": page_num + 1,
                        "context": self._clean_text(ocr_text),
                        "position": None,
                        "dimensions": (pix.width, pix.height),
                        "ocr_text": ocr_text,
                        "topic": detected_topic,
                        "is_diagram": False  # Hard to detect in scanned mode
                    }

            except Exception as page_error:
                self.logger.error(f"Failed to process page {page_num + 1}: {str(page_error)}")
                continue

        doc.close()
        return image_index


    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
            
        # Remove excessive whitespace and normalize
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _is_diagram(self, rect: fitz.Rect, page: fitz.Page) -> bool:
        """
        Heuristic to determine if image is likely a diagram (vs photo/illustration)
        """
        # Check if image has nearby diagram-related text
        nearby_text = page.get_text("text", clip=rect + (-20, -20, 20, 20))
        diagram_keywords = ["diagram", "figure", "chart", "graph", "illustration"]
        return any(keyword in nearby_text.lower() for keyword in diagram_keywords)

    def _extract_image_text(self, image_bytes: bytes) -> str:
        """OCR with enhanced error handling"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Preprocess image for better OCR
            image = image.convert('L')  # Grayscale
            return pytesseract.image_to_string(image)
        except Exception as e:
            self.logger.warning(f"OCR failed: {str(e)}")
            return ""

    def _detect_topic(self, text: str) -> Optional[str]:
        """Improved topic detection with hierarchy awareness"""
        if not text:
            return None
            
        # Look for section headers (numbered or all caps)
        patterns = [
            r'^(?P<topic>(?:[0-9]+\.)+\s+[^\n]+)',  # Numbered sections
            r'^(?P<topic>[A-Z][A-Z0-9\s]+[A-Z])',    # All caps headings
            r'^(?P<topic>Chapter\s+\d+:\s+.+)'       # Chapter headings
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return self._clean_text(match.group("topic"))
                
        return None

    def find_images_for_topic(self, topic: str, 
                            num_images: int = 2,
                            min_score: float = 0.3) -> List[Dict]:
        """
        Enhanced image search with relevance scoring
        
        Args:
            topic: Search query
            num_images: Max images to return
            min_score: Minimum relevance score (0-1)
        """
        relevant_images = []
        topic_lower = topic.lower()
        topic_words = set(topic_lower.split())
        
        for img_path, meta in self.image_index.items():
            if not meta['topic']:
                continue
                
            # Score based on multiple factors
            topic_match = topic_lower in meta['topic'].lower()
            context_score = self._calculate_similarity(topic_words, meta['context'])
            ocr_score = self._calculate_similarity(topic_words, meta['ocr_text'])
            
            # Weighted score (prioritize topic matches)
            score = (
                0.6 * float(topic_match) + 
                0.3 * context_score + 
                0.1 * ocr_score
            )
            
            if score >= min_score:
                relevant_images.append({
                    "path": img_path,
                    "page": meta['page'],
                    "context": meta['context'],
                    "score": round(score, 2),
                    "is_diagram": meta['is_diagram']
                })
        
        # Sort by score and diagram status (diagrams first)
        relevant_images.sort(
            key=lambda x: (-x['score'], -x['is_diagram'])
        )
        return relevant_images[:num_images]

    def _calculate_similarity(self, query_words: set, text: str) -> float:
        """Calculate word overlap similarity score"""
        if not text:
            return 0.0
            
        text_words = set(text.lower().split())
        common = query_words & text_words
        return len(common) / len(query_words) if query_words else 0.0

    def get_image_with_context(self, topic: str) -> str:
        """Generate comprehensive markdown output"""
        images = self.find_images_for_topic(topic)
        if not images:
            return f"## No relevant images found for '{topic}'"
            
        output = [f"## Images related to '{topic}'\n"]
        
        for img in images:
            img_name = os.path.basename(img['path'])
            diagram_flag = " (Diagram)" if img['is_diagram'] else ""
            
            output.extend([
                f"![{topic}{diagram_flag}]({img_name})",
                f"**Page {img['page']}** - Score: {img['score']:.2f}",
                f"*Context:* {img['context'][:200]}{'...' if len(img['context']) > 200 else ''}",
                "---"
            ])
        
        return "\n\n".join(output)