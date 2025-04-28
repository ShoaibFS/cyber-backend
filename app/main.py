# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# your prediction router
from app.routers.predict import router as predict_router

# load environment variables from .env
load_dotenv()

# get your frontend URL from env (fall back to the known Static Web App host)
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "https://brave-wave-0171c9a03.6.azurestaticapps.net"
)

app = FastAPI(
    title="ML Prediction API",
    version="0.1.0",
)

# enable CORS for only your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount your prediction endpoints under /api
app.include_router(predict_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello, this is your ML API!"}
