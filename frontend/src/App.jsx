import React, { useState } from "react";
import "./App.css";

export default function App() {
  const [query, setQuery] = useState("");
  const [queryResult, setQueryResult] = useState(null);
  const [summary, setSummary] = useState(null);
  const [health, setHealth] = useState(null);
  const [errors, setErrors] = useState(null);
  const [refreshStatus, setRefreshStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const API = "http://localhost:8000";

  async function callAPI(endpoint, method = "GET", body = null) {
    setLoading(true);
    try {
      const res = await fetch(`${API}${endpoint}`, {
        method,
        headers: { "Content-Type": "application/json" },
        body: body ? JSON.stringify(body) : null
      });
      return await res.json();
    } catch (err) {
      console.error(err);
      return { error: "Request failed" };
    } finally {
      setLoading(false);
    }
  }

  async function runQuery() {
    setQueryResult(await callAPI("/query", "POST", { q: query }));
  }

  async function runSummary() {
    setSummary(await callAPI("/summary"));
  }

  async function runHealth() {
    setHealth(await callAPI("/health"));
  }

  async function runErrors() {
    setErrors(await callAPI("/errors"));
  }

  async function runRefresh() {
    setRefreshStatus(await callAPI("/refresh", "POST"));
  }

  return (
    <div className="container">
      <h1 className="title">CloudRAG – Log Analysis Dashboard</h1>

      {loading && <p className="loading">⏳ Loading...</p>}

      {/* Query Section */}
      <div className="card">
        <h2>Ask a question about logs</h2>

        <input
          className="input"
          placeholder="e.g. Why did Postgres crash?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        <button className="btn" onClick={runQuery}>Query Logs</button>

        {queryResult && (
          <pre className="pre">{JSON.stringify(queryResult, null, 2)}</pre>
        )}
      </div>

      {/* Summary */}
      <div className="card">
        <h2>Log Summary</h2>
        <button className="btn" onClick={runSummary}>Get Summary</button>
        {summary && (
          <pre className="pre">{JSON.stringify(summary, null, 2)}</pre>
        )}
      </div>

      {/* Health */}
      <div className="card">
        <h2>Health Report</h2>
        <button className="btn" onClick={runHealth}>Get Health Status</button>
        {health && (
          <pre className="pre">{JSON.stringify(health, null, 2)}</pre>
        )}
      </div>

      {/* Error Logs */}
      <div className="card">
        <h2>Error Logs</h2>
        <button className="btn" onClick={runErrors}>Get Errors</button>
        {errors && (
          <pre className="pre">{JSON.stringify(errors, null, 2)}</pre>
        )}
      </div>

      {/* Ingest Logs */}
      <div className="card">
        <h2>Pull & Ingest Logs</h2>
        <button className="btn refresh" onClick={runRefresh}>
          Refresh Logs
        </button>
        {refreshStatus && (
          <pre className="pre">{JSON.stringify(refreshStatus, null, 2)}</pre>
        )}
      </div>
    </div>
  );
}
