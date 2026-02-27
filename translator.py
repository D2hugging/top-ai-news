from langchain_anthropic import ChatAnthropic
from config import ANTHROPIC_API_KEY

llm = ChatAnthropic(model="claude-haiku-4-5-20251001", anthropic_api_key=ANTHROPIC_API_KEY)

def translate_titles(titles):
    translated = []
    for title in titles:
        prompt = f"请将以下英文标题翻译为中文，不需要解释：\n\n{title}"
        print(f"[DEBUG] Translating: {title}")
        response = llm.invoke(prompt)
        translated.append(response.content.strip())

    return translated
