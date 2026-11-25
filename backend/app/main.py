from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import search

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Indian Law RAG API")

from fastapi.middleware.cors import CORSMiddleware
# Explicitly allow your Vercel frontend and localhost
origins = [
    "https://indian-law-rag-assistant-ftsi.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)

@app.get("/health")
def health():
    return {"status": "ok"}