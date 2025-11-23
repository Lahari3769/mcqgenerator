from setuptools import setup, find_packages

setup(
    name='mcqgen',
    version='0.0.1',
    author='majeti lahari',
    author_email='majetilahari@gmail.com',
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "langchain",
        "langchain-community",
        "streamlit",
        "python-dotenv",
        "PyPDF2",
        "pandas"
    ],
)
