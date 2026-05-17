import json
import logging

import aiohttp

from config import config

logger = logging.getLogger(__name__)

_BASE_URL = (
    "https://generativelanguage.googleapis.com"
    "/v1beta/models/gemini-2.0-flash-exp:generateContent"
)

_SYSTEM = """Ты — преподаватель арабского языка для русскоязычных студентов.

Правила:
- Отвечай только на русском языке
- Арабские слова пиши в формате: арабский (транскрипция) — перевод
- Объясняй просто, без академической перегрузки, максимум 5 предложений
- Если не уверен — честно говори об этом
- При исламских терминах — будь точен и аккуратен
- Не придумывай правила, которых не существует
- Если вопрос не связан с арабским языком — вежливо откажись"""


async def _generate(text: str, max_tokens: int = 400, temperature: float = 0.5) -> str:
    url = f"{_BASE_URL}?key={config.GEMINI_API_KEY}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": f"{_SYSTEM}\n\n{text}"}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
        },
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise Exception(f"HTTP {resp.status}: {data}")
            return data["candidates"][0]["content"]["parts"][0]["text"]


async def ask(question: str) -> str:
    try:
        return await _generate(question, max_tokens=400, temperature=0.5)
    except Exception as e:
        logger.error("Gemini error: %s", e)
        return "Ошибка при обращении к AI. Попробуйте позже."


async def generate_exercise() -> dict:
    prompt = """Создай упражнение на перевод с арабского для начинающего.
Верни только JSON без markdown:
{
  "question": "Как переводится: [арабское слово] ([транскрипция])?",
  "options": ["перевод A", "перевод B", "перевод C", "перевод D"],
  "correct": 0,
  "explanation": "краткое объяснение"
}
correct — индекс правильного ответа (0–3). Слово должно быть из базовой бытовой или исламской лексики."""
    try:
        text = await _generate(prompt, max_tokens=300, temperature=0.8)
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        logger.error("Exercise generation error: %s", e)
        return {}


async def generate_test_questions(topic: str, count: int = 5) -> list:
    prompt = f"""Создай {count} вопросов теста по теме «{topic}» для изучающих арабский язык (уровень начинающий).
Верни только JSON-массив без markdown:
[
  {{
    "question": "текст вопроса",
    "options": ["вариант A", "вариант B", "вариант C", "вариант D"],
    "correct": 0,
    "explanation": "краткое объяснение"
  }}
]
correct — индекс правильного ответа (0–3)."""
    try:
        text = await _generate(prompt, max_tokens=900, temperature=0.7)
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        logger.error("Test generation error: %s", e)
        return []
