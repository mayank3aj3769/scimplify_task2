from fastapi import FastAPI, Depends, HTTPException, Form, UploadFile, File, Request, Response
from fastapi.responses import RedirectResponse
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import List
import os
import secrets

from pymongo import MongoClient
from urllib.parse import quote_plus

app = FastAPI()

# MongoDB connection
username = quote_plus('rmayank331')
password = quote_plus('M@yank123')
uri = f"mongodb+srv://{username}:{password}@scimplifi.zd8d2lf.mongodb.net/?retryWrites=true&w=majority&appName=scimplifi"
client = AsyncIOMotorClient(uri)
db = client["scimplify"]
users_collection = db["users"]
pictures_collection=db["pictures"]

# Security configurations
SECRET = secrets.token_urlsafe(32)  # Generate a secure random secret key
manager = LoginManager(SECRET, token_url="/api/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    email: str
    password: str

# Picture model
class Picture(BaseModel):
    email: str
    file_path: str

async def load_user(email: str):
    user = await users_collection.find_one({"email": email})
    return user


@manager.user_loader()
async def user_loader(email: str):
    return await load_user(email)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)



@app.post("/api/signup")
async def signup(email: str = Form(...), password: str = Form(...)):
    user = await users_collection.find_one({"email": email})
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    #hashed_password = get_password_hash(password)
    await users_collection.insert_one({"email": email, "password": password})
    return {"msg": "User registered successfully"}

@app.post("/api/login")
async def login(response: Response, email: str = Form(...), password: str = Form(...)):
    user = await load_user(email)
    #user = await users_collection.find_one({"email": email})
    # if not user or not verify_password(password, user["password"]):
    if not user or password != user["password"]:
        raise InvalidCredentialsException
    access_token = manager.create_access_token(data={"sub": email})
    manager.set_cookie(response, access_token)
    return {"msg": "Login successful"}

@app.get("/api/logout")
def logout(response: Response):
    manager.set_cookie(response, "")
    return {"msg": "Logout successful"}

async def get_current_user(request: Request):
    token = request.cookies.get('access-token')
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized: No access token provided")

    try:
        data = await manager.get_current_user(token)
        email = data['email']
    except Exception as e:
        print(f"Token decode error: {e}")
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid token")

    user = await load_user(email)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized: User not found")

    return user

@app.post("/api/upload-picture")
async def upload_picture(request: Request, file: UploadFile = File(...), user: User = Depends(get_current_user)):
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
