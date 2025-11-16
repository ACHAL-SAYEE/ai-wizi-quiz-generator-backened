# app/models.py
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from db import Base

class QuizEntry(Base):
    __tablename__ = "quiz_entries"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(1000), unique=True, index=True, nullable=False)
    title = Column(String(512))
    summary = Column(Text)
    #key_entities = Column(JSON)      # {"people":[], "orgs":[], "locations":[]}
    sections = Column(JSON)          # list of section headings
    raw_html = Column(Text)          # optional: store scraped HTML
    extracted_text = Column(Text)    # cleaned article text used for LLM
    quiz = Column(JSON)              # generated quiz list
    related_topics = Column(JSON)    # suggested related topics
    cached = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
