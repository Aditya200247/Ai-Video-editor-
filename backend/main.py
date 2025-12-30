from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import endpoints

from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="AI Director-in-a-Box API")

# Ensure uploads dir exists
os.makedirs("backend/uploads", exist_ok=True)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (uploaded and rendered videos)
app.mount("/static", StaticFiles(directory="backend/uploads"), name="static")

# Ensure music dir exists
os.makedirs("backend/uploads/music", exist_ok=True)


app.include_router(endpoints.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "AI Director Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
