import { useState } from "react";

const TASK_META = {
  "Document Conversion": { 
    icon: <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>, 
    desc: "Convert to Markdown" 
  },
  "Text Summarization": { 
    icon: <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="21" y1="10" x2="3" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="14" y1="18" x2="3" y2="18"/></svg>, 
    desc: "Generate summary" 
  },
  "Sentiment Analysis": { 
    icon: <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>, 
    desc: "Analyze tone & emotion" 
  },
  "Topic Modeling": { 
    icon: <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>, 
    desc: "Discover key themes" 
  },
};

function UploadPage({ setAnalysisData }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedTasks, setSelectedTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dragOver, setDragOver] = useState(false);

  const taskOptions = Object.keys(TASK_META);

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
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) { setError("Please select a valid document."); return; }
    const fn = selectedFile.name.toLowerCase();
    if (!fn.endsWith(".pdf") && !fn.endsWith(".docx")) {
      setError("Only PDF and DOCX files are allowed."); return;
    }
    if (selectedTasks.length === 0) {
      setError("Please select at least one analysis task."); return;
    }

    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("selected_tasks", JSON.stringify(selectedTasks));

    try {
      const res = await fetch("http://127.0.0.1:8000/analyze", { method: "POST", body: formData });
      if (!res.ok) throw new Error("Server error");
      const data = await res.json();
      if (data.error) setError(data.error);
      else setAnalysisData(data);
    } catch (err) {
      console.error(err);
      setError("Backend connection failed.");
    } finally {
      setLoading(false);
    }
  };

  const allSelected = selectedTasks.length === taskOptions.length;

  return (
    <div style={st.splitPage}>
      
      {/* ── Left Pane: Thin Branding Sidebar ── */}
      <div style={st.leftPane}>
        <div style={st.leftContent}>
          <div style={st.logoBox}>
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
              <path d="M2 12h20"/>
            </svg>
          </div>
          <h1 style={st.heroTitle}>Smart Document Analyzer</h1>
          <p style={st.heroDesc}>
            Unlock intelligent AI insights instantly.
          </p>
          <div style={st.featuresList}>
             <div style={st.featureItem}>
               <span style={st.checkIcon}>✓</span> Fast Processing
             </div>
             <div style={st.featureItem}>
               <span style={st.checkIcon}>✓</span> Secured Analysis
             </div>
          </div>
        </div>
      </div>

      {/* ── Right Pane: Massive Workspace ── */}
      <div style={st.rightPane}>
        <div style={st.workspaceContainer}>
          
          <div style={{ marginBottom: "28px" }}>
            <h2 style={st.sectionTitle}>Get Started</h2>
            <p style={st.sectionSub}>Upload your document and configure parameters.</p>
          </div>

          <label
            style={{
              ...st.dropZone,
              borderColor: dragOver ? "var(--primary)" : "var(--border-color)",
              background: dragOver ? "var(--primary-bg)" : "var(--bg-card)",
              boxShadow: dragOver ? "inset 0 0 0 1px var(--primary)" : "none",
            }}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={(e) => { if (e.target.files[0]) setSelectedFile(e.target.files[0]); }}
              style={{ display: "none" }}
            />
            <div style={st.dropIcon}>
              <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <p style={st.dropTitle}>
              Click to browse or Drag & drop file
            </p>
            <p style={st.dropHint}>PDF & DOCX files (Up to 50 MB)</p>
          </label>

          {selectedFile && (
            <div style={st.fileRow}>
              <div style={st.fileIconBox}>📄</div>
              <div style={{ flex: 1, overflow: "hidden" }}>
                <p style={st.fileName}>{selectedFile.name}</p>
                <p style={st.fileMeta}>
                  {selectedFile.name.split(".").pop().toUpperCase()} • {(selectedFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
              <button className="btn-secondary interactive-card" onClick={(e) => { e.preventDefault(); setSelectedFile(null); }} style={st.fileRemove}>✕</button>
            </div>
          )}

          <div style={{ marginTop: "36px", paddingTop: "28px", borderTop: "1px solid var(--border-color)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <h3 style={st.sectionTitleList}>Analysis Tasks</h3>
              <button
                className="btn-secondary interactive-card"
                onClick={() => handleTaskChange("all")}
                style={{
                  ...st.allBtnSmall,
                  background: allSelected ? "var(--primary)" : "transparent",
                  color: allSelected ? "#fff" : "var(--text-main)",
                  borderColor: allSelected ? "var(--primary)" : "var(--border-color)",
                }}
              >
                {allSelected ? "✓ Clear All" : "Select All"}
              </button>
            </div>

            <div style={st.taskGrid}>
              {taskOptions.map((task) => {
                const active = selectedTasks.includes(task);
                const meta = TASK_META[task];
                return (
                  <button
                    key={task}
                    className="interactive-card btn-secondary"
                    onClick={() => handleTaskChange(task)}
                    style={{
                      ...st.taskCard,
                      borderColor: active ? "var(--primary)" : "var(--border-color)",
                      background: active ? "var(--primary-bg)" : "var(--bg-card)",
                    }}
                  >
                    <span style={st.taskIcon}>{meta.icon}</span>
                    <div style={{ flex: 1, textAlign: "left" }}>
                      <p style={{ ...st.taskName, color: active ? "var(--primary)" : "var(--text-main)" }}>{task}</p>
                      <p style={st.taskDesc}>{meta.desc}</p>
                    </div>
                    <div style={{
                      width: "20px",
                      height: "20px",
                      borderRadius: "50%",
                      border: active ? "6px solid var(--primary)" : "1.5px solid var(--text-light)",
                      backgroundColor: "transparent",
                      transition: "all 0.2s ease",
                      flexShrink: 0
                    }} />
                  </button>
                );
              })}
            </div>
          </div>

          <div style={{ marginTop: "40px" }}>
            <button
              className="btn-primary"
              onClick={handleUpload}
              disabled={loading}
              style={{
                ...st.submitBtn,
                opacity: loading ? 0.7 : 1,
                cursor: loading ? "not-allowed" : "pointer",
              }}
            >
              {loading ? (
                <span style={{ display: "flex", alignItems: "center", gap: 10, justifyContent: "center" }}>
                  <span style={st.spinner} />
                  Analyzing...
                </span>
              ) : "Analyze Document"}
            </button>
          </div>

          {loading && (
            <div style={st.loadBar}>
              <div style={st.loadTrack}>
                <div style={st.loadFill} />
              </div>
              <p style={st.loadText}>Processing document utilizing AI...</p>
            </div>
          )}

          {error && (
            <div style={st.errorBox}>
              <span style={{ fontSize: 16 }}>⚠️</span>
              <p style={{ margin: 0 }}>{error}</p>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

// ── Styles ──────────────────────────────────────────────────────
const st = {
  splitPage: {
    display: "flex",
    minHeight: "100vh",
    width: "100%",
    backgroundColor: "var(--bg-app)",
    flexDirection: "row", // Desktop side-by-side
    flexWrap: "wrap",
  },

  /* Left Pane - THIN SIDEBAR */
  leftPane: {
    flex: "0 0 280px", // Fixed thin size
    backgroundColor: "var(--primary)",
    color: "#ffffff",
    display: "flex",
    flexDirection: "column",
    justifyContent: "flex-start",
    padding: "60px 40px",
    position: "relative",
    borderRight: "1px solid rgba(0,0,0,0.1)",
  },
  leftContent: {
    width: "100%",
    animation: "fadeIn 0.6s ease",
  },
  logoBox: {
    width: "48px",
    height: "48px",
    backgroundColor: "rgba(255,255,255,0.18)",
    borderRadius: "14px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "32px",
    backdropFilter: "blur(10px)",
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
  },
  heroTitle: {
    fontSize: "28px", 
    fontWeight: "800",
    letterSpacing: "-0.5px",
    lineHeight: "1.2",
    marginBottom: "16px",
    color: "#ffffff"
  },
  heroDesc: {
    fontSize: "15px",
    lineHeight: "1.6",
    color: "rgba(255,255,255,0.9)",
    marginBottom: "36px",
  },
  featuresList: {
    display: "flex",
    flexDirection: "column",
    gap: "14px",
  },
  featureItem: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    fontSize: "13px",
    fontWeight: "600",
    color: "rgba(255,255,255,0.95)",
  },
  checkIcon: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    width: "20px",
    height: "20px",
    borderRadius: "50%",
    backgroundColor: "rgba(255,255,255,0.25)",
    fontSize: "11px",
    fontWeight: "800",
  },

  /* Right Pane - HUGE WORKSPACE */
  rightPane: {
    flex: "1 1 auto", // Fills remaining space
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "60px 24px",
  },
  workspaceContainer: {
    width: "100%",
    maxWidth: "800px", // Extremely wide
    animation: "fadeIn 0.5s ease",
  },
  sectionTitle: { fontSize: "32px", fontWeight: "800", color: "var(--text-main)", margin: "0 0 8px 0", letterSpacing: "-0.5px" },
  sectionTitleList: { fontSize: "18px", fontWeight: "700", color: "var(--text-main)", margin: "0" },
  sectionSub: { fontSize: "16px", color: "var(--text-muted)", margin: "0" },

  dropZone: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "64px 24px",
    borderRadius: "20px",
    border: "2px dashed var(--border-color)",
    cursor: "pointer",
    textAlign: "center",
    transition: "all 0.2s ease",
    backgroundColor: "var(--bg-card)",
  },
  dropIcon: {
    width: "72px",
    height: "72px",
    borderRadius: "18px",
    backgroundColor: "var(--badge-bg)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "20px",
  },
  dropTitle: { fontSize: "18px", color: "var(--text-main)", marginBottom: "6px", fontWeight: "600" },
  dropHint: { fontSize: "14px", color: "var(--text-light)" },

  fileRow: {
    marginTop: "20px",
    display: "flex",
    alignItems: "center",
    gap: "16px",
    background: "var(--bg-card)",
    padding: "18px 24px",
    borderRadius: "16px",
    border: "1px solid var(--border-color)",
    boxShadow: "var(--shadow-sm)"
  },
  fileIconBox: { fontSize: "32px", flexShrink: 0 },
  fileName: { fontSize: "16px", fontWeight: "600", color: "var(--text-main)", margin: "0 0 2px 0", textOverflow: "ellipsis", whiteSpace: "nowrap", overflow: "hidden" },
  fileMeta: { fontSize: "14px", color: "var(--text-light)", margin: "0" },
  fileRemove: {
    borderRadius: "8px",
    width: "36px",
    height: "36px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "13px",
    fontWeight: "700",
    flexShrink: 0,
    border: "1px solid var(--border-color)",
    padding: 0,
  },

  allBtnSmall: {
    padding: "8px 16px",
    borderRadius: "8px",
    fontSize: "13px",
    fontWeight: "600",
    border: "1px solid var(--border-color)",
    cursor: "pointer",
    transition: "all 0.2s ease"
  },
  taskGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" },
  taskCard: {
    display: "flex",
    alignItems: "flex-start",
    gap: "14px",
    padding: "16px 18px",
    borderRadius: "12px",
    border: "1px solid var(--border-color)",
    textAlign: "left",
  },
  taskIcon: { fontSize: "22px", flexShrink: 0, marginTop: "2px" },
  taskName: { fontSize: "15px", fontWeight: "600", margin: "0 0 4px 0" },
  taskDesc: { fontSize: "13px", color: "var(--text-muted)", margin: "0", lineHeight: "1.4" },

  submitBtn: {
    padding: "20px 24px",
    borderRadius: "16px",
    fontSize: "18px",
    fontWeight: "700",
    width: "100%",
    letterSpacing: "0.2px",
    border: "none",
  },
  spinner: {
    width: "20px",
    height: "20px",
    border: "3px solid rgba(255,255,255,0.3)",
    borderTop: "3px solid #fff",
    borderRadius: "50%",
    display: "inline-block",
    animation: "spin 0.8s linear infinite",
  },

  loadBar: { marginTop: "24px", textAlign: "center" },
  loadTrack: {
    width: "100%",
    height: "8px",
    background: "var(--border-color)",
    borderRadius: "999px",
    overflow: "hidden",
    marginBottom: "14px",
  },
  loadFill: {
    width: "60%",
    height: "100%",
    borderRadius: "999px",
    background: "var(--primary)",
  },
  loadText: { color: "var(--text-muted)", fontWeight: "500", fontSize: "15px" },

  errorBox: {
    marginTop: "24px",
    background: "var(--danger-bg)",
    color: "var(--danger-text)",
    padding: "16px",
    borderRadius: "12px",
    border: "1px solid var(--danger-border)",
    display: "flex",
    alignItems: "center",
    gap: "12px",
    fontWeight: "500",
    fontSize: "15px",
  },
};

export default UploadPage;