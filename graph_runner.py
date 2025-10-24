from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import os
import requests
from news_sources import fetch_hackernews
from translator import translate_titles
from formatter import format_markdown


class NewsState(TypedDict):
    items: List[dict]
    translated: List[str]
    markdown: str


def node_fetch_hn(state: NewsState):
    items = fetch_hackernews()
    return {"items": items}


def node_translate(state: NewsState):
    titles = [item['title'] for item in state['items']]
    return {"translated": translate_titles(titles)}


def node_format(state: NewsState):
    return {"markdown": format_markdown("Hacker News", state['items'], state['translated'])}


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
    builder.add_node("fetch_hn", node_fetch_hn)
    builder.add_node("translate", node_translate)
    builder.add_node("format", node_format)
    builder.add_node("send_discord", node_send_discord)

    builder.set_entry_point("fetch_hn")
    builder.add_edge("fetch_hn", "translate")
    builder.add_edge("translate", "format")
    builder.add_edge("format", "send_discord")
    builder.add_edge("send_discord", END)
    return builder.compile()
