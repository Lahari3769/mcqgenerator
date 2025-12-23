import json
import math

from utils.json_utils import extract_json
from models.mistral_client import client

# ==============================
# Config
# ==============================
MAX_TOKENS_PER_CALL = 4000         
TOKEN_THRESHOLD = 6000              
CHUNK_OVERLAP = 200                 # preserve context

# ==============================
# RESPONSE SCHEMA
# ==============================

RESPONSE_JSON = {
    "1": {
        "mcq": "multiple choice question",
        "options": {
            "a": "choice here",
            "b": "choice here",
            "c": "choice here",
            "d": "choice here",
        },
        "correct": ["correct answer(s)"],
        "explanation": "Explanation of correct answer(s)",
    },
    "2": {
        "mcq": "multiple choice question",
        "options": {
            "a": "choice here",
            "b": "choice here",
            "c": "choice here",
            "d": "choice here",
        },
        "correct": ["correct answer(s)"],
        "explanation": "Explanation of correct answer(s)",
    },
    "3": {
        "mcq": "multiple choice question",
        "options": {
            "a": "choice here",
            "b": "choice here",
            "c": "choice here",
            "d": "choice here",
        },
        "correct": ["correct answer(s)"],
        "explanation": "Explanation of correct answer(s)",
    },
}

# ==============================
# Utility Functions
# ==============================
def estimate_tokens(text: str) -> int:
    """
    Approximate token count without tokenizer dependency.
    ~4 chars per token is safe for English.
    """
    return max(1, len(text) // 4)


def chunk_text(text: str, max_tokens: int, overlap: int):
    max_chars = max_tokens * 4
    overlap_chars = overlap * 4

    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end - overlap_chars

    return chunks


def normalize_mcq_schema(mcqs: dict) -> dict:
    normalized = {}

    for q_id, q in mcqs.items():
        options = q.get("options", {})
        correct = q.get("correct", [])

        # Ensure correct is a list
        if isinstance(correct, str):
            correct = [c.strip() for c in correct.split(",")]

        # If elements are option texts, map them to keys
        mapped_correct = []
        for c in correct:
            for k, v in options.items():
                if c.strip().lower() == k.lower() or c.strip().lower() == v.lower():
                    mapped_correct.append(k)
                    break

        if not mapped_correct and options:
            mapped_correct = [list(options.keys())[0]]

        q["correct"] = mapped_correct
        normalized[str(q_id)] = q

    return normalized

# ==============================
# Core Generation
# ==============================
def generate_mcq_from_text(text: str, num_questions: int):
    prompt = f"""
    Text:
    {text}

    You are an expert MCQ Generator.

    Create exactly {num_questions} multiple choice questions with atleast one question having more than one correct answer

    RULES:
    - Questions must be based ONLY on the provided text
    - No repetition of questions
    - Each question must have 4 options (a, b, c, d)
    - Each question can have one or more correct answers
    - Provide a clear explanation for each correct answer
    - The field "correct" MUST ALWAYS be a JSON ARRAY of option keys
    - If only one option is correct, return a list with one element
    - Otherwise, if multiple options are correct, return a list with all correct elements
    - Use ONLY keys from the "options" object
    - Output ONLY valid JSON
    - No markdown, no extra text

    FORMAT (follow this strictly):
    {json.dumps(RESPONSE_JSON, indent=2)}
    """

    tokens_per_question = 200
    max_tokens = max(512, num_questions * tokens_per_question)

    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=max_tokens
    )

    raw_json = extract_json(response.choices[0].message.content)
    return normalize_mcq_schema(raw_json)

# ==============================
# Main Entry Point
# ==============================
def generate_mcq(text: str, num_questions: int = 5):
    """
    Intelligent MCQ generator:
    - Direct generation for short text
    - Chunked generation for long text
    - Deduplicates questions
    - Enforces schema integrity
    """

    total_tokens = estimate_tokens(text)

    # --------------------------
    # Case 1: Small input
    # --------------------------
    if total_tokens <= TOKEN_THRESHOLD:
        return generate_mcq_from_text(text, num_questions)

    # --------------------------
    # Case 2: Large input
    # --------------------------
    chunks = chunk_text(
        text,
        max_tokens=MAX_TOKENS_PER_CALL,
        overlap=CHUNK_OVERLAP
    )

    questions_per_chunk = max(1, math.ceil(num_questions / len(chunks)))

    final_mcqs = {}
    seen_questions = set()
    q_counter = 1

    for chunk in chunks:
        if q_counter > num_questions:
            break

        chunk_mcqs = generate_mcq_from_text(chunk, questions_per_chunk)

        for _, q in chunk_mcqs.items():
            question_text = q["mcq"].strip().lower()

            if question_text in seen_questions:
                continue

            final_mcqs[str(q_counter)] = q
            seen_questions.add(question_text)
            q_counter += 1

            if q_counter > num_questions:
                break

    return final_mcqs