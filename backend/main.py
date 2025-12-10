# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from controllers.log_controller import pull_and_save_logs
from controllers.rag_controller import query_logs
from controllers.rag_controller import summary_logs
# --- ADD CORS ---
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RAG Log Ingest API")

# Allow frontend at localhost:5173 (Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RefreshResp(BaseModel):
    ingested: int
    from_ts: int | None
    to_ts: int | None
    status: str


@app.post("/refresh", response_model=RefreshResp)
def refresh():
    ingested, from_ts, to_ts = pull_and_save_logs()
    return RefreshResp(
        ingested=ingested,
        from_ts=from_ts,
        to_ts=to_ts,
        status="success"
    )

@app.get("/summary")
def summary():
    return summary_logs()


@app.get("/")
def root():
    return {"msg": "Use POST /refresh to pull logs"}


@app.post("/query")
def query(data: dict):
    question = data.get("q")
    if not question:
        return {"error": "Missing field 'q'"}

    answer = query_logs(question)
    return {"result": answer}


# -------------------------
# AUTO-START UVICORN HERE
# -------------------------
if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server at http://0.0.0.0:8000 ...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
    print(" FastAPI server stopped")
