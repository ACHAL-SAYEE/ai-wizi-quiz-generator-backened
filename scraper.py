# app/scraper.py
import httpx
from bs4 import BeautifulSoup
from utils import extract_text_from_html, extract_sections_and_headings, clean_whitespace
from typing import Dict, Any

async def fetch_url_html(url: str, timeout=10):
    async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": "DeepKlarityBot/1.0"}) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.text

async def scrape_wikipedia(url: str) -> Dict[str, Any]:
    html = await fetch_url_html(url)
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find('h1', id='firstHeading')
    title = clean_whitespace(title_tag.get_text()) if title_tag else None

    extracted_text = extract_text_from_html(html)
    sections = extract_sections_and_headings(html)

    # basic summary: first paragraph(s)
    summary_tag = soup.select_one("div.mw-parser-output > p")
    summary = clean_whitespace(summary_tag.get_text()) if summary_tag else None

    return {
        "title": title,
        "summary": summary,
        "raw_html": html,
        "extracted_text": extracted_text,
        "sections": sections
    }
