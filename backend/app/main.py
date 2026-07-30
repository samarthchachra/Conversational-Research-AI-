from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.router import api_router
from fastapi.middleware.cors import CORSMiddleware
import app.models
from app.database.database import engine, Base

app = FastAPI(title="Research AI Assisstant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(
        bind=engine
    )

    print("Database tables verified.")

    yield

@app.get("/")
def home():
    return {"message":"Research AI backend is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

app.include_router(api_router)