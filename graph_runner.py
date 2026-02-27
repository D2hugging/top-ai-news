from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import os
import requests
from news_sources import fetch_hackernews, fetch_google_news, fetch_meta_news, fetch_nvidia_news
from translator import translate_titles
from formatter import format_markdown
from curator import curate_items


MIN_CURATED = 5
MAX_ATTEMPTS = 2


class NewsState(TypedDict):
    items: List[dict]
    translated: List[str]
    markdown: str
    fetch_limit: int
    curate_attempts: int


def node_fetch_all(state: NewsState):
    limit = state.get("fetch_limit") or 10
    items = (
        fetch_hackernews(limit)
        + fetch_google_news(limit)
        + fetch_meta_news(limit)
        + fetch_nvidia_news(limit)
    )
    return {"items": items}


def node_curate(state: NewsState):
    attempts = state.get("curate_attempts") or 0
    curated = curate_items(state["items"])
    return {
        "items": curated,
        "curate_attempts": attempts + 1,
        "fetch_limit": (state.get("fetch_limit") or 10) * 2,
    }


def route_after_curate(state: NewsState) -> str:
    too_few = len(state["items"]) < MIN_CURATED
    can_retry = state["curate_attempts"] < MAX_ATTEMPTS
    if too_few and can_retry:
        print(f"[curate] only {len(state['items'])} items, retrying with larger fetch...")
        return "fetch_all"
    return "translate"


def node_translate(state: NewsState):
    titles = [item['title'] for item in state['items']]
    return {"translated": translate_titles(titles)}


def node_format(state: NewsState):
    return {"markdown": format_markdown("Top AI News", state['items'], state['translated'])}


def node_send_discord(state: NewsState):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL not set, skipping notification.")
        return

    # split by "\n"
    parts = state["markdown"].split("\n")
    header = parts[0]
    news_items_str = ["\n".join(parts[i:i+2]) for i in range(1, len(parts), 2)]

    # send in chunks to avoid exceeding Discord message length limits
    message_chunk = header + "\n"
    for item_str in news_items_str:
        if len(message_chunk) + len(item_str) + 1 > 2000:
            requests.post(webhook_url, json={"content": message_chunk})
            message_chunk = ""  # new chunk
        message_chunk += item_str + "\n"

    if message_chunk:  # the last chunk
        requests.post(webhook_url, json={"content": message_chunk})


def build_graph():
    builder = StateGraph(NewsState)
    # add nodes
    builder.add_node("fetch_all", node_fetch_all)
    builder.add_node("curate", node_curate)
    builder.add_node("translate", node_translate)
    builder.add_node("format", node_format)
    builder.add_node("send_discord", node_send_discord)

    # add edges
    builder.set_entry_point("fetch_all")
    builder.add_edge("fetch_all", "curate")
    builder.add_conditional_edges("curate", route_after_curate, {"fetch_all": "fetch_all", "translate": "translate"})
    builder.add_edge("translate", "format")
    builder.add_edge("format", "send_discord")
    builder.add_edge("send_discord", END)

    return builder.compile()
