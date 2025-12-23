from setuptools import setup, find_packages

setup(
    name="mcq-generator",
    version="0.1.0",
    description="Modular MCQ Generator using OCR and LLMs",
    author="Majeti Lahari",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "huggingface-hub>=0.20.0",
        "transformers>=4.40.0",
        "torch>=2.0.0",
        "pillow>=10.0.0",
        "opencv-python>=4.9.0",
        "pytesseract>=0.3.10",
        "numpy>=1.24.0"
    ],
)