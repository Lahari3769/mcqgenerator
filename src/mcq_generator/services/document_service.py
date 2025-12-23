import os
import tempfile
from typing import List

import fitz 
from docx import Document
from PIL import Image

from services.image_service import image_to_text
from services.text_service import text_input_to_text

import streamlit as st


# ==============================
# PDF Processing
# ==============================
def extract_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)

    extracted_texts: List[str] = []

    for page in doc:
        # ---- Extract text ----
        text = page.get_text().strip()
        if text:
            extracted_texts.append(text_input_to_text(text))

        # ---- Extract images ----
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                tmp_img.write(image_bytes)
                img_path = tmp_img.name

            ocr_text = image_to_text(img_path)
            if ocr_text:
                extracted_texts.append(ocr_text)

            os.remove(img_path)

    return "\n".join(extracted_texts)


# ==============================
# DOCX Processing
# ==============================
def extract_from_docx(file_path: str) -> str:
    document = Document(file_path)

    extracted_texts: List[str] = []

    # ---- Extract text ----
    for para in document.paragraphs:
        if para.text.strip():
            extracted_texts.append(text_input_to_text(para.text))

    # ---- Extract images ----
    for rel in document.part._rels.values():
        if "image" in rel.target_ref:
            image_part = rel.target_part
            image_bytes = image_part.blob

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                tmp_img.write(image_bytes)
                img_path = tmp_img.name

            ocr_text = image_to_text(img_path)
            if ocr_text:
                extracted_texts.append(ocr_text)

            os.remove(img_path)

    return "\n".join(extracted_texts)


# ==============================
# Main Entry
# ==============================
import os

def document_to_text(file_path: str, original_filename: str) -> str:
    name = original_filename.lower()

    if ".pdf" in name:
        return extract_from_pdf(file_path)

    elif ".docx" in name or name.endswith(".doc"):
        return extract_from_docx(file_path)

    else:
        raise ValueError(f"Unsupported document type: {original_filename}")