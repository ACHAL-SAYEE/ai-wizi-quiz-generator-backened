# app/main.py
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from db import get_db, engine, Base
import scraper, llm, crud
from schemas import GenerateRequest, QuizResponse
from utils import clean_whitespace
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import asyncio
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Wiki Quiz Generator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all frontends (for development)
    allow_credentials=True,
    allow_methods=["*"],   # <-- ALLOW OPTIONS, POST, GET, etc.
    allow_headers=["*"],   # <-- ALLOW JSON headers
)
# Create tables (for quick start; in prod use alembic)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/generate", response_model=QuizResponse)
async def generate_quiz(req: GenerateRequest, db: AsyncSession = Depends(get_db)):
    url = str(req.url)
    # 1. Check cache / existing
    existing = await crud.get_entry_by_url(db, url)
    if existing:
        # return existing quickly
        return JSONResponse(status_code=200, content={
            "id": existing.id,
            "url": existing.url,
            "title": existing.title,
            "summary": existing.summary,
            "key_entities": existing.key_entities,
            "sections": existing.sections,
            "quiz": existing.quiz,
            "related_topics": existing.related_topics
        })

    # 2. Scrape
    try:
        scraped = await scraper.scrape_wikipedia(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch or parse URL: {str(e)}")

    title = scraped.get("title")
    summary = scraped.get("summary")
    context = scraped.get("extracted_text", "")
    sections = scraped.get("sections", [])

    # 3. Optionally run a light NER via simple heuristics (could be improved with spaCy)
    # For brevity, we'll leave key_entities empty or rely on LLM to extract
    key_entities = {"people": [], "organizations": [], "locations": []}

    # 4. Call LLM to generate quiz
    try:
        model_out = await llm.generate_quiz_from_text(title, summary, sections, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")

    quiz = model_out.get("quiz", [])
    related_topics = model_out.get("related_topics", [])

    payload = {
        "url": url,
        "title": title,
        "summary": summary,
        "key_entities": key_entities,
        "sections": sections,
        "raw_html": scraped.get("raw_html"),
        "extracted_text": context,
        "quiz": quiz,
        "related_topics": related_topics
    }

    entry = await crud.create_or_update_entry(db, payload)
    return JSONResponse(status_code=200, content={
        "id": entry.id,
        "url": entry.url,
        "title": entry.title,
        "summary": entry.summary,
        "key_entities": entry.key_entities,
        "sections": entry.sections,
        "quiz": entry.quiz,
        "related_topics": entry.related_topics
    })

@app.get("/history", response_model=List[QuizResponse])
async def history(db: AsyncSession = Depends(get_db)):
    entries = await crud.get_all_entries(db)
    out = []
    for e in entries:
        out.append({
            "id": e.id,
            "url": e.url,
            "title": e.title,
            "summary": e.summary,
            "key_entities": e.key_entities,
            "sections": e.sections,
            "quiz": e.quiz,
            "related_topics": e.related_topics,
            "created_at":e.created_at
        })
    return out

@app.get("/detail/{entry_id}", response_model=QuizResponse)
async def detail(entry_id: int, db: AsyncSession = Depends(get_db)):
    e = await crud.get_entry_by_id(db, entry_id)
    if not e:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {
        "id": e.id,
        "url": e.url,
        "title": e.title,
        "summary": e.summary,
        "key_entities": e.key_entities,
        "sections": e.sections,
        "quiz": e.quiz,
        "related_topics": e.related_topics
    }

if __name__ == "__main__":
    uvicorn.run("main:app",  host="0.0.0.0", port=8000,reload=True)
