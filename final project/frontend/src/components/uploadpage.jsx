import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { API_BASE_URL } from "../config";

const TASK_META = {
  "Document Conversion": { icon: "📄", desc: "Convert to Markdown format" },
  "Text Summarization": { icon: "📝", desc: "Generate concise summary" },
  "Sentiment Analysis": { icon: "💬", desc: "Analyze tone & emotions" },
  "Topic Modeling": { icon: "🧠", desc: "Discover key themes" },
};

const PROGRESS_STAGES = [
  { label: "Connecting to server…", pct: 15 },
  { label: "Uploading document…", pct: 35 },
  { label: "Running AI models…", pct: 60 },
  { label: "Generating insights…", pct: 85 },
  { label: "Finalizing results…", pct: 95 },
];

function UploadPage({ setAnalysisData }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedTasks, setSelectedTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [progressStage, setProgressStage] = useState(0);

  const taskOptions = Object.keys(TASK_META);

  // Animated progress stages during upload
  useEffect(() => {
    if (!loading) { setProgressStage(0); return; }
    const timers = PROGRESS_STAGES.map((_, i) =>
      setTimeout(() => setProgressStage(i), i * 2200)
    );
    return () => timers.forEach(clearTimeout);
  }, [loading]);

  const handleTaskChange = (task) => {
    if (task === "all") {
      setSelectedTasks(selectedTasks.length === taskOptions.length ? [] : [...taskOptions]);
    } else {
      setSelectedTasks((prev) =>
        prev.includes(task) ? prev.filter((t) => t !== task) : [...prev, task]
      );
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setError("");
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) { setError("Please select a PDF or DOCX file."); return; }
    const fn = selectedFile.name.toLowerCase();
    if (!fn.endsWith(".pdf") && !fn.endsWith(".docx")) {
      setError("Only PDF and DOCX files are allowed."); return;
    }
    if (selectedTasks.length === 0) {
      setError("Please select at least one analysis option."); return;
    }

    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("selected_tasks", JSON.stringify(selectedTasks));

    try {
      const res = await fetch(`${API_BASE_URL}/analyze`, { method: "POST", body: formData });
      if (!res.ok) throw new Error("Server error");
      const data = await res.json();
      if (data.error) setError(data.error);
      else setAnalysisData(data);
    } catch (err) {
      console.error(err);
      setError("Backend connection failed. Make sure FastAPI is running.");
    } finally {
      setLoading(false);
    }
  };

  const allSelected = selectedTasks.length === taskOptions.length;
  const stage = PROGRESS_STAGES[progressStage] || PROGRESS_STAGES[0];

  return (
    <div style={st.page}>
      {/* Decorative shapes */}
      <div style={st.shape1} />
      <div style={st.shape2} />
      <div style={st.shape3} />

      <div style={st.container}>
        {/* Hero */}
        <motion.div
          style={st.hero}
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
        >
          <div style={st.badge}>
            <span style={st.badgeDot} />
            AI-POWERED ANALYSIS
          </div>
          <h1 style={st.title}>
            Document <span style={{ color: "#7c3aed" }}>Intelligence</span> Analyzer
          </h1>
          <p style={st.subtitle}>
            Upload your document and extract structured insights — conversion, summarization,
            sentiment analysis, and topic modeling powered by AI.
          </p>
        </motion.div>

        {/* Upload Card */}
        <motion.div
          style={st.card}
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1, ease: [0.4, 0, 0.2, 1] }}
        >
          <div style={st.cardHead}>
            <span style={st.step}>1</span>
            <div>
              <h2 style={st.cardTitle}>Upload Document</h2>
              <p style={st.cardDesc}>Select a PDF or DOCX file to analyze</p>
            </div>
          </div>

          <label
            style={{
              ...st.dropZone,
              borderColor: dragOver ? "#8b5cf6" : "#d8d5f2",
              background: dragOver ? "rgba(139,92,246,0.05)" : "#fafaff",
              transform: dragOver ? "scale(1.01)" : "scale(1)",
            }}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={(e) => { if (e.target.files[0]) { setSelectedFile(e.target.files[0]); setError(""); } }}
              style={{ display: "none" }}
            />
            <div style={st.dropIcon}>
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <p style={st.dropTitle}>
              Drag & drop or <span style={{ color: "#7c3aed", fontWeight: 700 }}>browse</span>
            </p>
            <p style={st.dropHint}>PDF or DOCX • Max 50 MB</p>
          </label>

          {selectedFile && (
            <motion.div
              style={st.fileRow}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div style={st.fileIconBox}>📄</div>
              <div style={{ flex: 1 }}>
                <p style={st.fileName}>{selectedFile.name}</p>
                <p style={st.fileMeta}>
                  {selectedFile.name.split(".").pop().toUpperCase()} • {(selectedFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
              <button onClick={() => setSelectedFile(null)} style={st.fileRemove} aria-label="Remove file">✕</button>
            </motion.div>
          )}
        </motion.div>

        {/* Task Selection Card */}
        <motion.div
          style={st.card}
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2, ease: [0.4, 0, 0.2, 1] }}
        >
          <div style={st.cardHead}>
            <span style={st.step}>2</span>
            <div>
              <h2 style={st.cardTitle}>Choose Analysis Tasks</h2>
              <p style={st.cardDesc}>Select one or more processing modules</p>
            </div>
          </div>

          <button
            onClick={() => handleTaskChange("all")}
            style={{
              ...st.allBtn,
              background: allSelected ? "linear-gradient(135deg,#7c3aed,#a855f7)" : "#fff",
              color: allSelected ? "#fff" : "#64748b",
              borderColor: allSelected ? "transparent" : "#e2e8f0",
            }}
          >
            {allSelected ? "✓ All Selected" : "Select All"}
          </button>

          <div style={st.taskGrid}>
            {taskOptions.map((task, idx) => {
              const active = selectedTasks.includes(task);
              const meta = TASK_META[task];
              return (
                <motion.button
                  key={task}
                  onClick={() => handleTaskChange(task)}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.05 * idx }}
                  whileHover={{ y: -2, boxShadow: "0 6px 20px rgba(139,92,246,0.12)" }}
                  whileTap={{ scale: 0.98 }}
                  style={{
                    ...st.taskCard,
                    borderColor: active ? "#8b5cf6" : "#eee",
                    background: active ? "linear-gradient(145deg,#faf5ff,#f5f3ff)" : "#fff",
                    boxShadow: active
                      ? "0 0 0 2px rgba(139,92,246,0.15), 0 4px 16px rgba(139,92,246,0.08)"
                      : "0 2px 8px rgba(15,23,42,0.04)",
                  }}
                >
                  <span style={st.taskIcon}>{meta.icon}</span>
                  <div style={{ flex: 1, textAlign: "left" }}>
                    <p style={{ ...st.taskName, color: active ? "#5b21b6" : "#1e293b" }}>{task}</p>
                    <p style={st.taskDesc}>{meta.desc}</p>
                  </div>
                  <div style={{
                    ...st.check,
                    background: active ? "#7c3aed" : "#f1f5f9",
                    borderColor: active ? "#7c3aed" : "#e2e8f0",
                    color: active ? "#fff" : "transparent",
                  }}>✓</div>
                </motion.button>
              );
            })}
          </div>
        </motion.div>

        {/* Submit */}
        <motion.div
          style={{ textAlign: "center", marginTop: "4px" }}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <button
            onClick={handleUpload}
            disabled={loading}
            style={{
              ...st.submitBtn,
              opacity: loading ? 0.75 : 1,
              cursor: loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? (
              <span style={{ display: "flex", alignItems: "center", gap: 10, justifyContent: "center" }}>
                <span style={st.spinner} />
                Analyzing...
              </span>
            ) : "✨ Analyze Document"}
          </button>
          <p style={st.hint}>
            {selectedFile ? `Ready to analyze ${selectedFile.name}` : "Upload a file and select tasks to begin"}
          </p>
        </motion.div>

        {/* Multi-stage Loading bar */}
        {loading && (
          <motion.div
            style={st.loadBar}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <div style={st.loadTrack}>
              <motion.div
                style={st.loadFill}
                initial={{ width: "0%" }}
                animate={{ width: `${stage.pct}%` }}
                transition={{ duration: 1.2, ease: [0.4, 0, 0.2, 1] }}
              />
            </div>
            <div style={st.loadStageRow}>
              <p style={st.loadText}>{stage.label}</p>
              <span style={st.loadPct}>{stage.pct}%</span>
            </div>
            <div style={st.loadSteps}>
              {PROGRESS_STAGES.map((s, i) => (
                <div key={i} style={{
                  ...st.loadDot,
                  background: i <= progressStage ? "#7c3aed" : "#e2e8f0",
                  transform: i === progressStage ? "scale(1.3)" : "scale(1)",
                }} />
              ))}
            </div>
          </motion.div>
        )}

        {/* Error */}
        {error && (
          <motion.div
            style={st.errorBox}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <span style={{ fontSize: 16 }}>⚠️</span>
            <p style={{ margin: 0 }}>{error}</p>
          </motion.div>
        )}
      </div>
    </div>
  );
}

// ── Styles ──────────────────────────────────────────────────────
const st = {
  page: {
    minHeight: "100vh", display: "flex", justifyContent: "center", alignItems: "center",
    padding: "40px 20px", position: "relative", overflow: "hidden",
  },
  shape1: {
    position: "absolute", width: 420, height: 420, borderRadius: "50%",
    background: "radial-gradient(circle, rgba(139,92,246,0.08), transparent 70%)",
    top: "-8%", left: "-8%", pointerEvents: "none",
  },
  shape2: {
    position: "absolute", width: 350, height: 350, borderRadius: "50%",
    background: "radial-gradient(circle, rgba(236,72,153,0.06), transparent 70%)",
    bottom: "-6%", right: "-6%", pointerEvents: "none",
  },
  shape3: {
    position: "absolute", width: 200, height: 200, borderRadius: "50%",
    background: "radial-gradient(circle, rgba(59,130,246,0.05), transparent 70%)",
    top: "45%", right: "15%", pointerEvents: "none",
  },
  container: {
    width: "100%", maxWidth: 680, position: "relative", zIndex: 2,
  },
  hero: { textAlign: "center", marginBottom: 36 },
  badge: {
    display: "inline-flex", alignItems: "center", gap: 8,
    background: "linear-gradient(135deg, #ede9fe, #fce7f3)",
    color: "#7c3aed", padding: "7px 18px", borderRadius: 999,
    fontWeight: 700, fontSize: 11, letterSpacing: 1.8, marginBottom: 18,
  },
  badgeDot: {
    width: 6, height: 6, borderRadius: "50%", background: "#8b5cf6", display: "inline-block",
    animation: "pulse 2s ease-in-out infinite",
  },
  title: {
    fontSize: "clamp(28px, 5vw, 44px)", fontWeight: 800, color: "#0f172a", marginBottom: 14,
    letterSpacing: -1.5, lineHeight: 1.15,
  },
  subtitle: {
    fontSize: 16, color: "#64748b", lineHeight: 1.8, maxWidth: 520, margin: "0 auto",
  },
  card: {
    background: "rgba(255,255,255,0.82)", backdropFilter: "blur(20px)",
    borderRadius: 22, padding: "26px 28px", marginBottom: 18,
    border: "1px solid rgba(226,232,240,0.8)",
    boxShadow: "0 8px 30px rgba(15,23,42,0.06), 0 1px 3px rgba(15,23,42,0.04)",
  },
  cardHead: { display: "flex", alignItems: "center", gap: 14, marginBottom: 20 },
  step: {
    width: 34, height: 34, borderRadius: 10,
    background: "linear-gradient(135deg,#7c3aed,#a855f7)",
    color: "#fff", display: "flex", alignItems: "center", justifyContent: "center",
    fontWeight: 800, fontSize: 14, flexShrink: 0,
  },
  cardTitle: { fontSize: 18, fontWeight: 700, color: "#0f172a", margin: 0 },
  cardDesc: { fontSize: 13, color: "#94a3b8", margin: "2px 0 0 0" },

  dropZone: {
    display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
    padding: "36px 20px", borderRadius: 16, border: "2px dashed #d8d5f2",
    cursor: "pointer", textAlign: "center", transition: "all 0.25s ease",
  },
  dropIcon: {
    width: 56, height: 56, borderRadius: 14,
    background: "linear-gradient(135deg, #ede9fe, #f5f3ff)",
    display: "flex", alignItems: "center", justifyContent: "center",
    marginBottom: 14, border: "1px solid #e9e5f5",
  },
  dropTitle: { fontSize: 15, color: "#475569", marginBottom: 4, fontWeight: 500 },
  dropHint: { fontSize: 12, color: "#94a3b8" },

  fileRow: {
    marginTop: 14, display: "flex", alignItems: "center", gap: 12,
    background: "#f8f7ff", padding: "12px 16px", borderRadius: 14, border: "1px solid #ede9fe",
  },
  fileIconBox: { fontSize: 24, flexShrink: 0 },
  fileName: { fontSize: 14, fontWeight: 600, color: "#1e293b", margin: 0 },
  fileMeta: { fontSize: 12, color: "#94a3b8", margin: "2px 0 0 0" },
  fileRemove: {
    background: "#fee2e2", border: "1px solid #fecaca", color: "#ef4444",
    borderRadius: 8, width: 28, height: 28, display: "flex", alignItems: "center",
    justifyContent: "center", cursor: "pointer", fontSize: 11, fontWeight: 700, flexShrink: 0,
  },

  allBtn: {
    width: "100%", padding: "10px 16px", borderRadius: 12,
    border: "1.5px solid #e2e8f0", fontWeight: 600, fontSize: 13,
    cursor: "pointer", marginBottom: 14, transition: "all 0.2s ease",
  },
  taskGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
    gap: 12,
  },
  taskCard: {
    display: "flex", alignItems: "center", gap: 12, padding: "14px 16px",
    borderRadius: 14, border: "1.5px solid #eee", cursor: "pointer",
    transition: "all 0.2s ease", textAlign: "left", background: "#fff",
  },
  taskIcon: { fontSize: 22, flexShrink: 0 },
  taskName: { fontSize: 13, fontWeight: 700, margin: 0 },
  taskDesc: { fontSize: 11, color: "#94a3b8", margin: "2px 0 0 0" },
  check: {
    width: 22, height: 22, borderRadius: 7, border: "2px solid #e2e8f0",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: 11, fontWeight: 800, flexShrink: 0, transition: "all 0.2s ease",
  },

  submitBtn: {
    background: "linear-gradient(135deg,#7c3aed,#a855f7)",
    color: "#fff", border: "none", padding: "15px 40px", borderRadius: 14,
    fontSize: 16, fontWeight: 700, width: "100%", maxWidth: 380,
    boxShadow: "0 8px 28px rgba(124,58,237,0.25), 0 2px 6px rgba(0,0,0,0.08)",
    letterSpacing: 0.3, transition: "all 0.25s ease",
  },
  spinner: {
    width: 16, height: 16, border: "2.5px solid rgba(255,255,255,0.3)",
    borderTop: "2.5px solid #fff", borderRadius: "50%",
    display: "inline-block", animation: "spin 0.8s linear infinite",
  },
  hint: { color: "#94a3b8", fontSize: 13, marginTop: 10, fontWeight: 500 },

  loadBar: { marginTop: 22, textAlign: "center" },
  loadTrack: {
    width: "100%", height: 6, background: "#ede9fe", borderRadius: 999,
    overflow: "hidden", marginBottom: 12,
  },
  loadFill: {
    height: "100%", borderRadius: 999,
    background: "linear-gradient(90deg,#7c3aed,#a855f7,#ec4899,#7c3aed)",
    backgroundSize: "200% 100%", animation: "shimmer 1.5s linear infinite",
  },
  loadStageRow: {
    display: "flex", justifyContent: "space-between", alignItems: "center",
    marginBottom: 8,
  },
  loadText: { color: "#64748b", fontWeight: 500, fontSize: 13, margin: 0 },
  loadPct: { color: "#7c3aed", fontWeight: 700, fontSize: 13 },
  loadSteps: {
    display: "flex", justifyContent: "center", gap: 8, marginTop: 4,
  },
  loadDot: {
    width: 8, height: 8, borderRadius: "50%", transition: "all 0.4s ease",
  },

  errorBox: {
    marginTop: 20, background: "#fef2f2", color: "#dc2626",
    padding: "12px 18px", borderRadius: 14, border: "1px solid #fecaca",
    display: "flex", alignItems: "center", gap: 10, fontWeight: 500, fontSize: 13,
  },
};

export default UploadPage;