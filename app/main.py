from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.predict import router as predict_router
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

app = FastAPI(
    title="ML Prediction API",
    version="0.1.0",
)

# Enable CORS for any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # <-- allows all origins
    allow_credentials=True,
    allow_methods=["*"],            # <-- allows all methods (GET, POST, etc)
    allow_headers=["*"],            # <-- allows all headers
)

# Mount your prediction router
app.include_router(predict_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello, this is your ML API!"}
