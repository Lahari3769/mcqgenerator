import requests
from bs4 import BeautifulSoup
from services.image_service import image_to_text
import tempfile
import os

def scrape_url_to_text(url: str) -> str:
    """
    Scrape text and images from a URL.
    Images are processed with OCR and added to text.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # -------- Extract text --------
    texts = []
    for p in soup.find_all("p"):
        t = p.get_text().strip()
        if t:
            texts.append(t)
    
    # -------- Extract images --------
    images_text = []
    for img_tag in soup.find_all("img"):
        img_url = img_tag.get("src")
        if img_url:
            try:
                if not img_url.startswith("http"):
                    img_url = requests.compat.urljoin(url, img_url)
                img_resp = requests.get(img_url, stream=True, timeout=10)
                img_resp.raise_for_status()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                    tmp_img.write(img_resp.content)
                    tmp_path = tmp_img.name
                ocr_text = image_to_text(tmp_path)
                if ocr_text.strip():
                    images_text.append(ocr_text.strip())
                os.remove(tmp_path)
            except Exception:
                continue

    all_text = "\n".join(texts + images_text)
    return all_text.strip()