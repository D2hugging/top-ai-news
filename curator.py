from pydantic import BaseModel
from typing import List
from langchain_anthropic import ChatAnthropic
from config import ANTHROPIC_API_KEY


class CurationResult(BaseModel):
    selected_indices: List[int]


llm = ChatAnthropic(model="claude-haiku-4-5-20251001", anthropic_api_key=ANTHROPIC_API_KEY)
curator = llm.with_structured_output(CurationResult)


def curate_items(items: list, top_n: int = 15) -> list:
    if not items:
        return []

    numbered = "\n".join(f"{i}. {item['title']}" for i, item in enumerate(items))
    prompt = (
        f"You are an AI news curator. From the list below, select the {top_n} most "
        "relevant and interesting stories about AI, machine learning, and technology. "
        "Prefer stories with broad impact, novel research, or significant industry news. "
        "Avoid duplicates covering the same topic. "
        "Return only the 0-based indices of the stories you select.\n\n"
        + numbered
    )
    result = curator.invoke(prompt)
    valid = [i for i in result.selected_indices if 0 <= i < len(items)]
    return [items[i] for i in valid]
