# aws/rag_controller.py

import os
from dotenv import load_dotenv
load_dotenv()

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
