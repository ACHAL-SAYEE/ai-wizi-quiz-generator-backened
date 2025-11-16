# app/prompts.py
# Prompt templates used for the LLM via LangChain.

QUIZ_PROMPT_TEMPLATE = """
You are a helpful, precise quiz-generator assistant.
Given the following extracted Wikipedia article text and its metadata, produce a quiz with {n_questions} multiple-choice questions.

Article title: {title}
Article summary: {summary}
Sections: {sections}

Article text (relevant paragraphs):
{context}

Requirements:
- Output JSON only.
- Provide a top-level object with keys: "quiz" (list), "related_topics" (list).
- Each quiz item must have:
  - "question": short question text (no more than 120 chars)
  - "options": list of 4 plausible options (A-D)
  - "answer": exact option text (must match one option)
  - "explanation": 1-2 sentence explanation grounded in the article text (cite section where possible)
  - "difficulty": one of ["easy","medium","hard"]
- Make questions fact-based and grounded in the provided content (minimize hallucination).
- Mix question difficulties: ~40% easy, ~40% medium, ~20% hard.
- Under "related_topics" return 3-6 relevant Wikipedia topics (short phrases).

Return only valid JSON that can be parsed by a JSON parser.
"""

RELATED_TOPIC_PROMPT = """
Given the article title and summary, list 5 related Wikipedia topics (short phrases) for further reading.
Return JSON: {"related_topics": ["...","..."]}
"""
