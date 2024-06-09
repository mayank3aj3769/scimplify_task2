from fastapi import APIRouter, Depends, HTTPException, Form, Request, Response
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from passlib.context import CryptContext
import secrets
from models import load_user, users_collection

router = APIRouter()

# Security configurations
SECRET = secrets.token_urlsafe(32)  # Generate a secure random secret key
manager = LoginManager(SECRET, token_url="/api/login")
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto") ## to encrypt password in 

@manager.user_loader()
async def user_loader(email: str):
    return await load_user(email)

def get_password_hash(password):
    return pwd_context.hash(password) ## password hashing 

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def get_current_user(request: Request):
    token = request.cookies.get('access-token') ## extracts session_id from the current session
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

@router.post("/signup")
async def signup(email: str = Form(...), password: str = Form(...)): ## Input is accepted as form data 
    user = await users_collection.find_one({"email": email}) # checks if the user is already registered
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(password) ## Hashes the password , so that it is not stored as plain text
    await users_collection.insert_one({"email": email, "password": hashed_password})
    return {"msg": "User registered successfully"}

@router.post("/login")
async def login(response: Response, email: str = Form(...), password: str = Form(...)):
    user = await load_user(email)
    if not user or not verify_password(password, user['password']):
        raise InvalidCredentialsException 
    access_token = manager.create_access_token(data={"sub": email}) ## creates a session , mapped to the users email
    manager.set_cookie(response, access_token) 
    return {"msg": "Login successful"}

@router.get("/logout")
async def logout(response: Response):
    manager.set_cookie(response, "") # resets session value to null upon logging out.
    return {"msg": "Logout successful"}
