import gradio as gr
from graph_runner import build_graph
import argparse
import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks


def run_once():
    """Executes the complete task once and returns the result."""
    print("Running the graph once for scheduled execution...")
    graph = build_graph()
    result = graph.invoke({})
    print("Graph execution finished. Markdown content generated and notifications sent.")
    print(result.get("markdown", "No markdown content generated."))
    return result


def launch_gradio():
    """Creates and returns the Gradio Web UI interface."""
    graph = build_graph()

    def run_bot():
        result = graph.invoke({})
        return result["markdown"]

    return gr.Interface(fn=run_bot,
                        inputs=[],
                        outputs="markdown",
                        title="Hacker Top News",
                        description="Get the top news from Hacker News",
                        allow_flagging="never")


# Create FastAPI app
app = FastAPI()


@app.post("/run-task")
async def run_task_endpoint(request: Request, background_tasks: BackgroundTasks):
    """
    A secure endpoint to trigger a one-time task.
    Requires a secret token provided via the 'Authorization' header.
    """
    secret_token = os.getenv("SCHEDULER_SECRET")
    auth_header = request.headers.get("Authorization")

    if not secret_token or auth_header != f"Bearer {secret_token}":
        raise HTTPException(
            status_code=403, detail="Forbidden: Invalid or missing token.")

    background_tasks.add_task(run_once)
    return {"status": "accepted", "message": "Task has been accepted and is running in the background."}


# Mount the Gradio app to FastAPI
gradio_app = launch_gradio()
app = gr.mount_gradio_app(app, gradio_app, path="/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hacker Top News Bot")
    parser.add_argument('--run-once', action='store_true',
                        help='Run the task once and exit.')
    args = parser.parse_args()

    if args.run_once:
        run_once()
    else:
        uvicorn.run(app, host="0.0.0.0", port=7860)
