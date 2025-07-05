import gradio as gr
from graph_runner import build_graph

graph = build_graph()

def run_bot():
    result = graph.invoke({})
    return result["markdown"]

demo = gr.Interface(fn=run_bot,
                    inputs=[],
                    outputs="markdown",
                    title="巨头的AI",
                    description="点击按钮即可查看最新热点新闻",
                    allow_flagging="never")
demo.launch()