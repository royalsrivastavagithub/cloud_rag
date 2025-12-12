
---

# CloudRAG – AI-Powered CloudWatch Log Analysis Using RAG and Agentic Tools

CloudRAG is a lightweight, end-to-end Retrieval-Augmented Generation (RAG) system designed to analyze logs from any AWS CloudWatch log group.
It works with logs coming from EC2, ECS, Lambda, custom application logs, or any service that ships logs to CloudWatch.

CloudRAG pulls logs from a specified CloudWatch log group, embeds them using OpenAI embeddings, stores them in ChromaDB, and enables natural-language queries using RAG and an autonomous tool-calling agent.

It enables natural-language log analysis such as:

* “Which service failed?”
* “What error code appears in the logs?”
* “Did Postgres fail today?”
* “Why did errors occur today?”
* “Give me a summary of issues.”

This project demonstrates real-world integration of AWS logging pipelines, vector search, LangChain tool-calling agents, and LLM reasoning.

---

# Features

* Pull logs from any CloudWatch log group.
* Store logs locally for inspection.
* Embed logs using OpenAI embeddings.
* Store vector embeddings in ChromaDB.
* Natural-language log search using RAG retrieval.
* Tool-using autonomous LLM agent for root-cause analysis.
* FastAPI backend with endpoints for refresh, query, summary, health, errors, and agent.
* React-based frontend dashboard.
* Clean architecture with minimal dependencies.

---

# Project Structure

```
cloud_rag/
│
├── backend/
│   ├── controllers/
│   │   ├── log_controller.py      # Pull logs from CloudWatch
│   │   ├── vector_controller.py   # OpenAI embeddings + Chroma storage
│   │   ├── rag_controller.py      # Retrieval + LLM reasoning
│   │   └── agent_controller.py    # Autonomous LLM agent with tools
│   ├── aws_logs/                  # Raw logs (ignored)
│   ├── vector_db/                 # Chroma DB files (ignored)
│   ├── main.py                    # FastAPI server
│   └── requirements.txt
│
├── frontend/
│   ├── src/App.jsx
│   ├── src/App.css
│   └── vite.config.js
│
├── .env
├── docker-compose.yml
└── Dockerfile
```

`backend/aws_logs/` and `backend/vector_db/` are runtime-only directories and must remain in `.gitignore`.

---

# Environment Variables

Create a `.env` file in `backend/`:

```
AWS_ACCESS_KEY_ID=access-key-here
AWS_SECRET_ACCESS_KEY=secret-access-key-here
AWS_REGION=region-here
CLOUDWATCH_LOG_GROUP=/your/log/group
OPENAI_API_KEY=openai-api-key-here
```

This file is used for local backend execution.
For Docker deployments, pass environment variables separately or through Compose.

---

# Getting Started

## Using Docker Compose (Recommended)

This method builds and runs both the backend and frontend containers.

```
docker-compose up --build
```

Services will be available at:

* Backend API: `http://localhost:8000`
* Frontend UI: `http://localhost:8080`

---

## Running Locally

### 1. Run the Backend

```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Backend runs at `http://localhost:8000`.

### 2. Run the Frontend

```
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`.

---

# API Usage

## 1. Refresh Logs from CloudWatch

Pulls new logs from the configured CloudWatch log group, appends them locally, embeds them, and stores vectors in ChromaDB.

```
POST /refresh
```

Example:

```
curl -X POST http://localhost:8000/refresh
```

---

## 2. Query Logs Using Natural Language (RAG)

```
POST /query
```

Example:

```
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"q": "What is the error code?"}'
```

---

## 3. Get a Log Summary

```
GET /summary
```

Example:

```
curl http://localhost:8000/summary
```

---

## 4. Get a System Health Report

```
GET /health
```

Example:

```
curl http://localhost:8000/health
```

---

## 5. Retrieve Only Error Logs

```
GET /errors
```

Example:

```
curl http://localhost:8000/errors
```

---

# 6. Autonomous Agent API (Tool-Using Agent)

The agent can autonomously:

* Pull logs
* Query logs using RAG
* Summarize logs
* Retrieve error logs
* Generate system health reports
* Combine multiple tools to answer complex questions

### Endpoint

```
POST /agent
```

### Example

```
curl -X POST "http://localhost:8000/agent" \
     -H "Content-Type: application/json" \
     -d '{"query": "Why did errors occur today?"}'
```

The agent decides which tools to invoke, executes them, processes their outputs, and returns a final answer.

---

# Testing the End-to-End Pipeline

### Generate a test log on an EC2 instance or any system sending logs to CloudWatch:

```
sudo logger "CLOUDRAG_TEST: Backup service failed with exit code 17"
```

### Step 1: Refresh logs

```
curl -X POST http://localhost:8000/refresh
```

### Step 2: Query or use the agent

```
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"q": "What failed in the backup service?"}'
```

or

```
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{"query": "Give me a summary of problems today"}'
```

---

