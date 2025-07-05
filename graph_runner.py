from langgraph.graph import StateGraph, END
from typing import TypedDict, List
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

def build_graph():
    builder = StateGraph(NewsState)
    builder.add_node("fetch_hn", node_fetch_hn)
    builder.add_node("translate", node_translate)
    builder.add_node("format", node_format)

    builder.set_entry_point("fetch_hn")
    builder.add_edge("fetch_hn", "translate")
    builder.add_edge("translate", "format")
    builder.add_edge("format", END)
    return builder.compile()