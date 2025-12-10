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
* FastAPI backend with endpoints for refresh, query, summary, health, and errors.
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
├── .env                           # Used for local backend execution
├── docker-compose.yml             # Docker compose for running project
└── Dockerfile
```

Folders `backend/aws_logs/` and `backend/vector_db/` are runtime-only and must remain in `.gitignore`.

---

# Environment Variables

Create a `.env` file inside **backend/**:

```
AWS_ACCESS_KEY_ID=access-key-here
AWS_SECRET_ACCESS_KEY=secret-access-key-here
AWS_REGION=region-here
OPENAI_API_KEY=openai-api-key-here
```
This `.env` file is used when running the backend directly. For Docker, you may need to pass environment variables differently.

---

# Getting Started

There are two ways to run the project: using Docker Compose (recommended) or running the backend and frontend separately.

## Using Docker Compose (Recommended)
This is the easiest way to get started. It will build and run both the backend and frontend containers.

1.  **Ensure you have Docker and Docker Compose installed.**
2.  **Start the services:**
    ```bash
    docker-compose up --build
    ```
    - The backend API will be available at `http://localhost:8000`.
    - The frontend application will be available at `http://localhost:8080`.

## Running Locally

### 1. Run the Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
The backend server runs at `http://localhost:8000`.

### 2. Run the Frontend

```bash
cd frontend
npm install
npm run dev
```
The frontend application runs at `http://localhost:5173`.

Note: The backend includes permissive CORS rules to allow the frontend to connect from `localhost:5173`.

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

## 3. Get a Log Summary
Provides a high-level summary of the latest logs.

```
GET /summary
```

Example:
```bash
curl http://localhost:8000/summary
```
Response:
```json
{
  "total_logs_analyzed": 20,
  "errors": 5,
  "warnings": 2,
  "top_services": ["ssm-agent", "cron", "systemd"],
  "latest_timestamp": "...",
  "llm_summary": "The system is showing multiple errors related to the ssm-agent. Cron jobs are running as expected, but there are some warnings from systemd."
}
```

## 4. Get a Health Report
Provides a health report of the system based on all stored logs.

```
GET /health
```
Example:
```bash
curl http://localhost:8000/health
```
Response:
```json
{
    "total_logs": 150,
    "errors": 10,
    "warnings": 25,
    "services_with_errors": {
        "ssm-agent": 8,
        "postgres": 2
    },
    "top_repeated_patterns": [
        ["ssm-agent", 50],
        ["systemd", 30],
        ["cron", 20]
    ],
    "llm_summary": "The system health is degraded due to a high number of errors from the ssm-agent. Postgres also shows some failures. Other services appear to be running normally."
}
```

## 5. Get Error Logs
Retrieves all logs that are classified as errors.

```
GET /errors
```
Example:
```bash
curl http://localhost:8000/errors
```
Response:
```json
{
    "count": 2,
    "errors": [
        "2025-12-10T10:00:00Z some-service: ERROR: Failed to connect to database.",
        "2025-12-10T10:05:00Z another-service: Failure in processing job 123."
    ]
}
```
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