from langchain_google_genai import ChatGoogleGenerativeAI
import os

google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=google_api_key)

def translate_titles(titles):
    translated = []
    for title in titles:
        prompt = f"请将以下英文标题翻译为中文，不需要解释：\n\n{title}"
        print(f"[DEBUG] Translating: {title}")
        response = llm.invoke(prompt)
        translated.append(response.content.strip())
    return translated
