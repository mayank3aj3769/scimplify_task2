from fastapi import APIRouter, Depends, File, UploadFile
from typing import List
from auth import get_current_user
from models import pictures_collection

router = APIRouter()

@router.post("/upload-picture")
async def upload_picture(file: UploadFile = File(...), user = Depends(get_current_user)):
    file_location = f"pictures/{file.filename}"
    print(file_location)
    with open(file_location, "wb") as file_object:
        file_object.write(file.file.read())
    print(f"file object : {file_object}")
    await pictures_collection.insert_one({"email": user["email"], "file_path": file_location})
    return {"info": "file uploaded successfully", "file_path": file_location}

@router.get("/view-picture", response_model=List[str])
async def view_pictures():
    pictures = await pictures_collection.find().to_list(100)
    file_paths = [picture["file_path"] for picture in pictures]
    return file_paths
