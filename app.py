import gradio as gr_module
import logging
import gradio as gr
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
import os
from graph_runner import build_graph

# --------- logging: keep time format ---------
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --------- FastAPI main app ---------
app = FastAPI()

# --------- Gradio UI as /gradio ---------


def run_bot():
    graph = build_graph()
    result = graph.invoke({})
    return result["markdown"]


iface = gr.Interface(
    fn=run_bot,
    inputs=[],
    outputs="markdown",
    title="Hacker Top News",
    description="Get the top news from Hacker News",
    allow_flagging="never",
)
app = gr_module.mount_gradio_app(app, iface, path="/gradio")

# --------- Set root to auto redirect web visitors to /gradio ---------


@app.get("/")
def root():
    return RedirectResponse(url="/gradio")

# --------- Your API logic under /api/ ---------


@app.post("/api/run-task")
async def run_task_endpoint(request: Request, background_tasks: BackgroundTasks):
    logging.info(f"API /api/run-task called from {request.client.host}")
    secret_token = os.getenv("HF_TOKEN")
    auth_header = request.headers.get("Authorization")

    if secret_token and auth_header != f"Bearer {secret_token}":
        logging.warning(
            "Unauthorized access attempt to /api/run-task endpoint.")
        raise HTTPException(
            status_code=403, detail="Forbidden: Invalid or missing token.")

    def run_once():
        logging.info("Running the graph once for API call...")
        graph = build_graph()
        result = graph.invoke({})
        logging.info("Graph execution finished for API call.")
        logging.info(result.get("markdown", "No markdown content generated."))
        return result
    background_tasks.add_task(run_once)
    logging.info("Task accepted and scheduled in background for API call.")
    return {"status": "accepted", "message": "Task has been accepted and is running in the background."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
