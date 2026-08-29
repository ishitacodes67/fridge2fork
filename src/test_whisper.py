import whisper
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__)))
from query_router import full_pipeline

model = whisper.load_model("base")
result = model.transcribe("data/test_audio.m4a")
transcribed_query = result["text"].strip()

print(f"Transcribed query: {transcribed_query}")
full_pipeline(transcribed_query)