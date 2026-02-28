import os
import logging
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from graph_runner import build_graph

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = FastAPI(title="Hacker Top News")


@app.post("/v1/news/fetch")
async def run_task_endpoint(request: Request, background_tasks: BackgroundTasks):
    """供 GitHub Action 调用的接口"""
    logging.info(f"API /v1/news/fetch called from {request.client.host}")

    secret_token = os.getenv("HF_TOKEN")
    auth_header = request.headers.get("Authorization")
    if secret_token and auth_header != f"Bearer {secret_token}":
        logging.warning("Unauthorized access attempt.")
        raise HTTPException(
            status_code=403, detail="Forbidden: Invalid or missing token.")

    def run_once():
        logging.info("Running the graph once for API call...")
        graph = build_graph()
        result = graph.invoke({})
        logging.info("Graph execution finished.")
        logging.info(result.get("markdown", "No markdown content generated."))

    background_tasks.add_task(run_once)
    return JSONResponse({"status": "accepted", "message": "Task running in background."})


@app.get("/api/ping")
def ping():
    """健康检查"""
    return JSONResponse({"status": "ok", "app": "Hacker Top News"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
