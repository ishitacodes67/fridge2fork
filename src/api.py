import sys
import os
sys.path.append(os.path.dirname(__file__))

import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from query_router import full_pipeline, full_pipeline_from_photo
import whisper

app = FastAPI(title="Fridge2Fork API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

whisper_model = whisper.load_model("base")


class QueryRequest(BaseModel):
    query: str
    include_nutrition: bool = False
    email_to: str = None


@app.get("/")
def home():
    return {"message": "Fridge2Fork API is running."}


@app.post("/recommend")
def recommend(request: QueryRequest):
    response = full_pipeline(
        request.query,
        include_nutrition=request.include_nutrition,
        email_to=request.email_to,
    )
    return {"query": request.query, "response": response}


@app.post("/recommend-voice")
async def recommend_voice(
    file: UploadFile = File(...),
    include_nutrition: bool = Form(False),
    email_to: str = Form(None),
):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = whisper_model.transcribe(temp_path)
    transcribed_query = result["text"].strip()
    os.remove(temp_path)

    response = full_pipeline(
        transcribed_query,
        include_nutrition=include_nutrition,
        email_to=email_to,
    )
    return {"transcribed_query": transcribed_query, "response": response}


@app.post("/recommend-photo")
async def recommend_photo(
    file: UploadFile = File(...),
    include_nutrition: bool = Form(False),
    email_to: str = Form(None),
):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    response = full_pipeline_from_photo(
        temp_path,
        include_nutrition=include_nutrition,
        email_to=email_to,
    )
    os.remove(temp_path)
    return {"response": response}