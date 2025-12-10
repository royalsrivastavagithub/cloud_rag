Understood — here is a **clean, professional README.md** with **no emojis**, fully formatted in Markdown.

---

# CloudRAG – AI-Powered EC2 Log Analysis Using RAG

CloudRAG is a lightweight, end-to-end Retrieval-Augmented Generation (RAG) system designed to analyze EC2 instance logs using CloudWatch, OpenAI embeddings, ChromaDB, and FastAPI.

It allows you to pull logs from AWS and ask natural-language questions such as:

* "Which service failed?"
* "What error code appears in the logs?"
* "Did postgres fail today?"

This project demonstrates real-world integration of AWS, vector databases, LangChain components, and modern LLMs.

---

# Features

* Pull EC2 logs directly from CloudWatch
* Store logs locally for inspection
* Embed logs using OpenAI embeddings
* Store embeddings in ChromaDB
* Query logs using natural language with RAG-based retrieval
* FastAPI backend providing `/refresh` and `/query` endpoints
* Clean architecture and minimal dependencies

---

# Setup Instructions

## 1. Clone the repository

```bash
git clone <your-repo-url>
cd cloud_rag
```

## 2. Create and activate a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

Minimal working dependencies:

```
fastapi
uvicorn[standard]
boto3
python-dotenv
chromadb
langchain-openai
langchain-chroma
openai
```

---

# Environment Variables

Create a `.env` file in the project root:

```
AWS_REGION=us-east-1
CLOUDWATCH_LOG_GROUP=/ec2/logs/RAG

# OpenAI API key for embeddings + completion model
OPENAI_API_KEY=your_openai_api_key_here

# Optional: CloudWatch lookback window (minutes)
DEFAULT_LOOKBACK_MIN=10
```

Ensure `.env` is included in `.gitignore`.

---

# Project Structure

```
cloud_rag/
│
├── aws/
│   ├── log_controller.py       # Pull logs from CloudWatch
│   ├── vector_controller.py    # Embed logs + store in ChromaDB
│   └── rag_controller.py       # RAG retrieval + LLM reasoning
│
├── aws_logs/                   # Ignored local log storage
├── vector_db/                  # Ignored ChromaDB vector store
│
├── main.py                     # FastAPI entrypoint
├── requirements.txt
└── .env
```

Folders `aws_logs/` and `vector_db/` are runtime-only and should not be committed.

---

# Running the Application

Start the FastAPI server:

```bash
python main.py
```

The API will be available at:

```
http://localhost:8000
```

---

# API Usage

## 1. Pull latest logs from CloudWatch

```
POST /refresh
```

Example:

```bash
curl -X POST http://localhost:8000/refresh
```

Example response:

```json
{
  "ingested": 16,
  "from_ts": 1765349541622,
  "to_ts": 1765351025620,
  "status": "success"
}
```

This step fetches logs, stores them, embeds them, and inserts them into ChromaDB.

---

## 2. Query logs using natural language

```
POST /query
```

Example:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"q": "What is the error code mentioned in the logs?"}'
```

Example response:

```json
{
  "result": {
    "answer": "YES",
    "evidence": [
      "root: RAG_TEST_12345: The backup service encountered exit code 17"
    ]
  }
}
```

---

# Testing With a Custom Log Event

On your EC2 instance:

```bash
sudo logger "RAG_TEST_12345: The backup service encountered exit code 17"
```

Then:

1. Call `/refresh`
2. Query:
   `"What is the error code?"`
   `"Did the backup service fail?"`

---

# Potential Improvements

The following features can expand and enhance the system:

### Retrieval & Reasoning

* Time-based filtering (last hour, last 10 minutes)
* Structured output formatting without relying on the LLM
* Summaries of logs by severity (INFO, WARN, ERROR)

### Observability Enhancements

* Automatic detection of failing or restarting systemd services
* Endpoint summarizing overall system health
* Detection of repeated patterns or anomalies

### UI / Frontend

* Web dashboard for logs, queries, and visual insights
* Real-time updates and auto-refreshing interface

### Automation

* Background job to auto-run `/refresh` on a schedule
* SNS/SQS/Slack alerts when errors appear

### Deployment

* Containerize using Docker
* Deploy on ECS, EC2, or Kubernetes
* Use Chroma Cloud or Pinecone for scalable vector storage

---