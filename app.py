from fastapi import FastAPI, Depends, HTTPException, Request, Response, status, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from pydantic import BaseModel
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
import os

import random
from pymongo import MongoClient
from urllib.parse import quote_plus

app = FastAPI()

username = quote_plus('rmayank331')
password = quote_plus('M@yank123')
uri = f"mongodb+srv://{username}:{password}@scimplifi.zd8d2lf.mongodb.net/?retryWrites=true&w=majority&appName=scimplifi"
client = AsyncIOMotorClient(uri)
db = client["scimplify"]
users_collection = db["users"]
#pictures_collection = db["pictures"]

sessions={}
# Security configurations
# SECRET = "your_secret_key"
# manager = LoginManager(SECRET, token_url="/api/login")
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    email: str
    password: str


async def load_user(email: str):
    user = await users_collection.find_one({"email": email})
    return user

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

@app.post("/api/signup")
async def signup(email: str = Form(...), password: str = Form(...)):
    user = await users_collection.find_one({"email": email})
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    #hashed_password = get_password_hash(password)
    await users_collection.insert_one({"email": email, "password": password})
    return {"msg": "User registered successfully"}

def create_session(email):
    session_id = len(sessions) + random.randint(0, 1000000)
    sessions[session_id] = email
    return session_id

@app.post("/api/login")
async def login(response: Response, email: str = Form(...), password: str = Form(...)):
    user = await load_user(email)
    if not user or password != user["password"]:
        raise InvalidCredentialsException
    
    session_id = create_session(email)
    return {"message": "Logged in successfully", "session_id": session_id}
   
def get_session_id(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id is None or int(session_id) not in sessions:
        raise HTTPException(status_code=401, detail="Invalid session ID")
    return int(session_id)


@app.get("/api/logout")
def logout(request: Request):
    session_id = request.get_session_id()
    # if session_id not in sessions:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    sessions.pop(session_id)
    return {"message": "Logged out successfully", "session_id": session_id}

@app.post("/api/upload-picture")
async def upload_picture(request: Request, file: UploadFile = File(...)):
    user = await manager.get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    file_location = f"pictures/{file.filename}"
    with open(file_location, "wb") as file_object:
        file_object.write(file.file.read())
    await pictures_collection.insert_one({"email": user["email"], "file_path": file_location})
    return {"info": "file uploaded successfully", "file_path": file_location}

@app.get("/api/view-picture", response_model=List[str])
async def view_pictures():
    pictures = await pictures_collection.find().to_list(100)
    file_paths = [picture["file_path"] for picture in pictures]
    return file_paths

# Create uploads directory if not exists
if not os.path.exists('pictures'):
    os.makedirs('pictures')

# Start the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
