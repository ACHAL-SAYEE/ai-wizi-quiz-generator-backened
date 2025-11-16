# app/llm.py
import os
import json
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from prompts import QUIZ_PROMPT_TEMPLATE, RELATED_TOPIC_PROMPT
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
MAX_QUESTIONS = int(os.getenv("MAX_QUIZ_QUESTIONS", "7"))

# create LLM client via LangChain Google GenAI wrapper
def _create_llm():
    # LangChain's ChatGoogleGenerativeAI reads GOOGLE_API_KEY from env by default
    llm = ChatGoogleGenerativeAI(model=MODEL, api_key=GOOGLE_API_KEY, temperature=0.2)
    return llm

async def generate_quiz_from_text(title: str, summary: str, sections: List[str], context: str, n_questions: int = None) -> Dict[str, Any]:
    n = n_questions or MAX_QUESTIONS
    llm = _create_llm()
    prompt = QUIZ_PROMPT_TEMPLATE.format(n_questions=n, title=title or "", summary=summary or "", sections=sections, context=context[:120000])
    message = HumanMessage(content=prompt)
    resp = llm.invoke([message])  # synchronous-like; LangChain wrapper will handle
    # resp.content is often a list/dict depending on model; ensure string
    text = getattr(resp, "content", None)
    if isinstance(text, list):
        # sometimes returns list of messages; join
        text = " ".join([m.get("text", "") if isinstance(m, dict) else str(m) for m in text])
    text = str(text)

    # some models return JSON inside markdown. Attempt to extract first {...}
    import re
    m = re.search(r'(\{.*\})', text, re.S)
    if m:
        json_text = m.group(1)
    else:
        # fall back: try to parse whole text
        json_text = text

    try:
        parsed = json.loads(json_text)
    except Exception as e:
        # if parsing fails, wrap with minimal attempt
        # fallback: create a minimal JSON with one placeholder question
        parsed = {
            "quiz": [{
                "question": "Failed to parse model output. Here's a fallback question.",
                "options": ["A","B","C","D"],
                "answer": "A",
                "explanation": "Model output couldn't be parsed as JSON.",
                "difficulty": "medium"
            }],
            "related_topics": []
        }
    # ensure structure
    if "quiz" not in parsed:
        parsed["quiz"] = []
    if "related_topics" not in parsed:
        parsed["related_topics"] = []
    return parsed
