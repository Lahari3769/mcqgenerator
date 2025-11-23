import os
import PyPDF2
import json
import traceback
import re

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfFileReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text

        except Exception:
            raise Exception("error reading the PDF file")

    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    else:
        raise Exception("unsupported file format only pdf and text file supported")


def extract_json(text):
    """
    Extracts the first valid JSON object from the model output.
    Removes extra text, markdown, etc.
    """
    try:
        # Find first {...} block using a regex
        match = re.search(r'\{[\s\S]*\}', text)
        if not match:
            return None
        json_str = match.group(0)

        # Try loading JSON
        return json.loads(json_str)

    except Exception:
        return None


def get_table_data(quiz_str):
    try:
        quiz_dict = extract_json(quiz_str)
        if quiz_dict is None:
            print("❌ JSON extraction failed")
            return False

        quiz_table_data = []

        # Iterate extracted JSON
        for key, value in quiz_dict.items():
            mcq = value.get("mcq", "")
            options = " || ".join(
                [
                    f"{option}-> {option_value}"
                    for option, option_value in value.get("options", {}).items()
                ]
            )
            correct = value.get("correct", "")

            quiz_table_data.append(
                {"MCQ": mcq, "Choices": options, "Correct": correct}
            )

        return quiz_table_data

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False
