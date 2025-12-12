# main.py
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

# Controllers (sync functions)
from controllers.log_controller import pull_and_save_logs
from controllers.rag_controller import (
    query_logs,
    summary_logs,
    health_report,
    get_error_logs,
)
from controllers.agent_controller import run_agent

# CORS
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RAG Log Ingest API")

# Allow frontend at localhost:5173 (Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RefreshResp(BaseModel):
    ingested: int
    from_ts: int | None
    to_ts: int | None
    status: str


class AgentQuery(BaseModel):
    query: str


# ---------------------------
# Async Endpoints
# ---------------------------

@app.post("/refresh", response_model=RefreshResp)
async def refresh():
    ingested, from_ts, to_ts = await run_in_threadpool(pull_and_save_logs)
    return RefreshResp(
        ingested=ingested,
        from_ts=from_ts,
        to_ts=to_ts,
        status="success"
    )


@app.get("/summary")
async def summary():
    return await run_in_threadpool(summary_logs)


@app.get("/")
async def root():
    return {"msg": "Use POST /refresh to pull logs"}


@app.post("/query")
async def query(data: dict):
    question = data.get("q")
    if not question:
        return {"error": "Missing field 'q'"}

    answer = await run_in_threadpool(query_logs, question)
    return {"result": answer}


@app.get("/health")
async def health():
    return await run_in_threadpool(health_report)


@app.get("/errors")
async def errors():
    return await run_in_threadpool(get_error_logs)


@app.post("/agent")
async def agent_api(body: AgentQuery):
    # run_agent is sync → move to thread
    response = await run_in_threadpool(run_agent, body.query)
    return {"response": response}


# ---------------------------
# Start Server
# ---------------------------
if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server at http://0.0.0.0:8000 ...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
