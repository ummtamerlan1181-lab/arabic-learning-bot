# Arabic Learning Bot

Telegram-бот для изучения арабского языка для русскоязычных пользователей.

## Стек

- Python 3.11+
- aiogram 3.7
- OpenAI API (gpt-4o-mini)
- SQLite (aiosqlite)

## Структура проекта

```
arabic_bot/
├── main.py                  # Точка входа
├── config.py                # Конфигурация из .env
├── states.py                # FSM-состояния
├── database/
│   ├── db.py                # Инициализация SQLite
│   └── models.py            # Датаклассы
├── handlers/
│   ├── start.py             # /start, главное меню
│   ├── lessons.py           # Уроки
│   ├── words.py             # Слова и карточки
│   ├── exercises.py         # Упражнения (AI)
│   ├── reading.py           # Тексты для чтения
│   ├── tests.py             # Тесты (AI)
│   ├── progress.py          # Прогресс пользователя
│   ├── settings.py          # Настройки
│   └── ai_helper.py         # AI-помощник
├── keyboards/
│   ├── main_menu.py         # Главное меню
│   ├── common.py            # Кнопки назад/домой
│   ├── lessons.py           # Клавиатуры уроков
│   └── words.py             # Клавиатуры слов
├── services/
│   ├── ai_service.py        # OpenAI интеграция
│   ├── progress_service.py  # Прогресс и очки
│   └── word_service.py      # Работа со словарём
├── middlewares/
│   └── throttling.py        # Защита от спама
├── data/
│   ├── words.json           # 60 слов по 6 темам
│   ├── lessons.json         # 10 уроков
│   └── reading.json         # Тексты для чтения
├── requirements.txt
└── .env.example
```

## Запуск

### 1. Установи зависимости

```bash
pip install -r requirements.txt
```

### 2. Создай `.env` файл

```bash
cp .env.example .env
```

Заполни:
```
BOT_TOKEN=токен_от_BotFather
OPENAI_API_KEY=ключ_от_OpenAI
```

### 3. Запусти

```bash
python main.py
```

## Функции MVP

| Раздел | Описание |
|--------|----------|
| 📘 Уроки | 10 уроков: алфавит, грамматика, глаголы, предлоги, диалоги |
| 🧠 Слова | 60 слов по темам: семья, дом, еда, Коран, приветствия, учёба |
| ✍️ Упражнения | AI генерирует задания на перевод с 4 вариантами |
| 📖 Чтение | Тексты 3 уровней с транскрипцией и переводом |
| 🎯 Тесты | 5 вопросов по алфавиту, словам или грамматике |
| 📊 Прогресс | Серия дней, очки, статистика |
| 🤖 AI-помощник | Вопрос → ответ по арабскому языку |

## Получение токенов

- **BOT_TOKEN**: [@BotFather](https://t.me/BotFather) в Telegram → /newbot
- **OPENAI_API_KEY**: [platform.openai.com](https://platform.openai.com/api-keys)
