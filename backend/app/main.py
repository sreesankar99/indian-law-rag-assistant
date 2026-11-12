from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import search

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Indian Law RAG API")

# Allow all origins for development (Swagger, Frontend, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your frontend URL
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)

@app.get("/health")
def health():
    return {"status": "ok"}