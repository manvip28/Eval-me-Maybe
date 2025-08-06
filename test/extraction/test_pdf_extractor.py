import os
import shutil
import tempfile
import unittest
from PIL import Image, ImageDraw
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pdf_extractor import PDFExtractor  # Update path as needed

class TestPDFExtractor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create temp directory
        cls.test_dir = tempfile.mkdtemp()
        print(f"\n📂 Created temp directory: {cls.test_dir}")
        
        # Create test PDFs
        cls.sample_pdf = os.path.join(cls.test_dir, "sample.pdf")
        cls.image_pdf = os.path.join(cls.test_dir, "with_images.pdf")
        cls._create_sample_pdf()
        cls._create_pdf_with_images()
    
    @classmethod
    def tearDownClass(cls):
        # Cleanup temp directory
        shutil.rmtree(cls.test_dir)
        print(f"🧹 Cleaned up temp directory: {cls.test_dir}")
    
    @classmethod
    def _create_sample_pdf(cls):
        """Create a simple text-based PDF"""
        c = canvas.Canvas(cls.sample_pdf, pagesize=letter)
        
        # Page 1
        c.drawString(100, 700, "1.1 Introduction")
        c.drawString(100, 680, "This is the introduction content.")
        c.drawString(100, 660, "It has multiple lines.")
        
        # Page 2
        c.showPage()
        c.drawString(100, 700, "2.1 Main Content")
        c.drawString(100, 680, "This is the main body text.")
        c.drawString(100, 660, "See Figure 1 for reference.")
        
        c.save()
        print(f"📄 Created sample PDF: {cls.sample_pdf}")
    
    @classmethod
    def _create_pdf_with_images(cls):
        """Create PDF with embedded images"""
        # Create a test image
        img_path = os.path.join(cls.test_dir, "test_img.png")
        img = Image.new('RGB', (100, 100), color='red')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Test Image", fill='white')
        img.save(img_path)
        
        # Create PDF with image
        c = canvas.Canvas(cls.image_pdf, pagesize=letter)
        c.drawImage(img_path, 100, 600, width=100, height=100)
        c.drawString(100, 580, "3.1 Image Section")
        c.drawString(100, 560, "This page contains an image.")
        c.drawString(100, 540, "See the diagram above.")
        c.save()
        print(f"🖼️ Created PDF with images: {cls.image_pdf}")
    
    def test_text_extraction(self):
        """Test basic text extraction"""
        print("\n🔍 Testing text extraction...")
        extractor = PDFExtractor(self.sample_pdf)
        content = extractor.extract_content()
        
        # Verify topics
        topics = content["topics"]
        self.assertIn("1.1 Introduction", topics)
        self.assertIn("2.1 Main Content", topics)
        
        # Verify content
        intro_text = topics["1.1 Introduction"]["text"]
        self.assertIn("introduction content", intro_text)
        
        print("✅ Text extraction passed")
    
    def test_chunking(self):
        """Test text chunking functionality"""
        print("\n🔍 Testing text chunking...")
        extractor = PDFExtractor(self.sample_pdf)
        content = extractor.extract_content()
        topics = content["topics"]
        
        # Verify chunks
        intro_chunks = topics["1.1 Introduction"]["chunks"]
        self.assertGreater(len(intro_chunks), 0)
        
        main_content = topics["2.1 Main Content"]["chunks"]
        self.assertGreater(len(main_content), 0)
        
        print("✅ Text chunking passed")
    
    def test_image_extraction(self):
        """Test image extraction"""
        print("\n🔍 Testing image extraction...")
        extractor = PDFExtractor(self.image_pdf)
        content = extractor.extract_content()
        topics = content["topics"]
        
        # Verify images
        images = topics["3.1 Image Section"]["images"]
        self.assertEqual(len(images), 1)
        self.assertTrue(os.path.exists(images[0]))
        
        # Verify image-text association
        chunks = topics["3.1 Image Section"]["chunks"]
        has_images = any(chunk["contains_images"] for chunk in chunks.values())
        self.assertTrue(has_images)
        
        print("✅ Image extraction passed")
    
    def test_image_in_text_detection(self):
        """Test detection of image references in text"""
        print("\n🔍 Testing image reference detection...")
        extractor = PDFExtractor(self.image_pdf)
        
        # Should detect image references
        self.assertTrue(extractor._chunk_has_images("See figure 1.2", []))
        self.assertTrue(extractor._chunk_has_images("Refer to Table 3", []))
        
        # Should not detect images
        self.assertFalse(extractor._chunk_has_images("Regular text", []))
        self.assertFalse(extractor._chunk_has_images("", []))
        
        print("✅ Image reference detection passed")

if __name__ == "__main__":
    print("Starting PDF Extractor Tests")
    print("============================")
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(TestPDFExtractor('test_text_extraction'))
    suite.addTest(TestPDFExtractor('test_chunking'))
    suite.addTest(TestPDFExtractor('test_image_extraction'))
    suite.addTest(TestPDFExtractor('test_image_in_text_detection'))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\nTest Summary")
    print("============")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ All tests passed successfully!")
    else:
        print("❌ Some tests failed. See details above.")