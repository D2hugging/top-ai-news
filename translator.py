from llm import get_llm

llm = get_llm()


def translate_titles(titles):
    if not titles:
        return []

    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles))
    prompt = f"将以下英文标题翻译为中文，按编号返回，每行一个，不需要解释：\n\n{numbered}"
    response = llm.invoke(prompt)

    lines = [l.split(". ", 1)[-1].strip() for l in response.content.strip().split("\n") if l.strip()]

    # fallback: pad with empty strings if LLM returns fewer lines than expected
    while len(lines) < len(titles):
        lines.append("")

    return lines[:len(titles)]
