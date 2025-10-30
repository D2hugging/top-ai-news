import os
import logging
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
import gradio as gr
from graph_runner import build_graph

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 创建 FastAPI 应用
app = FastAPI()


@app.post("/v1/news/fetch")
async def run_task_endpoint(request: Request, background_tasks: BackgroundTasks):
    logging.info(f"API /v1/news/fetch called from {request.client.host}")

    # Token 校验（与 Space Secret 对应）
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
    return {"status": "accepted", "message": "Task running in background."}


# 定义 Gradio 接口（UI）
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

# 挂载 Gradio 到 FastAPI 子路径
app = gr.mount_gradio_app(app, iface, path="/ui")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
