import cv2, pytesseract, re
from PIL import Image

def image_to_text(image_path: str) -> str:
    img = cv2.imread(image_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    custom_config = r"--oem 3 --psm 6"

    text = pytesseract.image_to_string(
        gray,
        config=custom_config
    )

    raw_text = text.strip()
    clean_text = clean_ocr_text(raw_text)

    return clean_text

def clean_ocr_text(text: str) -> str:
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # remove weird chars
    text = re.sub(r'\n{2,}', '\n', text)       # extra newlines
    text = re.sub(r'\s{2,}', ' ', text)        # extra spaces
    return text.strip()