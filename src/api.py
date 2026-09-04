import sys
import os
sys.path.append(os.path.dirname(__file__))

import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from query_router import full_pipeline, full_pipeline_from_photo

app = FastAPI(title="Fridge2Fork API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    include_nutrition: bool = False
    email_to: str = None


@app.get("/")
def home():
    return {"message": "Fridge2Fork API is running."}


@app.post("/recommend")
def recommend(request: QueryRequest):
    result = full_pipeline(
        request.query,
        include_nutrition=request.include_nutrition,
        email_to=request.email_to,
        return_meta=True,
    )
    return {"query": request.query, **result}


@app.post("/recommend-photo")
async def recommend_photo(
    file: UploadFile = File(...),
    include_nutrition: bool = Form(False),
    email_to: str = Form(None),
):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = full_pipeline_from_photo(
        temp_path,
        include_nutrition=include_nutrition,
        email_to=email_to,
        return_meta=True,
    )
    os.remove(temp_path)
    return result