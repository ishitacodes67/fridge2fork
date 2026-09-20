import sys
import os
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from query_router_lite import full_pipeline_lite as full_pipeline

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
# import sys
# import os
# sys.path.append(os.path.dirname(__file__))

# import shutil
# from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from query_router import full_pipeline, full_pipeline_from_photo
# from database import init_db, get_db, User, FavoriteRecipe
# from auth import hash_password, verify_password, create_access_token, decode_access_token
# import whisper

# app = FastAPI(title="Fridge2Fork API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# init_db()
# whisper_model = whisper.load_model("base")
# security = HTTPBearer()


# def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
#     payload = decode_access_token(credentials.credentials)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     user = db.query(User).filter(User.email == payload.get("sub")).first()
#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")
#     return user


# class QueryRequest(BaseModel):
#     query: str
#     include_nutrition: bool = False
#     email_to: str = None


# class SignupRequest(BaseModel):
#     email: str
#     password: str


# class LoginRequest(BaseModel):
#     email: str
#     password: str


# class SaveFavoriteRequest(BaseModel):
#     query: str
#     recipe_text: str


# @app.get("/")
# def home():
#     return {"message": "Fridge2Fork API is running locally (full pipeline)."}


# @app.post("/recommend")
# def recommend(request: QueryRequest):
#     result = full_pipeline(
#         request.query,
#         include_nutrition=request.include_nutrition,
#         email_to=request.email_to,
#         return_meta=True,
#     )
#     return {"query": request.query, **result}


# @app.post("/recommend-voice")
# async def recommend_voice(
#     file: UploadFile = File(...),
#     include_nutrition: bool = Form(False),
#     email_to: str = Form(None),
# ):
#     temp_path = f"temp_{file.filename}"
#     with open(temp_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     result = whisper_model.transcribe(temp_path)
#     transcribed_query = result["text"].strip()
#     os.remove(temp_path)

#     response = full_pipeline(
#         transcribed_query,
#         include_nutrition=include_nutrition,
#         email_to=email_to,
#         return_meta=True,
#     )
#     return {"transcribed_query": transcribed_query, **response}


# @app.post("/recommend-photo")
# async def recommend_photo(
#     file: UploadFile = File(...),
#     include_nutrition: bool = Form(False),
#     email_to: str = Form(None),
# ):
#     temp_path = f"temp_{file.filename}"
#     with open(temp_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     result = full_pipeline_from_photo(
#         temp_path,
#         include_nutrition=include_nutrition,
#         email_to=email_to,
#         return_meta=True,
#     )
#     os.remove(temp_path)
#     return result


# @app.post("/signup")
# def signup(request: SignupRequest, db: Session = Depends(get_db)):
#     existing = db.query(User).filter(User.email == request.email).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     user = User(email=request.email, hashed_password=hash_password(request.password))
#     db.add(user)
#     db.commit()
#     return {"message": "Account created successfully"}


# @app.post("/login")
# def login(request: LoginRequest, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == request.email).first()
#     if not user or not verify_password(request.password, user.hashed_password):
#         raise HTTPException(status_code=401, detail="Incorrect email or password")
#     token = create_access_token({"sub": user.email})
#     return {"access_token": token, "token_type": "bearer"}


# @app.post("/favorites")
# def save_favorite(request: SaveFavoriteRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     favorite = FavoriteRecipe(user_id=current_user.id, query=request.query, recipe_text=request.recipe_text)
#     db.add(favorite)
#     db.commit()
#     return {"message": "Recipe saved to favorites"}


# @app.get("/favorites")
# def get_favorites(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     favorites = db.query(FavoriteRecipe).filter(FavoriteRecipe.user_id == current_user.id).all()
#     return [{"id": f.id, "query": f.query, "recipe_text": f.recipe_text, "saved_at": f.saved_at} for f in favorites]