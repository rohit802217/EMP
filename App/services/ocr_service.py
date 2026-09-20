"""
Text extraction from uploaded answer sheets / answer keys
(image or PDF), via OCR (Tesseract through pytesseract) with a
native-text-layer fast path for text-based PDFs.
"""

from io import BytesIO
import streamlit as st
from PIL import Image

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PdfReader = None
    PYPDF_AVAILABLE = False

try:
    from pdf2image import convert_from_bytes
    PDF_IMAGE_AVAILABLE = True
except ImportError:
    convert_from_bytes = None
    PDF_IMAGE_AVAILABLE = False

PDF_AVAILABLE = PYPDF_AVAILABLE or PDF_IMAGE_AVAILABLE


def preprocess_image(img):
    """Grayscale, upscale small images, and threshold for cleaner OCR."""
    img = img.convert("L")

    width, height = img.size
    if width < 1600:
        scale = 1600 / width
        img = img.resize((int(width * scale), int(height * scale)))

    img = img.point(lambda p: 0 if p < 180 else 255)
    return img


def extract_text_from_file(uploaded_file):
    """Extract raw text from an uploaded image or PDF."""
    if not OCR_AVAILABLE:
        st.error("pytesseract is not installed.\n\nRun:\npip install pytesseract")
        return ""

    filename = uploaded_file.name.lower()
    text = ""

    if filename.endswith(".pdf"):
        pdf_bytes = uploaded_file.read()
        pages_needing_ocr = []

        # Pure-Python extraction for PDFs that already contain selectable text.
        if PYPDF_AVAILABLE:
            try:
                reader = PdfReader(BytesIO(pdf_bytes))
                for page_number, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        text += page_text + "\n"
                    else:
                        pages_needing_ocr.append(page_number + 1)
            except Exception:
                # If the text layer is malformed, OCR every rendered page.
                text = ""
                pages_needing_ocr = []

        # Render scanned/image-only PDFs with Poppler, then OCR with Tesseract.
        if not text.strip() or pages_needing_ocr:
            if not PDF_IMAGE_AVAILABLE:
                st.error("Scanned-PDF support requires `pdf2image` and Poppler.")
                return text
            try:
                if pages_needing_ocr and text.strip():
                    for page_number in pages_needing_ocr:
                        images = convert_from_bytes(
                            pdf_bytes, dpi=250, first_page=page_number,
                            last_page=page_number, fmt="png",
                        )
                        for img in images:
                            text += pytesseract.image_to_string(
                                preprocess_image(img), config="--psm 6"
                            ) + "\n"
                else:
                    for img in convert_from_bytes(pdf_bytes, dpi=250, fmt="png"):
                        text += pytesseract.image_to_string(
                            preprocess_image(img), config="--psm 6"
                        ) + "\n"
            except Exception as exc:
                st.error(f"Could not render the PDF for OCR: {exc}")
                return text
    else:
        img = Image.open(uploaded_file)
        img = preprocess_image(img)
        text = pytesseract.image_to_string(img, config="--psm 6")

    return text
