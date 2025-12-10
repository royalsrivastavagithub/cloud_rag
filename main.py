# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from controllers.log_controller import pull_and_save_logs
from controllers.rag_controller import query_logs
app = FastAPI(title="RAG Log Ingest API")

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