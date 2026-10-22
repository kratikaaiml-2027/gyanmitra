"""AI layer for GyanMitra. All AI calls live here, so you can swap the provider by editing only this file.

If no GEMINI_API_KEY is found, the app runs in DEMO MODE with built-in sample answers,
so the project always runs, even without internet or a key.
"""
import json
import os
import re

from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _get_key() -> str:
    try:
        import streamlit as st

        key = st.secrets.get("GEMINI_API_KEY")  # used on Streamlit Cloud
        if key:
            return key
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY", "")


def has_key() -> bool:
    return bool(_get_key())


def _generate(prompt: str) -> str:
    from google import genai

    client = genai.Client(api_key=_get_key())
    return client.models.generate_content(model=MODEL, contents=prompt).text


def explain(question: str, language: str, class_level: str, subject: str) -> str:
    if not has_key():
        return (
            f"**(Demo mode: no API key found)**\n\n"
            f"1. **One-line answer:** This is a sample reply for: *{question}*\n"
            f"2. **Step-by-step:** Add your GEMINI_API_KEY to get real explanations in {language}.\n"
            f"3. **Example:** Like a teacher explaining under a tree, one step at a time."
        )
    prompt = f"""You are a kind, patient tutor for a {class_level} student in rural India.
Subject: {subject}. Reply ONLY in {language}, using very simple words.
Answer using exactly this structure:
1. One-line answer
2. Step-by-step explanation
3. A simple example from everyday village or home life
Keep it short and age-appropriate.

Doubt: {question}"""
    return _generate(prompt)


DEMO_QUIZ = [
    {"question": "What is 1/2 + 1/2?", "options": ["1/4", "1", "2", "1/2"], "answer_index": 1,
     "hint": "Two halves make a whole.", "explanation": "1/2 + 1/2 = 2/2 = 1."},
    {"question": "Which fraction is the biggest?", "options": ["1/8", "1/4", "1/2", "1/3"], "answer_index": 2,
     "hint": "Smaller bottom number means bigger pieces.", "explanation": "1/2 is bigger than 1/3, 1/4 and 1/8."},
    {"question": "What is the top number of a fraction called?", "options": ["Denominator", "Numerator", "Whole", "Decimal"],
     "answer_index": 1, "hint": "It starts with N.", "explanation": "The top number is the numerator."},
    {"question": "3/3 is equal to?", "options": ["0", "3", "1", "1/3"], "answer_index": 2,
     "hint": "Same top and bottom.", "explanation": "3/3 = 1 whole."},
    {"question": "A pizza has 8 slices. You eat 2. What fraction did you eat?", "options": ["2/8", "8/2", "6/8", "1/8"],
     "answer_index": 0, "hint": "Eaten slices over total slices.", "explanation": "You ate 2 out of 8, which is 2/8."},
]


def make_quiz(topic: str, language: str, class_level: str, subject: str, weak: bool = False) -> list:
    if not has_key():
        return DEMO_QUIZ
    easier = " The student is weak in this topic, so keep the questions a little easier." if weak else ""
    prompt = f"""Create a 5-question multiple-choice quiz for a {class_level} student on "{topic}" ({subject}).
Language: {language}.{easier}
Return ONLY valid JSON, no extra text, in this format:
[{{"question": "...", "options": ["A", "B", "C", "D"], "answer_index": 0, "hint": "...", "explanation": "..."}}]"""
    raw = re.sub(r"```json|```", "", _generate(prompt)).strip()
    return json.loads(raw)
