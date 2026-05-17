import asyncio
import json
import logging
from functools import partial

from google import genai
from google.genai import types

from config import config

logger = logging.getLogger(__name__)

_client = genai.Client(
    api_key=config.GEMINI_API_KEY,
    http_options={"api_version": "v1"},
)

_MODEL = "gemini-1.5-flash"

_SYSTEM = """Ты — преподаватель арабского языка для русскоязычных студентов.

Правила:
- Отвечай только на русском языке
- Арабские слова пиши в формате: арабский (транскрипция) — перевод
- Объясняй просто, без академической перегрузки, максимум 5 предложений
- Если не уверен — честно говори об этом
- При исламских терминах — будь точен и аккуратен
- Не придумывай правила, которых не существует
- Если вопрос не связан с арабским языком — вежливо откажись"""


def _sync_generate(contents: str, max_tokens: int, temperature: float) -> str:
    response = _client.models.generate_content(
        model=_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM,
            max_output_tokens=max_tokens,
            temperature=temperature,
        ),
    )
    return response.text or ""


async def _generate(contents: str, max_tokens: int = 400, temperature: float = 0.5) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, partial(_sync_generate, contents, max_tokens, temperature)
    )


async def ask(question: str) -> str:
    try:
        text = await _generate(question, max_tokens=400, temperature=0.5)
        return text or "Не удалось получить ответ."
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
