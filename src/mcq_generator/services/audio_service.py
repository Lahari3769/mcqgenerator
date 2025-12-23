import whisper

whisper_model = whisper.load_model("base")

def audio_to_text(audio_path: str) -> str:
    result = whisper_model.transcribe(audio_path)
    return result["text"].strip()