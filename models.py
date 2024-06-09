from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus

# MongoDB connection
username = quote_plus('rmayank331')
password = quote_plus('M@yank123')
uri = f"mongodb+srv://{username}:{password}@scimplifi.zd8d2lf.mongodb.net/?retryWrites=true&w=majority&appName=scimplifi"
client = AsyncIOMotorClient(uri)
db = client["scimplify"]
users_collection = db["users"]
pictures_collection = db["pictures"]

async def load_user(email: str):
    user = await users_collection.find_one({"email": email})
    return user
