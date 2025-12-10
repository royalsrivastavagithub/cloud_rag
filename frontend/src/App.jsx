import { useState } from 'react';
import './App.css';

function App() {
  const [refreshResult, setRefreshResult] = useState(null);
  const [query, setQuery] = useState('');
  const [queryResult, setQueryResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Helper: Clean markdown-wrapped JSON
  const parseLLMJson = (resultString) => {
    if (!resultString || typeof resultString !== "string") return null;

    try {
      const cleaned = resultString
        .replace(/```json/g, "")
        .replace(/```/g, "")
        .trim();

      return JSON.parse(cleaned);
    } catch (err) {
      console.error("Failed to parse JSON from LLM:", err);
      return null;
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    setError(null);
    setRefreshResult(null);
    setQueryResult(null);

    try {
      const response = await fetch('http://localhost:8000/refresh', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setRefreshResult(data);

    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setRefreshResult(null);
    setQueryResult(null);

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ q: query }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("QUERY RAW RESPONSE:", data);

      const parsed = parseLLMJson(data.result);
      console.log("PARSED JSON:", parsed);

      setQueryResult(parsed);

    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="header">CloudRAG – Log Intelligence</header>

      <section className="feature-section">
        <h2>Refresh Logs</h2>
        <p>Click the button to ingest the latest logs from CloudWatch.</p>
        <button onClick={handleRefresh} disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh Logs'}
        </button>
      </section>

      <section className="feature-section">
        <h2>Query Logs</h2>
        <form onSubmit={handleQuerySubmit} className="query-form">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your question..."
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Querying...' : 'Submit Query'}
          </button>
        </form>
      </section>

      <section className="results-section">
        <h2>Results</h2>

        {loading && <p>Loading...</p>}
        {error && <p className="error-message">Error: {error}</p>}

        {refreshResult && (
          <div>
            <h3>Refresh Status</h3>
            <pre>{JSON.stringify(refreshResult, null, 2)}</pre>
          </div>
        )}

        {queryResult && (
          <div>
            <h3>Answer</h3>
            <p>{queryResult?.answer || "No answer returned."}</p>

            <h3>Evidence</h3>
            {Array.isArray(queryResult?.evidence) &&
            queryResult.evidence.length > 0 ? (
              <ul className="evidence-list">
                {queryResult.evidence.map((item, index) => (
                  <li key={index} className="evidence-item">{item}</li>
                ))}
              </ul>
            ) : (
              <p>No evidence available.</p>
            )}
          </div>
        )}

        {!loading && !error && !refreshResult && !queryResult && (
          <p>Results from your actions will appear here.</p>
        )}
      </section>
    </div>
  );
}

export default App;
