import { useState } from "react";

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const analyzeQuestion = async () => {
    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: question.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail?.message ||
          data.detail ||
          "Analysis failed."
        );
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>AI Data Analyst</h1>

      <p>
        Ask a natural-language question about your business data.
      </p>

      <textarea
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        placeholder="What was the total revenue in 2025?"
        rows={4}
      />

      <br />

      <button
        onClick={analyzeQuestion}
        disabled={loading || !question.trim()}
      >
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      {error && (
        <div>
          <h2>Error</h2>
          <p>{error}</p>
        </div>
      )}

      {result && (
        <div>
          <h2>Answer</h2>

          <pre>{result.answer}</pre>

          <h2>SQL</h2>

          <pre>{result.sql}</pre>

          <h2>Tools Used</h2>

          <pre>
            {result.tools_used.join(", ")}
          </pre>

          <h2>Execution Trace</h2>

          <pre>
            {JSON.stringify(result.trace, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App;
