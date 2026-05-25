import os
import feedparser
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

chat_history = []


def fetch_relevant_news_via_google(ai_keyword="cs2"):
    try:
        feed = feedparser.parse("https://www.hltv.org/rss/news")
        news_batch = ""
        for entry in feed.entries[:5]:
            news_batch += f"Заголовок: {entry.title}\nКонтент: {entry.summary}\n---\n"
        return analyze_news_with_ai(news_batch)
    except Exception as e:
        return f"Ошибка загрузки новостей: {e}"


def analyze_news_with_ai(raw_data):
    if not raw_data: return "Нет данных."

    prompt = f"Проанализируй эти заголовки HLTV и сделай дайджест на русском языке для пользователя:\n{raw_data}"

    try:
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка AI: {e}"


def ask_custom_question(user_query):
    global chat_history
    if not user_query: return "Введите вопрос..."

    chat_history.append({"role": "user", "content": user_query})
    if len(chat_history) > 10: chat_history = chat_history[-10:]

    system_instruction = (
        "Ты профессиональный аналитик CS2. Сейчас май 2026 года. "
        "Для ответа используй встроенный веб-поиск (online_search). "
        "Ищи информацию СТРОГО на сайте hltv.org. "
        "Если игрок ушел в инактив или не играет в активном составе — НЕ ПИШИ ЕГО. "
        "Отвечай прямо, коротко и только на русском языке."
    )

    try:
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[{"role": "system", "content": system_instruction}] + chat_history,
            max_tokens=1000,
            extra_body={"online_search": True}
        )
        answer = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": answer})
        return answer
    except Exception as e:
        return f"Ошибка AI: {e}"


def clear_history():
    global chat_history
    chat_history = []