---

# **CloudRAG – AI-Powered EC2 Log Analysis Using RAG**

CloudRAG is a lightweight, end-to-end Retrieval-Augmented Generation (RAG) system designed to analyze EC2 instance logs using CloudWatch, OpenAI embeddings, ChromaDB, and FastAPI.

It enables natural-language log analysis such as:

* “Which service failed?”
* “What error code appears in the logs?”
* “Did Postgres fail today?”

This project demonstrates real-world integration of AWS logging pipelines, vector search, LangChain components, and LLM reasoning.

---

# **Features**

* Pull EC2 logs directly from CloudWatch.
* Store logs locally for inspection.
* Embed logs using OpenAI embeddings.
* Store vector embeddings in ChromaDB.
* Natural-language log search using RAG retrieval.
* FastAPI backend with endpoints for refresh, query, summary, health, and errors.
* React-based frontend dashboard.
* Clean architecture with minimal dependencies.

---

# **Project Structure**

```
cloud_rag/
│
├── backend/
│   ├── controllers/
│   │   ├── log_controller.py      # Pull logs from CloudWatch
│   │   ├── vector_controller.py   # OpenAI embeddings + Chroma storage
│   │   └── rag_controller.py      # Retrieval + LLM reasoning
│   ├── aws_logs/                  # Raw logs (ignored)
│   ├── vector_db/                 # Chroma DB files (ignored)
│   ├── main.py                    # FastAPI server
│   └── requirements.txt
│
├── frontend/
│   ├── src/App.jsx                # React UI
│   ├── src/App.css
│   └── vite.config.js
│
├── .env                           # Local backend environment variables
├── docker-compose.yml             # Docker Compose for full stack
└── Dockerfile
```

`backend/aws_logs/` and `backend/vector_db/` are runtime-only and must remain in `.gitignore`.

---

# **Environment Variables**

Create a `.env` file in **backend/**:

```
AWS_ACCESS_KEY_ID=access-key-here
AWS_SECRET_ACCESS_KEY=secret-access-key-here
AWS_REGION=region-here
OPENAI_API_KEY=openai-api-key-here
```

This file is used for local backend execution.
For Docker, environment variables may need to be passed differently (e.g., via Compose).

---

# **Getting Started**

You can run the project via Docker Compose (recommended) or run the backend and frontend manually.

---

## **Using Docker Compose (Recommended)**

This method builds and runs both the backend and frontend containers.

1. Ensure Docker and Docker Compose are installed.
2. Start the services:

   ```bash
   docker-compose up --build
   ```

Services will be available at:

* **Backend API:** `http://localhost:8000`
* **Frontend UI:** `http://localhost:8080`

---

## **Running Locally**

### **1. Run the Backend**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Backend runs at `http://localhost:8000`.

### **2. Run the Frontend**

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

The backend includes permissive CORS rules to allow requests from this port.

---

# **API Usage**

## **1. Refresh Logs from CloudWatch**

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

---

## **2. Query Logs Using Natural Language**

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

## **3. Get a Log Summary**

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
  "llm_summary": "The system is showing multiple errors related to the ssm-agent..."
}
```

---

## **4. Get a Health Report**

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
  "llm_summary": "The system health is degraded due to a high number of errors..."
}
```

---

## **5. Retrieve Only Error Logs**

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

# **Testing the End-to-End Pipeline**

### **Generate a test log on an EC2 instance:**

```bash
sudo logger "RAG_TEST_12345: Backup service failed with exit code 17"
```

### **Step 1: Refresh logs**

```bash
curl -X POST http://localhost:8000/refresh
```

### **Step 2: Query logs**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"q": "What failed in the backup service?"}'
```

---

# **Future Improvements**

### **Retrieval & LLM Enhancements**

* Multi-turn questions.
* Time-based retrieval (e.g., last 15 minutes, last hour).
* Log severity classification (INFO/WARN/ERROR).

### **Observability Features**

* Detect frequent restarts or anomalies.
* Summaries of critical issues.
* Alerting via SNS or Slack.

### **Frontend Enhancements**

* Interactive system health dashboard.
* Search history.
* Filter logs by service or instance.

---
