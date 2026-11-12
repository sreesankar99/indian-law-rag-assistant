from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, Index
from pgvector.sqlalchemy import Vector
from app.database import Base

class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. "bns_103"
    act = Column(String(20), index=True, nullable=False)  # BNS | IPC | CONSTITUTION
    chapter_no = Column(String(20), nullable=True)
    chapter_title = Column(Text, nullable=True)
    section_no = Column(String(20), index=True, nullable=False)
    section_title = Column(Text, nullable=False)
    text_en = Column(Text, nullable=False)
    plain_summary_en = Column(Text, nullable=True)
    keywords = Column(JSON, default=list)
    ipc_corresponding = Column(String(50), nullable=True)
    
    # We add the embedding column directly here for simplicity (pgvector)
    embedding = Column(Vector(3072)) 

    __table_args__ = (
        Index("ix_sections_act_section", "act", "section_no", unique=True),
    )

class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(String(50), index=True) # Matches Section.section_id
    language = Column(String(10), index=True, nullable=False)
    title = Column(Text, nullable=True)
    text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    source = Column(String(20), nullable=False, default="machine")