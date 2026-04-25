import { useEffect, useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from "recharts";

/* ── Sentiment Colors ────────────────────────────────────────── */
const SC = {
  Positive: { bar: "var(--primary)", bg: "var(--primary-bg)", border: "var(--primary)", text: "var(--primary)", light: "var(--primary-bg)" },
  Neutral:  { bar: "var(--text-muted)", bg: "var(--badge-bg)", border: "var(--text-muted)", text: "var(--text-muted)", light: "var(--badge-bg)" },
  Negative: { bar: "var(--danger-text)", bg: "var(--danger-bg)", border: "var(--danger-border)", text: "var(--danger-text)", light: "var(--danger-bg)" },
};
const sentimentOf = (label) => {
  const k = (label || "").charAt(0).toUpperCase() + (label || "").slice(1).toLowerCase();
  return SC[k] || SC.Neutral;
};

/* ── Topic Colors ────────────────────────────────────────────── */
const TOPIC_COLORS = ["var(--primary)", "#10b981", "#f59e0b", "#6366f1", "#ef4444", "#14b8a6", "#8b5cf6", "#ec4899"];

/* ── Custom Tooltip ──────────────────────────────────────────── */
const LightTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "var(--bg-card)", borderRadius: 12, padding: "10px 16px",
      boxShadow: "var(--shadow-lg)", border: "1px solid var(--border-color)",
    }}>
      <p style={{ color: "var(--text-light)", fontSize: 12, margin: "0 0 3px 0" }}>{label}</p>
      <p style={{ color: "var(--text-main)", fontSize: 15, fontWeight: 700, margin: 0 }}>{payload[0].value}</p>
    </div>
  );
};

/* ═════════════════════════════════════════════════════════════ */
/*  MAIN COMPONENT                                              */
/* ═════════════════════════════════════════════════════════════ */
function ResultsDashboard({ analysis = {}, onReset }) {
  const {
    filename = "N/A", selected_tasks = [], markdown_text = "",
    summary = "", sentiment = {}, topic = {},
  } = analysis || {};

  useEffect(() => { window.scrollTo({ top: 0, behavior: "smooth" }); }, []);

  const dominant_topic = topic?.dominant_topic || "N/A";
  const topics = topic?.topics || [];
  const chunk_results = topic?.chunk_results || [];
  const report = topic?.report || `Document "${filename}" was analyzed successfully.`;

  const [activeTab, setActiveTab] = useState("doc-info");
  const [selectedTopic, setSelectedTopic] = useState("all");
  const [searchText, setSearchText] = useState("");
  
  // Collapse toggles to handle massive files safely
  const [showSentences, setShowSentences] = useState(false);
  const [showChunks, setShowChunks] = useState(false);

  const sentimentData = [
    { name: "Positive", value: sentiment?.positive || 0 },
    { name: "Neutral",  value: sentiment?.neutral  || 0 },
    { name: "Negative", value: sentiment?.negative || 0 },
  ];

  const filteredChunks = useMemo(() => (chunk_results || []).filter((c) => {
    const tm = selectedTopic === "all" || c.topic === selectedTopic;
    const sm = (c.text || "").toLowerCase().includes(searchText.toLowerCase());
    return tm && sm;
  }), [chunk_results, selectedTopic, searchText]);

  const overallSentiment = sentiment?.overall_sentiment || sentiment?.label || "N/A";
  const confidence = sentiment?.average_confidence || sentiment?.confidence || 0;
  const sentenceResults = sentiment?.sentence_level || sentiment?.sentence_results || [];

  const has = {
    conv: selected_tasks.includes("Document Conversion"),
    sum:  selected_tasks.includes("Text Summarization"),
    sent: selected_tasks.includes("Sentiment Analysis"),
    top:  selected_tasks.includes("Topic Modeling"),
  };

  const download = (content, name, type) => {
    const b = new Blob([content || ""], { type });
    const a = document.createElement("a");
    a.href = window.URL.createObjectURL(b);
    a.download = name;
    a.click();
  };

  return (
    <div style={s.page}>

      {/* ── Header ── */}
      <header style={s.header}>
        <div>
          <div style={s.badge}><span style={s.badgeDot} />ANALYSIS COMPLETE</div>
          <h1 style={s.title}>Results Dashboard</h1>
          <p style={s.subtitle}>
            Insights extracted from <strong style={{ color: "var(--text-main)" }}>{filename}</strong>
          </p>
        </div>
        <button className="btn-secondary" style={s.backBtn} onClick={onReset}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
          New Analysis
        </button>
      </header>

      {/* ── Task Pills ── */}
      <div style={s.pillRow}>
        {(selected_tasks || []).map((t, i) => <span key={i} style={s.pill}>✓ {t}</span>)}
      </div>

      {/* ── Layout: Horizontal Tabs + Dynamic Main ── */}
      <div style={s.layout}>
        {/* Top Horizontal Tabs */}
        <nav style={s.horizontalTabBar}>
          <TabButton active={activeTab === "doc-info"} onClick={() => setActiveTab("doc-info")} text="Document Info" />
          {has.conv && <TabButton active={activeTab === "markdown"} onClick={() => setActiveTab("markdown")} text="Markdown" />}
          {has.sum  && <TabButton active={activeTab === "summary"} onClick={() => setActiveTab("summary")} text="Summary" />}
          {has.sent && <TabButton active={activeTab === "sentiment"} onClick={() => setActiveTab("sentiment")} text="Sentiment" />}
          {has.top  && <TabButton active={activeTab === "topics"} onClick={() => setActiveTab("topics")} text="Topics" />}
          <TabButton active={activeTab === "report"} onClick={() => setActiveTab("report")} text="Report" />
        </nav>

        {/* Dynamic Main Content */}
        <main style={s.main}>

          {/* Document Info Tab */}
          {activeTab === "doc-info" && (
            <Panel icon="📋" title="Document Information">
              <div style={s.infoGrid}>
                <InfoBox label="Filename" value={filename} />
                <InfoBox label="Selected Modules" value={(selected_tasks || []).join(", ") || "None"} />
              </div>
              <div style={s.statsRow}>
                {has.sent && <Stat icon="💬" label="Sentiment" val={overallSentiment} accent={sentimentOf(overallSentiment).bar} />}
                {has.sent && <Stat icon="📊" label="Confidence" val={typeof confidence === "number" ? (confidence * 100).toFixed(1) + "%" : confidence} />}
                {has.top && <Stat icon="🧠" label="Top Topic" val={dominant_topic} />}
                {has.top && <Stat icon="🧩" label="Chunks" val={chunk_results.length} />}
              </div>
            </Panel>
          )}

          {/* Markdown Tab */}
          {activeTab === "markdown" && has.conv && (
            <Panel icon="📝" title="Converted Markdown">
              <div style={s.codeBox}>
                <pre style={s.code}>{markdown_text || "No markdown output available."}</pre>
              </div>
              <Btn onClick={() => download(markdown_text, "converted.md", "text/markdown")}>⬇ Download .md</Btn>
            </Panel>
          )}

          {/* Summary Tab */}
          {activeTab === "summary" && has.sum && (
            <Panel icon="📖" title="Text Summary">
              <div style={s.textCard}>
                <p style={s.bodyText}>{summary || "No summary available."}</p>
              </div>
            </Panel>
          )}

          {/* Sentiment Tab */}
          {activeTab === "sentiment" && has.sent && (
            <Panel icon="💬" title="Sentiment Analysis">
              <div style={s.sentGrid}>
                {/* Bar Chart */}
                <div style={s.chartBox}>
                  <p style={s.microLabel}>DISTRIBUTION</p>
                  <div style={{ width: "100%", height: 220 }}>
                    <ResponsiveContainer>
                      <BarChart data={sentimentData} barCategoryGap="32%">
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" vertical={false} />
                        <XAxis dataKey="name" tick={{ fontWeight: 600, fontSize: 12, fill: "var(--text-light)" }} axisLine={{ stroke: "var(--border-color)" }} tickLine={false} />
                        <YAxis tick={{ fontSize: 11, fill: "var(--text-muted)" }} axisLine={false} tickLine={false} />
                        <Tooltip content={<LightTooltip />} cursor={{ fill: "rgba(139,92,246,0.04)" }} />
                        <Bar dataKey="value" radius={[8, 8, 0, 0]} maxBarSize={46}>
                          {sentimentData.map((e, i) => <Cell key={i} fill={SC[e.name]?.bar} />)}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Insights */}
                <div style={{ ...s.insightBox, borderLeft: `4px solid ${sentimentOf(overallSentiment).bar}` }}>
                  <p style={s.microLabel}>INSIGHTS</p>
                  <div style={{ marginBottom: 14 }}>
                    <p style={s.iLabel}>Overall</p>
                    <span style={{
                      display: "inline-block", padding: "6px 18px", borderRadius: 999,
                      fontWeight: 700, fontSize: 13,
                      background: sentimentOf(overallSentiment).light,
                      color: sentimentOf(overallSentiment).text,
                    }}>{overallSentiment}</span>
                  </div>
                  <div style={{ display: "flex", gap: 24, marginBottom: 14 }}>
                    <div>
                      <p style={s.iLabel}>Confidence</p>
                      <p style={s.iBig}>{typeof confidence === "number" ? (confidence * 100).toFixed(1) + "%" : confidence}</p>
                    </div>
                    <div>
                      <p style={s.iLabel}>Total Sentences</p>
                      <p style={s.iBig}>{sentiment?.total_sentences || sentenceResults.length || 0}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Foldable Sentence Results to handle large files */}
              <div style={{ marginTop: 28, paddingTop: 20, borderTop: "1px solid var(--border-color)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                  <p style={{ ...s.microLabel, margin: 0 }}>SENTENCE-LEVEL RESULTS ({sentenceResults.length})</p>
                  <button 
                    onClick={() => setShowSentences(!showSentences)}
                    style={s.toggleBtn}
                  >
                    {showSentences ? "Hide Sentences" : "View All Sentences"}
                  </button>
                </div>
                
                {showSentences && (
                  <div>
                    {sentenceResults.length > 0 ? sentenceResults.map((item, i) => {
                      const c = sentimentOf(item.label);
                      return (
                        <div key={i} style={{
                          ...s.sentCard, borderLeftColor: c.border,
                        }}>
                          <p style={s.sentText}>{item.sentence || "No sentence"}</p>
                          <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 8 }}>
                            <span style={{
                              padding: "3px 12px", borderRadius: 999, fontSize: 11,
                              fontWeight: 700, background: c.light, color: c.text,
                            }}>{item.label || "N/A"}</span>
                            <span style={{ fontSize: 12, color: "var(--text-light)", fontWeight: 500 }}>
                              {((item.confidence || item.score || 0) * 100).toFixed(1)}% confidence
                            </span>
                          </div>
                        </div>
                      );
                    }) : <p style={s.empty}>No sentence-level results available.</p>}
                  </div>
                )}
              </div>
            </Panel>
          )}

          {/* Topics Tab */}
          {activeTab === "topics" && has.top && (
            <Panel icon="🧠" title="Topic Modeling">
              {topics.length > 0 ? (
                <>
                  {/* Topic overview cards */}
                  <div style={s.topicCardsGrid}>
                    {topics.map((t, i) => {
                      const color = TOPIC_COLORS[i % TOPIC_COLORS.length];
                      const score = t.avg_score || t.score || 0;
                      return (
                        <div key={i} style={{ ...s.topicCard, borderTop: `3px solid ${color}` }}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                            <div style={{ ...s.topicIdx, background: `${color}15`, color: color }}>#{i + 1}</div>
                            <span style={{ ...s.topicScore, color: color }}>{(score * 100).toFixed(0)}%</span>
                          </div>
                          <p style={s.topicName}>{t.topic}</p>
                          <div style={s.topicBar}>
                            <div style={{ ...s.topicBarFill, width: `${Math.min(score * 100, 100)}%`, background: color }} />
                          </div>
                          <p style={s.topicCount}>{t.count || t.chunk_count || "—"} chunks</p>
                        </div>
                      );
                    })}
                  </div>

                  {/* Dominant topic highlight */}
                  <div style={s.dominantBox}>
                    <div style={s.dominantIcon}>🏆</div>
                    <div>
                      <p style={s.iLabel}>Dominant Topic</p>
                      <p style={{ fontSize: 18, fontWeight: 800, color: "var(--text-main)", margin: 0 }}>{dominant_topic}</p>
                    </div>
                  </div>

                  {/* Foldable Chunk Results to prevent massive scrolling */}
                  <div style={{ marginTop: 36, paddingTop: 28, borderTop: "1px solid var(--border-color)" }}>
                     <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                      <p style={{ ...s.microLabel, margin: 0 }}>CHUNK ANALYSIS ({filteredChunks.length})</p>
                      <button 
                        onClick={() => setShowChunks(!showChunks)}
                        style={s.toggleBtn}
                      >
                        {showChunks ? "Hide Chunks" : "View All Chunks"}
                      </button>
                    </div>

                    {showChunks && (
                      <div>
                        <div style={s.filterRow}>
                          <select value={selectedTopic} onChange={(e) => setSelectedTopic(e.target.value)} style={s.sel}>
                            <option value="all">All Topics</option>
                            {topics.map((t, i) => <option key={i} value={t.topic}>{t.topic}</option>)}
                          </select>
                          <input type="text" placeholder="Search chunks..." value={searchText} onChange={(e) => setSearchText(e.target.value)} style={s.searchIn} />
                        </div>

                        {filteredChunks.length > 0 ? filteredChunks.map((ch, i) => {
                          const cIdx = topics.findIndex((t) => t.topic === ch.topic);
                          const color = cIdx >= 0 ? TOPIC_COLORS[cIdx % TOPIC_COLORS.length] : "var(--primary)";
                          return (
                            <div key={ch.chunk_id || i} style={{ ...s.chunkCard, borderLeft: `3px solid ${color}` }}>
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                                <span style={s.chunkId}>Chunk {ch.chunk_id || i + 1}</span>
                                <div style={{ display: "flex", gap: 8 }}>
                                  <span style={{ ...s.chunkTag, background: `${color}12`, color: color }}>{ch.topic || "N/A"}</span>
                                  <span style={s.chunkScore}>Score: {ch.score || 0}</span>
                                </div>
                              </div>
                              <p style={s.chunkText}>{ch.text || "No text available"}</p>
                            </div>
                          );
                        }) : <p style={s.empty}>No chunk-level results available.</p>}
                      </div>
                    )}
                  </div>
                </>
              ) : <p style={s.empty}>No topic results available.</p>}
            </Panel>
          )}

          {/* Report Tab */}
          {activeTab === "report" && (
             <Panel icon="📊" title="Final Report">
               <div style={s.reportBox}>
                 {(report || "No report available.").split("\n").map((ln, i) => (
                   <p key={i} style={{ marginBottom: 10, whiteSpace: "pre-wrap" }}>{ln}</p>
                 ))}
               </div>
               <Btn onClick={() => download(report, "report.txt", "text/plain")}>⬇ Download Report</Btn>
             </Panel>
          )}
          
        </main>
      </div>
    </div>
  );
}

/* ═══ Sub-components ══════════════════════════════════════════ */
function Stat({ icon, label, val, accent }) {
  return (
    <div style={s.statCard}>
      <div style={s.statIcon}>{icon}</div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={s.statLabel}>{label}</p>
        <p style={{ ...s.statVal, ...(accent ? { color: accent } : {}) }}>{val}</p>
      </div>
    </div>
  );
}

function Panel({ icon, title, children }) {
  return (
    <section className="card-container" style={s.panel}>
      <div style={s.panelHead}>
        <span style={s.panelIcon}>{icon}</span>
        <h2 style={s.panelTitle}>{title}</h2>
      </div>
      {children}
    </section>
  );
}

function TabButton({ active, onClick, text }) {
  return (
    <button
      onClick={onClick}
      style={{
        ...s.navLink,
        background: active ? "var(--primary)" : "var(--bg-card)",
        color: active ? "#ffffff" : "var(--text-muted)",
        borderColor: active ? "var(--primary)" : "var(--border-color)",
        fontWeight: active ? 700 : 600,
        boxShadow: active ? "var(--shadow-sm)" : "none",
      }}
    >
      {text}
    </button>
  );
}

function InfoBox({ label, value }) {
  return (
    <div style={s.infoCard}>
      <p style={s.iLabel}>{label}</p>
      <p style={s.iVal}>{value}</p>
    </div>
  );
}

function Btn({ onClick, children }) {
  return <button className="btn-primary" onClick={onClick} style={s.actionBtn}>{children}</button>;
}

/* ═══ Styles ═════════════════════════════════════════════════ */
const s = {
  page: {
    minHeight: "100vh", padding: "32px 36px", position: "relative",
    overflow: "hidden", animation: "fadeIn 0.5s ease",
  },
  header: {
    display: "flex", flexDirection: "column", alignItems: "flex-start",
    gap: 16, marginBottom: 32, position: "relative", zIndex: 2,
  },
  badge: {
    display: "inline-flex", alignItems: "center", gap: 8,
    background: "var(--badge-bg)", color: "var(--primary)",
    padding: "6px 16px", borderRadius: 999, fontWeight: 700, fontSize: 11,
    letterSpacing: 1.8, marginBottom: 12,
  },
  badgeDot: { width: 6, height: 6, borderRadius: "50%", background: "var(--primary)" },
  title: { fontSize: 40, fontWeight: 800, color: "var(--text-main)", margin: 0, letterSpacing: -1.2 },
  subtitle: { marginTop: 8, color: "var(--text-muted)", fontSize: 15, lineHeight: 1.7 },
  backBtn: {
    display: "inline-flex", alignItems: "center", gap: 8,
    padding: "10px 20px", borderRadius: 12,
    fontSize: 14, marginTop: 10, // Thoroughly cleared from the top right
  },

  pillRow: {
    display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 24,
    position: "relative", zIndex: 2,
  },
  pill: {
    background: "var(--primary-bg)", color: "var(--primary)",
    padding: "5px 14px", borderRadius: 999, fontWeight: 600, fontSize: 12,
  },

  statsRow: {
    display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(155px, 1fr))",
    gap: 12, marginTop: 24, paddingTop: 24, borderTop: "1px solid var(--border-color)",
  },
  statCard: {
    padding: "16px 18px", display: "flex", alignItems: "center", gap: 12,
    borderRadius: 16, background: "var(--badge-bg)", border: "1px solid var(--border-color)",
  },
  statIcon: {
    width: 40, height: 40, borderRadius: 11,
    background: "var(--bg-card)",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: 18, flexShrink: 0,
  },
  statLabel: { color: "var(--text-light)", fontSize: 11, fontWeight: 500, margin: 0, marginBottom: 1 },
  statVal: {
    color: "var(--text-main)", fontSize: 14, fontWeight: 700, margin: 0,
    wordBreak: "break-word", overflow: "hidden", textOverflow: "ellipsis",
  },

  layout: {
    display: "flex", flexDirection: "column", gap: 16,
    position: "relative", zIndex: 2,
  },

  horizontalTabBar: {
    display: "flex", gap: 12, paddingBottom: 16, borderBottom: "1px solid var(--border-color)",
    overflowX: "auto", whiteSpace: "nowrap",
  },
  navLink: {
    padding: "10px 24px", borderRadius: 999, fontSize: 14, cursor: "pointer",
    border: "1px solid var(--border-color)", transition: "all 0.2s ease",
  },

  main: { display: "flex", flexDirection: "column" },

  panel: {
    borderRadius: 20, padding: "32px", animation: "fadeIn 0.3s ease",
  },
  panelHead: { display: "flex", alignItems: "center", gap: 12, marginBottom: 26 },
  panelIcon: {
    width: 38, height: 38, borderRadius: 12,
    background: "var(--badge-bg)",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: 18, flexShrink: 0, border: "1px solid var(--border-color)"
  },
  panelTitle: { fontSize: 24, fontWeight: 800, color: "var(--text-main)", margin: 0, letterSpacing: -0.5 },

  infoGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 },
  infoCard: {
    background: "var(--badge-bg)", borderRadius: 14, padding: "16px 20px",
    border: "1px solid var(--border-color)",
  },
  iLabel: { color: "var(--text-light)", fontSize: 12, fontWeight: 500, margin: "0 0 4px 0" },
  iVal: { color: "var(--text-main)", fontSize: 15, fontWeight: 600, margin: 0, wordBreak: "break-word", lineHeight: 1.4 },
  iBig: { fontSize: 28, fontWeight: 800, color: "var(--text-main)", margin: 0 },

  codeBox: {
    background: "#0f172a", borderRadius: 14, padding: 24,
    overflowX: "auto", maxHeight: 500,
  },
  code: { whiteSpace: "pre-wrap", lineHeight: 1.8, fontSize: 13, color: "#e2e8f0", margin: 0 },

  textCard: { background: "var(--bg-app)", borderRadius: 14, padding: 24, border: "1px solid var(--border-color)" },
  bodyText: { color: "var(--text-main)", fontSize: 15, lineHeight: 1.9, margin: 0 },
  empty: { color: "var(--text-light)", fontSize: 14 },

  microLabel: {
    fontSize: 11, fontWeight: 700, color: "var(--text-light)",
    textTransform: "uppercase", letterSpacing: 1.5, margin: "0 0 12px 0",
  },

  toggleBtn: {
    background: "transparent", border: "1.5px solid var(--primary)", color: "var(--primary)",
    padding: "6px 14px", borderRadius: 8, fontSize: 12, fontWeight: 700, cursor: "pointer", transition: "all 0.2s ease"
  },

  sentGrid: { display: "grid", gridTemplateColumns: "minmax(240px,380px) 1fr", gap: 20, alignItems: "stretch" },
  chartBox: {
    background: "var(--bg-app)", borderRadius: 16, padding: "24px 18px 18px 6px",
    border: "1px solid var(--border-color)",
  },
  insightBox: {
    background: "var(--bg-app)", borderRadius: 16, padding: 26,
    border: "1px solid var(--border-color)", borderLeft: "4px solid var(--primary)",
    display: "flex", flexDirection: "column", justifyContent: "center",
  },
  sentCard: {
    padding: "16px 20px", borderRadius: 14, marginBottom: 12,
    background: "var(--bg-app)", border: "1px solid var(--border-color)",
  },
  sentText: { color: "var(--text-main)", fontSize: 14, lineHeight: 1.7, margin: 0 },

  topicCardsGrid: {
    display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 16,
  },
  topicCard: {
    background: "var(--bg-app)", borderRadius: 16, padding: "20px 22px",
    border: "1px solid var(--border-color)",
  },
  topicIdx: {
    padding: "4px 10px", borderRadius: 8, fontWeight: 800, fontSize: 12,
  },
  topicScore: { fontSize: 22, fontWeight: 800 },
  topicName: { fontSize: 15, fontWeight: 700, color: "var(--text-main)", margin: "0 0 12px 0" },
  topicBar: { height: 6, borderRadius: 999, background: "var(--border-color)", overflow: "hidden", marginBottom: 8 },
  topicBarFill: { height: "100%", borderRadius: 999, transition: "width 0.5s ease" },
  topicCount: { fontSize: 13, color: "var(--text-light)", margin: 0 },
  
  dominantBox: {
    display: "flex", alignItems: "center", gap: 18, marginTop: 24,
    background: "var(--primary-bg)", borderRadius: 16,
    padding: "20px 24px", border: "1px solid var(--border-color)",
  },
  dominantIcon: {
    width: 52, height: 52, borderRadius: 14,
    background: "var(--primary)", color: "white",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: 24, flexShrink: 0,
  },

  filterRow: { display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 20 },
  sel: {
    padding: "10px 16px", borderRadius: 12, border: "1.5px solid var(--border-color)",
    minWidth: 200, background: "var(--bg-card)", color: "var(--text-main)", fontSize: 14, fontWeight: 500,
  },
  searchIn: {
    padding: "10px 16px", borderRadius: 12, border: "1.5px solid var(--border-color)",
    flex: 1, minWidth: 220, background: "var(--bg-card)", color: "var(--text-main)", fontSize: 14, fontWeight: 500,
  },
  chunkCard: {
    background: "var(--bg-app)", padding: "16px 20px", borderRadius: 14,
    marginBottom: 12, border: "1px solid var(--border-color)",
  },
  chunkId: { color: "var(--primary)", fontWeight: 700, fontSize: 14 },
  chunkTag: { padding: "4px 12px", borderRadius: 999, fontSize: 12, fontWeight: 600 },
  chunkScore: { fontSize: 13, color: "var(--text-light)", fontWeight: 500 },
  chunkText: { color: "var(--text-main)", fontSize: 14, lineHeight: 1.8, margin: 0 },

  reportBox: {
    background: "var(--bg-app)", borderRadius: 14, padding: 26,
    border: "1px solid var(--border-color)", color: "var(--text-main)", lineHeight: 1.9, fontSize: 15,
  },

  actionBtn: {
    marginTop: 16, padding: "12px 24px", borderRadius: 12,
    fontSize: 14,
  },
};

export default ResultsDashboard;