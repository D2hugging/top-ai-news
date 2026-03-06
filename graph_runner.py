from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import os
import requests
from news_sources import fetch_hackernews, fetch_google_news, fetch_meta_news, fetch_nvidia_news
from translator import translate_titles
from formatter import format_markdown
from curator import curate_items
from persistence import load_recent_urls, save_urls


class NewsState(TypedDict):
    items: List[dict]
    translated: List[str]
    markdown: str
    seen_urls: List[str]


def node_fetch_all(state: NewsState):
    items = (
        fetch_hackernews()
        + fetch_google_news()
        + fetch_meta_news()
        + fetch_nvidia_news()
    )
    return {"items": items}


def node_dedup(state: NewsState):
    seen = load_recent_urls()
    fresh = [item for item in state["items"] if item["url"] not in seen]
    return {"items": fresh, "seen_urls": list(seen)}


def node_curate(state: NewsState):
    seen_urls = set(state.get("seen_urls") or [])
    return {"items": curate_items(state["items"], seen_urls=seen_urls)}


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

    save_urls(state["items"])


def build_graph():
    builder = StateGraph(NewsState)
    # add nodes
    builder.add_node("fetch_all", node_fetch_all)
    builder.add_node("dedup", node_dedup)
    builder.add_node("curate", node_curate)
    builder.add_node("translate", node_translate)
    builder.add_node("format", node_format)
    builder.add_node("send_discord", node_send_discord)

    # add edges
    builder.set_entry_point("fetch_all")
    builder.add_edge("fetch_all", "dedup")
    builder.add_edge("dedup", "curate")
    builder.add_edge("curate", "translate")
    builder.add_edge("translate", "format")
    builder.add_edge("format", "send_discord")
    builder.add_edge("send_discord", END)

    return builder.compile()
