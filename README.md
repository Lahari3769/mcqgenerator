📄 LLM-Powered Multimodal Quiz & Assessment Generator
A Streamlit-based end-to-end multimodal GenAI application that generates and evaluates quizzes from text, documents, images, audio, and video using a unified LLM-driven pipeline.

The app supports:
📄 PDF & Word documents
🖼 Images (OCR)
🔊 Audio files (speech-to-text)
🌐 Web pages
✍️ Direct text input
🚀 Features

PDF text extraction using PyMuPDF
DOCX parsing with python-docx
Image OCR via OpenCV + Tesseract
Audio transcription using OpenAI Whisper
Web scraping with BeautifulSoup
LLM integration using Hugging Face Inference API
Interactive UI powered by Streamlit

🧰 Tech Stack
Frontend/UI: Streamlit
OCR: Tesseract, OpenCV, Pillow
Speech-to-Text: OpenAI Whisper, FFmpeg
Document Parsing: PyMuPDF, python-docx
Web Scraping: BeautifulSoup
LLMs: Hugging Face Hub
Environment Management: python-dotenv


🛠 Installation Guide
1️⃣ Prerequisites
Python 3.9+
pip
Git

Verify Python:
python --version


2️⃣ Clone the Repository
git clone <your-repository-url>
cd <your-project-folder>


3️⃣ Create & Activate a Virtual Environment (Recommended)
macOS / Linux
python -m venv venv
source venv/bin/activate

Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate


4️⃣ Install Python Dependencies
pip install --upgrade pip
pip install -r requirements.txt


5️⃣ Install System Dependencies
Some features require additional system tools.
🔊 FFmpeg (Required for Audio Processing & Whisper)

macOS
brew install ffmpeg

Windows
Download: https://ffmpeg.org/download.html

Add FFmpeg to your system PATH
Verify:
ffmpeg -version

🔍 Tesseract OCR (Required for Image-to-Text)
macOS
brew install tesseract

Windows
Download: https://github.com/UB-Mannheim/tesseract/wiki

Add Tesseract to your system PATH
Verify:
tesseract --version

🔐 Environment Variables
Create a .env file in the project root:
HUGGINGFACEHUB_API_TOKEN=your_api_key_here


▶️ Running the App
Start the Streamlit application:
streamlit run app.py

Then open your browser at:
http://localhost:8501