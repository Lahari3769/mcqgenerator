import re
import json

def clean_json_text(text: str) -> str:
    """
    Clean common artifacts in LLM JSON output.
    - Fix trailing commas
    - Remove unexpected characters
    """
    # Remove trailing commas before } or ]
    text = re.sub(r',\s*([}\]])', r'\1', text)
    # Replace non-printable characters with space
    text = re.sub(r'[^\x20-\x7E\n\t{}[\]:,"]+', ' ', text)
    return text.strip()

def extract_json(text: str) -> dict:
    """
    Try to extract valid JSON from LLM output.
    """
    text = text.strip()

    # First, try direct parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: clean text and retry
    clean_text = clean_json_text(text)
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        pass

    # Last fallback: try single quotes -> double quotes
    clean_text = clean_text.replace("'", '"')
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        pass

    raise ValueError("No valid JSON could be parsed from LLM response")
