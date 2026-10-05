import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function formatValue(value) {
  if (value === null || value === undefined) {
    return "—";
  }

  const numericValue = Number(value);

  if (Number.isFinite(numericValue)) {
    return numericValue.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  return String(value);
}

function formatAnswerRow(row) {
  return row
    .map((value, index) => {
      if (index === 0) {
        return String(value ?? "—");
      }

      return formatValue(value);
    })
    .join(" | ");
}

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const analyzeQuestion = async () => {
    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail?.message ||
            data?.detail?.error ||
            "Analysis failed.",
        );
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "Unable to connect to the API.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      analyzeQuestion();
    }
  };

  const rows = result?.rows || [];
  const columns = result?.columns || [];
  const tools = result?.tools_used || [];
  const trace = result?.trace || {};

  const chartUrl = result?.chart_url
    ? `${API_URL}${result.chart_url}`
    : null;

  const resultRowCount = rows.length;
  const toolCount = tools.length;
  const retryCount = trace.sql_retries || 0;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">✦</div>

          <div>
            <div className="brand-title">AI Data Analyst</div>
            <div className="brand-subtitle">
              Ask questions. Analyze data. Get answers.
            </div>
          </div>
        </div>

        <div className="status-pill">
          <span className="status-dot" />
          Local AI
        </div>
      </header>

      <main className="dashboard">
        <section className="hero">
          <div className="hero-copy">
            <span className="eyebrow">NATURAL LANGUAGE ANALYTICS</span>

            <h1>
              Explore your data
              <br />
              <span>with plain English.</span>
            </h1>

            <p>
              Ask business questions and let the analyst inspect your
              PostgreSQL data, generate SQL, perform analysis, and visualize
              the result.
            </p>
          </div>

          <div className="question-card">
            <label htmlFor="question">
              What would you like to know?
            </label>

            <textarea
              id="question"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="e.g. What percentage of revenue came from each category?"
              rows={4}
            />

            <div className="question-footer">
              <span className="shortcut">
                Ctrl + Enter to analyze
              </span>

              <button
                className="analyze-button"
                onClick={analyzeQuestion}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    Analyze
                    <span>→</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </section>

        {error && (
          <section className="error-card">
            <div className="error-icon">!</div>

            <div>
              <strong>Analysis failed</strong>
              <p>{error}</p>
            </div>
          </section>
        )}

        {loading && (
          <section className="loading-card">
            <div className="loading-animation">
              <span />
              <span />
              <span />
            </div>

            <div>
              <strong>Analyzing your question</strong>
              <p>
                Inspecting the schema, generating SQL, and running the
                required analysis...
              </p>
            </div>
          </section>
        )}

        {result && !loading && (
          <section className="results-section">
            <div className="section-heading">
              <div>
                <span className="eyebrow">ANALYSIS RESULT</span>

                <h2>Your answer</h2>

                <p>
                  Generated from the database and executed through the
                  analysis pipeline.
                </p>
              </div>

              <div className="result-badge">
                <span className="status-dot" />
                Complete
              </div>
            </div>

            <div className="metrics-grid">
              <div className="metric-card">
                <span className="metric-label">Rows returned</span>
                <strong>{resultRowCount}</strong>
              </div>

              <div className="metric-card">
                <span className="metric-label">Columns</span>
                <strong>{columns.length}</strong>
              </div>

              <div className="metric-card">
                <span className="metric-label">Tools used</span>
                <strong>{toolCount}</strong>
              </div>

              <div className="metric-card">
                <span className="metric-label">SQL retries</span>
                <strong>{retryCount}</strong>
              </div>
            </div>

            <div className="results-grid">
              <div className="main-results">
                <section className="panel answer-panel">
                  <div className="panel-header">
                    <div>
                      <span className="panel-kicker">ANSWER</span>
                      <h3>What the data says</h3>
                    </div>
                  </div>

                  <div className="question-display">
                    <span>Question</span>
                    <p>{result.question}</p>
                  </div>

                  <div className="answer-content">
                    {rows.length > 0 ? (
                      rows.map((row, index) => (
                        <p key={index}>
                          {formatAnswerRow(row)}
                        </p>
                      ))
                    ) : (
                      <p>{result.answer}</p>
                    )}
                  </div>
                </section>

                {chartUrl && (
                  <section className="panel chart-panel">
                    <div className="panel-header">
                      <div>
                        <span className="panel-kicker">
                          VISUALIZATION
                        </span>
                        <h3>Data visualization</h3>
                      </div>

                      <span className="chart-badge">
                        Generated automatically
                      </span>
                    </div>

                    <div className="chart-container">
                      <img
                        src={chartUrl}
                        alt="Generated data visualization"
                      />
                    </div>
                  </section>
                )}

                <section className="panel table-panel">
                  <div className="panel-header">
                    <div>
                      <span className="panel-kicker">
                        DATABASE RESULT
                      </span>
                      <h3>Raw result</h3>
                    </div>
                  </div>

                  <div className="table-wrapper">
                    <table>
                      <thead>
                        <tr>
                          {columns.map((column) => (
                            <th key={column}>{column}</th>
                          ))}
                        </tr>
                      </thead>

                      <tbody>
                        {rows.map((row, rowIndex) => (
                          <tr key={rowIndex}>
                            {row.map((value, columnIndex) => (
                              <td key={columnIndex}>
                                {formatValue(value)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </section>
              </div>

              <aside className="sidebar-results">
                <section className="panel tools-panel">
                  <div className="panel-header">
                    <div>
                      <span className="panel-kicker">
                        AGENT EXECUTION
                      </span>
                      <h3>Tools used</h3>
                    </div>
                  </div>

                  <div className="tool-list">
                    {tools.map((tool) => (
                      <div className="tool-item" key={tool}>
                        <span className="tool-check">✓</span>
                        <span>{tool}</span>
                      </div>
                    ))}
                  </div>
                </section>

                {trace.total_duration_ms !== undefined && (
                  <section className="panel trace-summary">
                    <div className="panel-header">
                      <div>
                        <span className="panel-kicker">
                          PERFORMANCE
                        </span>
                        <h3>Execution</h3>
                      </div>
                    </div>

                    <div className="trace-stat">
                      <span>Total duration</span>
                      <strong>
                        {Number(trace.total_duration_ms).toFixed(0)} ms
                      </strong>
                    </div>

                    <div className="trace-stat">
                      <span>SQL retries</span>
                      <strong>{retryCount}</strong>
                    </div>

                    <div className="trace-stat">
                      <span>Result rows</span>
                      <strong>{trace.result_rows ?? resultRowCount}</strong>
                    </div>
                  </section>
                )}

                {result.sql && (
                  <section className="panel sql-panel">
                    <div className="panel-header">
                      <div>
                        <span className="panel-kicker">
                          GENERATED SQL
                        </span>
                        <h3>Query</h3>
                      </div>
                    </div>

                    <pre>{result.sql}</pre>
                  </section>
                )}
              </aside>
            </div>
          </section>
        )}

        {!result && !loading && !error && (
          <section className="examples-section">
            <div className="section-heading compact">
              <div>
                <span className="eyebrow">TRY AN EXAMPLE</span>
                <h2>Ask something interesting</h2>
              </div>
            </div>

            <div className="example-grid">
              {[
                "What was our total revenue in 2025?",
                "What percentage of revenue came from each category?",
                "Show the top 5 product categories by revenue in 2025.",
                "Show the quarterly revenue for 2025.",
              ].map((example) => (
                <button
                  className="example-card"
                  key={example}
                  onClick={() => setQuestion(example)}
                >
                  <span>{example}</span>
                  <span className="example-arrow">→</span>
                </button>
              ))}
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <span>AI Data Analyst</span>
        <span>PostgreSQL · Ollama · Qwen · FastAPI · React</span>
      </footer>
    </div>
  );
}

export default App;
