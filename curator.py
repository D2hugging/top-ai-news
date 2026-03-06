from typing import List
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from llm import get_llm
from news_sources import fetch_hackernews, fetch_google_news, fetch_meta_news, fetch_nvidia_news


llm = get_llm()

SOURCES = {
    "hackernews": fetch_hackernews,
    "google": fetch_google_news,
    "meta": fetch_meta_news,
    "nvidia": fetch_nvidia_news,
}


def curate_items(items: list, top_n: int = 15, seen_urls: set = None) -> list:
    if not items:
        return []

    session_items = list(items)
    result = {"selected": []}
    _seen_urls = seen_urls or set()

    @tool
    def fetch_more(source: str, limit: int = 10) -> str:
        """Fetch additional news items from a specific source when current results are
        insufficient or lack diversity. source must be one of: hackernews, google, meta, nvidia.
        limit is the number of additional items to fetch (max 30)."""
        if source not in SOURCES:
            return f"Unknown source '{source}'. Choose from: {list(SOURCES.keys())}"
        new_items = SOURCES[source](min(limit, 30))
        existing_urls = {item["url"] for item in session_items} | _seen_urls
        new_items = [i for i in new_items if i["url"] not in existing_urls]
        session_items.extend(new_items)
        offset = len(session_items) - len(new_items)
        preview = "\n".join(f"{offset + j}. {item['title']}" for j, item in enumerate(new_items))
        return f"Added {len(new_items)} new items from {source}:\n{preview}\nTotal: {len(session_items)}"

    @tool
    def finalize(indices: List[int]) -> str:
        """Finalize the curation by selecting items at the given 0-based indices.
        Call this when you are satisfied with your selection."""
        valid = [session_items[i] for i in indices if 0 <= i < len(session_items)]
        result["selected"] = valid
        return f"Finalized {len(valid)} items."

    agent = create_react_agent(llm, [fetch_more, finalize])

    numbered = "\n".join(f"{i}. {item['title']}" for i, item in enumerate(session_items))
    prompt = (
        f"You are an AI news curator. Review the following {len(session_items)} news items "
        f"and select the best {top_n} stories about AI, machine learning, and technology.\n\n"
        "Guidelines:\n"
        "- Prefer stories with broad impact, novel research, or significant industry news\n"
        "- Avoid topical duplicates covering the same event\n"
        "- If current items are insufficient or lack diversity, call fetch_more to get more from a specific source\n"
        "- When satisfied with your selection, call finalize with the chosen indices\n\n"
        f"Current items:\n{numbered}"
    )

    agent.invoke({"messages": [{"role": "user", "content": prompt}]})

    # fallback if agent didn't call finalize
    return result["selected"] or session_items[:top_n]
