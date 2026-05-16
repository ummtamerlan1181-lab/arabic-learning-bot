import json
import logging

from openai import AsyncOpenAI

from config import config

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

_SYSTEM = """Ты — преподаватель арабского языка для русскоязычных студентов.

Правила:
- Отвечай только на русском языке
- Арабские слова пиши в формате: арабский (транскрипция) — перевод
- Объясняй просто, без академической перегрузки, максимум 5 предложений
- Если не уверен — честно говори об этом
- При исламских терминах — будь точен и аккуратен
- Не придумывай правила, которых не существует
- Если вопрос не связан с арабским языком — вежливо откажись"""


async def ask(question: str) -> str:
    try:
        resp = await _client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": question},
            ],
            max_tokens=400,
            temperature=0.5,
        )
        return resp.choices[0].message.content or "Не удалось получить ответ."
    except Exception as e:
        logger.error("OpenAI error: %s", e)
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
        resp = await _client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.8,
        )
        text = (resp.choices[0].message.content or "{}").strip()
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
        resp = await _client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": prompt},
            ],
            max_tokens=900,
            temperature=0.7,
        )
        text = (resp.choices[0].message.content or "[]").strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        logger.error("Test generation error: %s", e)
        return []
