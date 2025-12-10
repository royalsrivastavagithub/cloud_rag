
---

# CloudRAG – AI-Powered EC2 Log Analysis Using RAG

CloudRAG is a lightweight, end-to-end Retrieval-Augmented Generation (RAG) system designed to analyze EC2 instance logs using CloudWatch, OpenAI embeddings, ChromaDB, and FastAPI.

It allows natural-language log analysis such as:

* “Which service failed?”
* “What error code appears in the logs?”
* “Did postgres fail today?”

This project demonstrates a real-world integration of AWS logging pipelines, vector search, LangChain components, and LLM reasoning.

---

# Features

* Pull EC2 logs directly from CloudWatch.
* Store logs locally for inspection.
* Embed logs using OpenAI embeddings.
* Store vector embeddings in ChromaDB.
* Natural-language log search using RAG retrieval.
* FastAPI backend with `/refresh` and `/query` endpoints.
* React-based frontend dashboard.
* Clean architecture and minimal dependencies.

---

# Project Structure

```
cloud_rag/
│
├── backend/
│   ├── controllers/
│   │   ├── log_controller.py      # Pull logs from CloudWatch
│   │   ├── vector_controller.py   # OpenAI embeddings + Chroma storage
│   │   └── rag_controller.py      # Retrieval + LLM reasoning
│   ├── aws_logs/                  # Ignored - raw logs
│   ├── vector_db/                 # Ignored - Chroma DB files
│   ├── main.py                    # FastAPI server
│   └── requirements.txt
│
├── frontend/
│   ├── src/App.jsx                # React UI
│   ├── src/App.css
│   └── vite.config.js
│
├── .env                           # Environment variables
└── Dockerfile
```

Folders `backend/aws_logs/` and `backend/vector_db/` are runtime-only and must remain in `.gitignore`.

---

# Environment Variables

Create a `.env` file inside **backend/**:

```
AWS_REGION=us-east-1
CLOUDWATCH_LOG_GROUP=/ec2/logs/RAG

OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_LOOKBACK_MIN=10
```

---

# Installing & Running Backend

## 1. Create virtual environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Start FastAPI server

```bash
python main.py
```

Server runs at:

```
http://localhost:8000
```

---

# API Usage

## 1. Refresh logs from CloudWatch

```
POST /refresh
```

Example:

```bash
curl -X POST http://localhost:8000/refresh
```

Response:

```json
{
  "ingested": 16,
  "from_ts": 1765349541622,
  "to_ts": 1765351025620,
  "status": "success"
}
```

## 2. Query logs using natural language

```
POST /query
```

Example:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"q": "What is the error code?"}'
```

Response:

```json
{
  "result": {
    "answer": "YES",
    "evidence": ["... extracted log line ..."]
  }
}
```

---

# React Frontend (Vite + React + JavaScript)

A simple UI to:

* Trigger `/refresh`
* Ask questions via `/query`
* Display structured answers & evidence

## Install and run:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

### CORS

Backend includes permissive CORS rules:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

# Running With Docker

## Build the image

```bash
docker build -t cloudrag-backend ./backend
```

## Run the container

```bash
docker run -p 8000:8000 --env-file .env cloudrag-backend
```

Backend now runs inside Docker.

---

# Testing the Pipeline End-to-End

### On EC2 instance (log generator):

```bash
sudo logger "RAG_TEST_12345: Backup service failed with exit code 17"
```

### Step 1: Refresh logs

```bash
curl -X POST http://localhost:8000/refresh
```

### Step 2: Query logs

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"q": "What failed in the backup service?"}'
```

---

# Improving the Project (Future Additions)

### Retrieval & LLM Improvements

* Multi-turn questions
* Time-filtered retrieval (last 15 min, 1 hour)
* Log severity classification (INFO/WARN/ERROR)

### Observability Features

* Detect frequent restarts / anomalies
* Summaries of critical issues
* Automatic alerts (SNS, Slack)

### Frontend Enhancements

* System health dashboard
* Search history
* Filter logs by service or instance

### Infrastructure

* Deploy backend and frontend using Docker Compose
* ECS/Kubernetes deployment
* Use managed vector DB (Pinecone / Chroma Cloud)

---
