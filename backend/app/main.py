from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import text
from app.api.router import api_router
from fastapi.middleware.cors import CORSMiddleware
import app.models
from app.database.database import engine, Base
from app.services.vectorstore.qdrantService import client as qdrant_client

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

@app.get("/health/deep")
def deep_health():
    status = {"database": "disconnected", "vector_store": "disconnected"}

    # 1. Ping Supabase Postgres to prevent the 7-day inactivity pause
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        status["database"] = "active"
    except Exception as e:
        status["database"] = f"error: {str(e)}"

    # 2. Ping Qdrant to prevent free cluster suspension
    try:
        qdrant_client.get_collections()
        status["vector_store"] = "active"
    except Exception as e:
        status["vector_store"] = f"error: {str(e)}"

    is_healthy = status["database"] == "active" and status["vector_store"] == "active"
    status["status"] = "healthy" if is_healthy else "degraded"
    return status

app.include_router(api_router)
