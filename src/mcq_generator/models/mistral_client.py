from huggingface_hub import InferenceClient
import os
import dotenv

dotenv.load_dotenv()

client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
)