# app/schemas.py
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from datetime import datetime

class GenerateRequest(BaseModel):
    url: HttpUrl

class QuizItem(BaseModel):
    question: str
    options: List[str]
    answer: str
    explanation: Optional[str]
    difficulty: Optional[str]

class QuizResponse(BaseModel):
    id: int
    url: str
    title: Optional[str]
    summary: Optional[str]
    sections: Optional[List[str]]
    quiz: List[QuizItem]
    related_topics: Optional[List[str]]
    created_at: datetime
