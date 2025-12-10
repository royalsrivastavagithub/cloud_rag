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
