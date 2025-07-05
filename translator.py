from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)

def translate_titles(titles):
    translated = []
    for title in titles:
        prompt = f"请将以下英文标题翻译为中文，不需要解释：\n\n{title}"
        print(f"[DEBUG] Translating: {title}")
        response = llm.invoke(prompt)
        translated.append(response.content.strip())
    return translated
