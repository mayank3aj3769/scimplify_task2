from fastapi import FastAPI
import os
from auth import router as auth_router
from upload import router as upload_router

app = FastAPI()

# Include the routers
app.include_router(auth_router, prefix="/api")
app.include_router(upload_router, prefix="/api")

# Create uploads directory if not exists
if not os.path.exists('pictures'):
    os.makedirs('pictures')

# Start the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
