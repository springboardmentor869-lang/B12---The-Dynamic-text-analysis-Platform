import { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [analysisType, setAnalysisType] = useState("convert");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleAnalyze = async () => {
    if (!file) {
      alert("Upload a file first!");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`http://127.0.0.1:8000/${analysisType}`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      setResult(data.result || data.text || JSON.stringify(data));
    } catch (error) {
      alert("Error connecting to backend");
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <div className="card">
        <h2>📄 Document Analyzer</h2>
        <p>Upload your document and choose analysis type</p>

        <div className="upload-box">
          <input type="file" onChange={handleFileChange} />
          {file && <span className="file-name">{file.name}</span>}
        </div>

        {file && <p className="success">✔ File selected</p>}

        <select
          value={analysisType}
          onChange={(e) => setAnalysisType(e.target.value)}
        >
          <option value="convert">Convert</option>
          <option value="summarize">Summarize</option>
          <option value="sentiment">Sentiment</option>
          <option value="topic">Topic</option>
        </select>

        <button onClick={handleAnalyze}>
          {loading ? "Analyzing..." : "Analyze Document 📄"}
        </button>

        {result && (
          <div className="output">
            {result}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;