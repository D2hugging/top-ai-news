from llm import get_llm

llm = get_llm()

def translate_titles(titles):
    translated = []
    for title in titles:
        prompt = f"请将以下英文标题翻译为中文，不需要解释：\n\n{title}"
        print(f"[DEBUG] Translating: {title}")
        response = llm.invoke(prompt)
        translated.append(response.content.strip())

    return translated
