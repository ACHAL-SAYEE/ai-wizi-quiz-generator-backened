# app/utils.py
import re
from bs4 import BeautifulSoup
from datetime import datetime
def clean_whitespace(text: str) -> str:
    return re.sub(r'\s+', ' ', (text or "")).strip()

def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # remove tables, nav, references, scripts, styles
    for selector in ['table', 'script', 'style', 'sup', 'footer', 'nav', 'aside']:
        for el in soup.select(selector):
            el.decompose()
    # keep paragraphs and headings
    texts = []
    for tag in soup.find_all(['h1','h2','h3','h4','p','li']):
        if tag.get_text():
            texts.append(tag.get_text(separator=' ', strip=True))
    return clean_whitespace("\n\n".join(texts))

def extract_sections_and_headings(html: str):
    soup = BeautifulSoup(html, "html.parser")
    headings = []
    for tag in soup.find_all(['h2','h3']):
        text = tag.get_text(separator=' ', strip=True)
        if text:
            # remove [edit] suffix sometimes present
            text = re.sub(r'\[edit\]$', '', text).strip()
            headings.append(text)
    return headings

def current_time():
    return datetime.now().strftime("%H:%M:%S")

