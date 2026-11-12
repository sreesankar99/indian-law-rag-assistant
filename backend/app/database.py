from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# HARDCODED FOR NOW TO BYPASS THE IMPORT ERROR
DATABASE_URL = "postgresql+psycopg2://postgres:170599@localhost:5432/indianlaw"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()