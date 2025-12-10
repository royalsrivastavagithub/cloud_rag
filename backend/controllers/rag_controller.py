# aws/rag_controller.py
import re
import os
from dotenv import load_dotenv
load_dotenv()
from .vector_controller import vector_store
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma

# Load embeddings (same as vector_controller)
emb = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

# Load vector store
db = Chroma(
    collection_name="logs",
    embedding_function=emb,
    persist_directory="./vector_db",
)

# Chat model (can use gpt-4o-mini or gpt-4o)
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini",   # cheap + powerful
    temperature=0
)

def summary_logs():
    # Pull a broad set of logs to summarize
    docs = vector_store.similarity_search("summarize logs", k=20)

    raw_logs = [d.page_content for d in docs]

    # Basic stats extraction
    error_count = sum(1 for log in raw_logs if "error" in log.lower())
    warn_count = sum(1 for log in raw_logs if "warn" in log.lower())

    # Extract services (assumes "serviceName:" or systemd patterns)
    service_pattern = r"(?:systemd|root|cron|ssm-agent|amazon-ssm-agent|backup|postgres)[^:]*"
    services = []

    for log in raw_logs:
        match = re.search(service_pattern, log, re.IGNORECASE)
        if match:
            services.append(match.group().strip())

    # Extract timestamps
    timestamps = []
    for log in raw_logs:
        try:
            ts = log.split(" | ")[0]
            timestamps.append(ts)
        except:
            continue

    latest_ts = max(timestamps) if timestamps else None

    # Ask LLM to summarize the logs
    prompt = f"""
Summarize the following EC2 logs. 
Provide:
1. Key issues found
2. Services involved
3. Any failures or unusual events
4. A concise human-readable summary

Logs:
{raw_logs}
"""

    llm_summary = llm.invoke(prompt).content

    return {
        "total_logs_analyzed": len(raw_logs),
        "errors": error_count,
        "warnings": warn_count,
        "top_services": list(set(services)),
        "latest_timestamp": latest_ts,
        "llm_summary": llm_summary,
    }

def query_logs(question: str):
    """Retrieve relevant logs and ask the LLM to summarize/analyze them."""
    # 1. Retrieve similar log entries
    retrieved = db.similarity_search(question, k=10)

    if not retrieved:
        return {
            "answer": "No relevant logs found.",
            "evidence": []
        }

    context_logs = "\n".join([doc.page_content for doc in retrieved])

    prompt = f"""
You are a log analysis assistant for EC2 system logs.

USER QUESTION:
{question}

RELEVANT LOGS:
{context_logs}

TASK:
- Analyze whether the logs answer the user's question.
- If the question is about failures (e.g., postgres fail, service crash), determine if such events occurred.
- Provide a clear YES/NO answer when appropriate.
- Quote the exact log lines as evidence.
- Keep the answer short and actionable.

Respond in JSON with fields:
- answer
- evidence (list of log lines)
    """

    response = llm.invoke(prompt).content

    return response

def health_report():
    # Get all logs from ChromaDB
    results = vector_store.get(
        include=["metadatas", "documents"]
    )

    logs = results["documents"]
    metas = results["metadatas"]

    total = len(logs)

    errors = []
    warnings = []
    services_with_errors = {}
    repeated = {}

    for log, meta in zip(logs, metas):
        text = log.lower()

        # Error classification
        if "error" in text or "failed" in text:
            errors.append(log)
        elif "warn" in text:
            warnings.append(log)

        # Extract service name (very simple heuristic)
        m = re.search(r"([a-zA-Z0-9\-\.]+):", log)
        if m:
            svc = m.group(1)
            repeated[svc] = repeated.get(svc, 0) + 1

        # Track services with failures
        if "error" in text or "failed" in text:
            services_with_errors[svc] = services_with_errors.get(svc, 0) + 1

    # Top 3 recurring services
    top_repeated = sorted(repeated.items(), key=lambda x: x[1], reverse=True)[:3]

    # AI summary
    llm = ChatOpenAI(model="gpt-4o-mini")
    summary = llm.invoke(
        f"""
        Analyze these system logs and give a short server health assessment.

        Total logs: {total}
        Errors: {len(errors)}
        Warnings: {len(warnings)}
        Services with error counts: {services_with_errors}
        Repeated patterns: {top_repeated}

        Return a concise summary in 4–5 sentences.
        """
    ).content

    return {
        "total_logs": total,
        "errors": len(errors),
        "warnings": len(warnings),
        "services_with_errors": services_with_errors,
        "top_repeated_patterns": top_repeated,
        "llm_summary": summary
    }

