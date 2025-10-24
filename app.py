import gradio as gr
from graph_runner import build_graph
import argparse


def run_once():
    print("Running the graph once for scheduled execution...")
    graph = build_graph()
    result = graph.invoke({})
    print("Graph execution finished. Markdown content generated and notifications sent.")
    print(result.get("markdown", "No markdown content generated."))


def launch_gradio():
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hacker Top News Bot")
    parser.add_argument('--run-once', action='store_true',
                        help='Run the task once and exit.')
    args = parser.parse_args()

    if args.run_once:
        run_once()
    else:
        launch_gradio()
