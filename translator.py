from llm import get_llm

llm = get_llm()


def translate_titles(titles):
    if not titles:
        return []

    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles))
    prompt = (
        "将以下英文标题翻译为中文，按编号返回，每行一个，不需要解释。\n\n"
        "示例：\n"
        "输入：\n"
        "1. OpenAI releases new model\n"
        "2. Google updates search algorithm\n"
        "输出：\n"
        "1. OpenAI 发布新模型\n"
        "2. Google 更新搜索算法\n\n"
        f"现在请翻译：\n{numbered}"
    )
    response = llm.invoke(prompt)

    lines = [l.split(". ", 1)[-1].strip() for l in response.content.strip().split("\n") if l.strip()]

    # fallback: pad with empty strings if LLM returns fewer lines than expected
    while len(lines) < len(titles):
        lines.append("")

    return lines[:len(titles)]
