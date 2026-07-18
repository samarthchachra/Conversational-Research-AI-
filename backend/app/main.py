from fastapi import FastAPI
from app.api.router import api_router
app = FastAPI(title="Research AI Assisstant")

app.include_router(api_router)

@app.get("/")
def home():
    return {"message":"Research AI backend is running"}
