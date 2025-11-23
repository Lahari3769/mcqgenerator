import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv

from mcqgen.utils import read_file, get_table_data
from mcqgen.logger import logging

# LangChain imports for Ollama
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain

# Load .env (not required unless you add keys later)
load_dotenv()

###############################################
### Choose the FREE model you want to use   ###
###############################################
# Recommended: "gemma2:9b" or "llama3.1:8b"
llm = Ollama(
    model="llama3.1:8b",
    temperature=0.3
)

###############################################
### QUIZ GENERATION PROMPT
###############################################
template = """
Text:{text}

You are an expert MCQ creator. Based on the above text, create {number} 
multiple-choice questions for {subject} students in a {tone} tone.

Rules:
- Questions must come ONLY from the text.
- NO repetitions.
- Give EXACT JSON following the format below:
### RESPONSE_JSON
{response_json}
"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=template
)

quiz_chain = LLMChain(
    llm=llm,
    prompt=quiz_generation_prompt,
    output_key="quiz",
    verbose=True
)

###############################################
### QUIZ REVIEW PROMPT
###############################################
evaluation_template = """
You are an expert English educator.
Given the following MCQ quiz for {subject} students:

Quiz MCQs:
{quiz}

In under 50 words:
- Evaluate complexity
- Suggest improvements
- Rewrite any questions if needed
"""

quiz_evaluation_prompt = PromptTemplate(
    input_variables=["subject", "quiz"],
    template=evaluation_template
)

review_chain = LLMChain(
    llm=llm,
    prompt=quiz_evaluation_prompt,
    output_key="review",
    verbose=True
)

###############################################
### SEQUENTIAL CHAIN (Generate → Review)
###############################################
generate_evaluate_chain = SequentialChain(
    chains=[quiz_chain, review_chain],
    input_variables=["text", "number", "subject", "tone", "response_json"],
    output_variables=["quiz", "review"],
    verbose=True
)
