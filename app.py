import gradio as gr
from graph_runner import build_graph

graph = build_graph()

def run_bot():
    result = graph.invoke({})
    return result["markdown"]

demo = gr.Interface(fn=run_bot,
                    inputs=[],
                    outputs="markdown",
                    title="Hacker Top News",
                    description="Get the top news from Hacker News",
                    allow_flagging="never")

demo.launch()