import gradio as gr
from graph_runner import build_graph

graph = build_graph()

def run_bot():
    result = graph.invoke({})
    return result["markdown"]

demo = gr.Interface(fn=run_bot,
                    inputs=[],
                    outputs="markdown",
                    title="🔥 AI 新闻机器人 (Hacker News 中文摘要)",
                    description="点击按钮即可查看最新热点新闻（自动翻译）")
demo.launch()