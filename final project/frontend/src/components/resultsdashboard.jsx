import { useEffect, useMemo, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, Cell,
} from "recharts";

/* ── Sentiment Colors ──────────────────────────────────────── */
const SC = {
  Positive: { bar: "#22c55e", bg: "#f0fdf4", border: "#22c55e", text: "#15803d", light: "#dcfce7", glow: "rgba(34,197,94,0.15)" },
  Neutral:  { bar: "#3b82f6", bg: "#eff6ff", border: "#3b82f6", text: "#1d4ed8", light: "#dbeafe", glow: "rgba(59,130,246,0.15)" },
  Negative: { bar: "#ef4444", bg: "#fef2f2", border: "#ef4444", text: "#dc2626", light: "#fee2e2", glow: "rgba(239,68,68,0.15)" },
};
const sentimentOf = (l) => {
  const k = (l || "").charAt(0).toUpperCase() + (l || "").slice(1).toLowerCase();
  return SC[k] || SC.Neutral;
};
const TOPIC_COLORS = ["#7c3aed", "#ec4899", "#3b82f6", "#f59e0b", "#10b981", "#6366f1", "#ef4444", "#14b8a6"];

const LightTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "rgba(255,255,255,0.95)", backdropFilter: "blur(12px)", borderRadius: 14, padding: "12px 18px", boxShadow: "0 12px 40px rgba(15,23,42,0.12)", border: "1px solid rgba(226,232,240,0.6)" }}>
      <p style={{ color: "#64748b", fontSize: 11, margin: "0 0 4px 0", fontWeight: 500, textTransform: "uppercase", letterSpacing: 0.5 }}>{label}</p>
      <p style={{ color: "#0f172a", fontSize: 18, fontWeight: 800, margin: 0 }}>{payload[0].value}</p>
    </div>
  );
};

/* ── Tab Definitions ─────────────────────────────────────────── */
const TAB_DEFS = [
  { id: "overview", icon: "📋", label: "Overview" },
  { id: "markdown", icon: "📝", label: "Markdown", task: "Document Conversion" },
  { id: "summary", icon: "📖", label: "Summary", task: "Text Summarization" },
  { id: "sentiment", icon: "💬", label: "Sentiment", task: "Sentiment Analysis" },
  { id: "topics", icon: "🧠", label: "Topics", task: "Topic Modeling" },
  { id: "report", icon: "📊", label: "Report" },
];

/* ── Collapsible ─────────────────────────────────────────────── */
function Collapsible({ title, count, accent = "#7c3aed", defaultOpen = false, children }) {
  const [open, setOpen] = useState(defaultOpen);
  const ref = useRef(null);
  const [h, setH] = useState(0);
  useEffect(() => { if (ref.current) setH(ref.current.scrollHeight); }, [children, open]);

  return (
    <div style={st.collWrap}>
      <button onClick={() => setOpen(!open)} style={st.collHead}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1 }}>
          <div style={{ ...st.collArrow, background: `${accent}12`, color: accent, border: `1px solid ${accent}25` }}>
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"
              style={{ transform: open ? "rotate(90deg)" : "rotate(0)", transition: "transform 0.3s ease" }}>
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </div>
          <span style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{title}</span>
        </div>
        {count !== undefined && <span style={{ ...st.collCount, background: `${accent}10`, color: accent, border: `1px solid ${accent}20` }}>{count} items</span>}
      </button>
      <div style={{ maxHeight: open ? h + 40 : 0, overflow: "hidden", transition: "max-height 0.4s cubic-bezier(0.4,0,0.2,1), opacity 0.3s ease", opacity: open ? 1 : 0 }}>
        <div ref={ref} style={{ padding: "14px 0 4px 0" }}>{children}</div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════ */
/*  RESULTS DASHBOARD                                             */
/* ═══════════════════════════════════════════════════════════════ */
function ResultsDashboard({ analysis = {}, onReset }) {
  const { filename = "N/A", selected_tasks = [], markdown_text = "", summary = "", sentiment = {}, topic = {} } = analysis || {};

  const [activeTab, setActiveTab] = useState("overview");
  const [showScrollTop, setShowScrollTop] = useState(false);

  useEffect(() => { window.scrollTo({ top: 0, behavior: "smooth" }); }, []);
  useEffect(() => {
    const h = () => setShowScrollTop(window.scrollY > 300);
    window.addEventListener("scroll", h, { passive: true });
    return () => window.removeEventListener("scroll", h);
  }, []);

  // Keyboard: Esc = back, ← → = switch tabs
  const visibleTabs = useMemo(() => TAB_DEFS.filter(t => !t.task || selected_tasks.includes(t.task)), [selected_tasks]);
  useEffect(() => {
    const h = (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.tagName === "SELECT") return;
      if (e.key === "Escape") { onReset(); return; }
      const idx = visibleTabs.findIndex(t => t.id === activeTab);
      if (e.key === "ArrowRight" && idx < visibleTabs.length - 1) { e.preventDefault(); setActiveTab(visibleTabs[idx + 1].id); }
      if (e.key === "ArrowLeft" && idx > 0) { e.preventDefault(); setActiveTab(visibleTabs[idx - 1].id); }
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [visibleTabs, activeTab, onReset]);

  const dominant_topic = topic?.dominant_topic || "N/A";
  const topics = topic?.topics || [];
  const chunk_results = topic?.chunk_results || [];
  const report = topic?.report || `Document "${filename}" was analyzed successfully.`;
  const [selectedTopic, setSelectedTopic] = useState("all");
  const [searchText, setSearchText] = useState("");

  const sentimentData = [
    { name: "Positive", value: sentiment?.positive || 0 },
    { name: "Neutral",  value: sentiment?.neutral  || 0 },
    { name: "Negative", value: sentiment?.negative || 0 },
  ];
  const filteredChunks = useMemo(() => (chunk_results || []).filter((c) => {
    return (selectedTopic === "all" || c.topic === selectedTopic) && (c.text || "").toLowerCase().includes(searchText.toLowerCase());
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

  const dl = (content, name, type) => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([content || ""], { type }));
    a.download = name; a.click();
  };

  const confStr = typeof confidence === "number" ? (confidence * 100).toFixed(1) + "%" : confidence;

  /* ── Render Tab Content ───────────────────────────────────── */
  const renderContent = () => {
    switch (activeTab) {
      /* ── Overview ── */
      case "overview":
        return (
          <motion.div key="overview" {...fadeAnim}>
            {/* Stats row */}
            <div style={st.statsGrid}>
              <StatCard icon="📄" label="Document" value={filename} />
              {has.sent && <StatCard icon="💬" label="Sentiment" value={overallSentiment} accent={sentimentOf(overallSentiment).bar} />}
              {has.sent && <StatCard icon="📊" label="Confidence" value={confStr} />}
              {has.sent && <StatCard icon="📋" label="Sentences" value={sentiment?.total_sentences || sentenceResults.length || 0} />}
              {has.top && <StatCard icon="🧠" label="Top Topic" value={dominant_topic} />}
              {has.top && <StatCard icon="🧩" label="Chunks" value={chunk_results.length} />}
            </div>

            {/* Quick summary preview */}
            <div style={st.card}>
              <div style={st.cardHead}>
                <span style={st.step}>📋</span>
                <div>
                  <h2 style={st.cardTitle}>Analysis Overview</h2>
                  <p style={st.cardDesc}>Quick look at your document analysis results</p>
                </div>
              </div>
              <div style={st.infoRow}>
                <div style={st.infoItem}><p style={st.infoLabel}>FILENAME</p><p style={st.infoVal}>{filename}</p></div>
                <div style={st.infoItem}><p style={st.infoLabel}>MODULES APPLIED</p><p style={st.infoVal}>{selected_tasks.join(", ") || "None"}</p></div>
              </div>
              {has.sum && summary && (
                <div style={{ marginTop: 18 }}>
                  <p style={st.infoLabel}>SUMMARY PREVIEW</p>
                  <p style={{ ...st.bodyText, marginTop: 6 }}>{summary.length > 300 ? summary.slice(0, 300) + "…" : summary}</p>
                  {summary.length > 300 && <button onClick={() => setActiveTab("summary")} style={st.linkBtn}>Read full summary →</button>}
                </div>
              )}
            </div>

            {/* Quick sentiment bar if available */}
            {has.sent && (
              <div style={st.card}>
                <div style={st.cardHead}>
                  <span style={st.step}>💬</span>
                  <div><h2 style={st.cardTitle}>Sentiment at a Glance</h2><p style={st.cardDesc}>Overall tone of the document</p></div>
                </div>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 14 }}>
                  {sentimentData.map(d => {
                    const c = SC[d.name];
                    return <span key={d.name} style={{ display: "inline-flex", alignItems: "center", gap: 6, padding: "6px 16px", borderRadius: 999, fontSize: 13, background: c.bg, color: c.text, fontWeight: 600, border: `1px solid ${c.border}20` }}>
                      <span style={{ width: 8, height: 8, borderRadius: "50%", background: c.bar }} />{d.name}: {d.value}
                    </span>;
                  })}
                </div>
                <button onClick={() => setActiveTab("sentiment")} style={st.linkBtn}>View detailed analysis →</button>
              </div>
            )}
          </motion.div>
        );

      /* ── Markdown ── */
      case "markdown":
        return (
          <motion.div key="markdown" {...fadeAnim}>
            <div style={st.card}>
              <div style={st.cardHead}><span style={st.step}>📝</span><div><h2 style={st.cardTitle}>Converted Markdown</h2><p style={st.cardDesc}>Document content in Markdown format</p></div></div>
              <div style={st.codeBox}><pre style={st.code}>{markdown_text || "No markdown output available."}</pre></div>
              <ActionBtn onClick={() => dl(markdown_text, "converted.md", "text/markdown")} icon="⬇">Download .md</ActionBtn>
            </div>
          </motion.div>
        );

      /* ── Summary ── */
      case "summary":
        return (
          <motion.div key="summary" {...fadeAnim}>
            <div style={st.card}>
              <div style={st.cardHead}><span style={st.step}>📖</span><div><h2 style={st.cardTitle}>Text Summary</h2><p style={st.cardDesc}>AI-generated concise summary</p></div></div>
              <div style={st.textBox}><p style={st.bodyText}>{summary || "No summary available."}</p></div>
            </div>
          </motion.div>
        );

      /* ── Sentiment ── */
      case "sentiment":
        return (
          <motion.div key="sentiment" {...fadeAnim}>
            <div style={st.card}>
              <div style={st.cardHead}><span style={st.step}>💬</span><div><h2 style={st.cardTitle}>Sentiment Analysis</h2><p style={st.cardDesc}>Tone and emotion analysis of the document</p></div></div>

              <div style={st.sentLayout}>
                {/* Chart */}
                <div style={st.chartCard}>
                  <p style={st.microLabel}>DISTRIBUTION</p>
                  <div style={{ width: "100%", height: 220 }}>
                    <ResponsiveContainer>
                      <BarChart data={sentimentData} barCategoryGap="32%">
                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                        <XAxis dataKey="name" tick={{ fontWeight: 600, fontSize: 12, fill: "#64748b" }} axisLine={{ stroke: "#e2e8f0" }} tickLine={false} />
                        <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                        <Tooltip content={<LightTooltip />} cursor={{ fill: "rgba(139,92,246,0.04)" }} />
                        <Bar dataKey="value" radius={[10, 10, 0, 0]} maxBarSize={46} animationDuration={800}>
                          {sentimentData.map((e, i) => <Cell key={i} fill={SC[e.name]?.bar} />)}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Insights */}
                <div style={{ ...st.insightCard, borderLeft: `4px solid ${sentimentOf(overallSentiment).bar}` }}>
                  <p style={st.microLabel}>INSIGHTS</p>
                  <div style={{ marginBottom: 14 }}>
                    <p style={st.infoLabel}>Overall</p>
                    <span style={{ display: "inline-block", padding: "8px 22px", borderRadius: 999, fontWeight: 700, fontSize: 14, background: sentimentOf(overallSentiment).light, color: sentimentOf(overallSentiment).text, boxShadow: `0 2px 12px ${sentimentOf(overallSentiment).glow}` }}>{overallSentiment}</span>
                  </div>
                  <div style={{ display: "flex", gap: 28, marginBottom: 14 }}>
                    <div><p style={st.infoLabel}>Confidence</p><p style={st.bigNum}>{confStr}</p></div>
                    <div><p style={st.infoLabel}>Sentences</p><p style={st.bigNum}>{sentiment?.total_sentences || sentenceResults.length || 0}</p></div>
                  </div>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    {sentimentData.map(d => { const c = SC[d.name]; return <span key={d.name} style={{ display: "inline-flex", alignItems: "center", gap: 6, padding: "5px 14px", borderRadius: 999, fontSize: 12, background: c.bg, color: c.text, fontWeight: 600, border: `1px solid ${c.border}20` }}><span style={{ width: 8, height: 8, borderRadius: "50%", background: c.bar }} />{d.name}: {d.value}</span>; })}
                  </div>
                </div>
              </div>

              {/* Sentence cards */}
              <div style={{ marginTop: 24 }}>
                <Collapsible title="Sentence-Level Results" count={sentenceResults.length} accent={sentimentOf(overallSentiment).bar}>
                  {sentenceResults.length > 0 ? sentenceResults.map((item, i) => {
                    const c = sentimentOf(item.label);
                    return (
                      <div key={i} style={{ ...st.sentCard, borderLeftColor: c.border, background: `linear-gradient(135deg, ${c.bg}, #fff)` }}>
                        <p style={st.sentText}>{item.sentence || "No sentence"}</p>
                        <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 10 }}>
                          <span style={{ padding: "4px 14px", borderRadius: 999, fontSize: 11, fontWeight: 700, background: c.light, color: c.text, border: `1px solid ${c.border}30` }}>{item.label || "N/A"}</span>
                          <span style={{ fontSize: 12, color: "#94a3b8", fontWeight: 500 }}>{((item.confidence || item.score || 0) * 100).toFixed(1)}%</span>
                        </div>
                      </div>
                    );
                  }) : <p style={st.empty}>No sentence-level results available.</p>}
                </Collapsible>
              </div>
            </div>
          </motion.div>
        );

      /* ── Topics ── */
      case "topics":
        return (
          <motion.div key="topics" {...fadeAnim}>
            {/* Topic cards */}
            <div style={st.card}>
              <div style={st.cardHead}><span style={st.step}>🧠</span><div><h2 style={st.cardTitle}>Topic Modeling</h2><p style={st.cardDesc}>Discovered themes and chunk analysis</p></div></div>

              {topics.length > 0 ? (<>
                <div style={st.topicGrid}>
                  {topics.map((t, i) => {
                    const color = TOPIC_COLORS[i % TOPIC_COLORS.length];
                    const score = t.avg_score || t.score || 0;
                    return (
                      <motion.div key={i} whileHover={{ y: -3 }} style={{ ...st.topicCard, borderTop: `3px solid ${color}` }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                          <div style={{ padding: "4px 10px", borderRadius: 8, fontWeight: 800, fontSize: 11, background: `${color}15`, color }}>#{i + 1}</div>
                          <span style={{ fontSize: 20, fontWeight: 800, color }}>{(score * 100).toFixed(0)}%</span>
                        </div>
                        <p style={{ fontSize: 14, fontWeight: 700, color: "#0f172a", margin: "0 0 10px 0" }}>{t.topic}</p>
                        <div style={st.topicBar}><div style={{ height: "100%", borderRadius: 999, width: `${Math.min(score * 100, 100)}%`, background: `linear-gradient(90deg, ${color}, ${color}aa)`, transition: "width 0.8s ease" }} /></div>
                        <p style={{ fontSize: 12, color: "#94a3b8", margin: 0 }}>{t.count || t.chunk_count || "—"} chunks</p>
                      </motion.div>
                    );
                  })}
                </div>

                {/* Chart */}
                <div style={{ ...st.chartCard, marginTop: 20 }}>
                  <p style={st.microLabel}>TOPIC SCORE COMPARISON</p>
                  <div style={{ width: "100%", height: 280 }}>
                    <ResponsiveContainer>
                      <BarChart data={topics.map((t, i) => ({ topic: t.topic, score: t.avg_score || t.score || 0 }))} barCategoryGap="24%">
                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                        <XAxis dataKey="topic" tick={{ fontSize: 11, fill: "#64748b", fontWeight: 600 }} axisLine={{ stroke: "#e2e8f0" }} tickLine={false} />
                        <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                        <Tooltip content={<LightTooltip />} cursor={{ fill: "rgba(139,92,246,0.04)" }} />
                        <Bar dataKey="score" radius={[10, 10, 0, 0]} maxBarSize={48} animationDuration={1000}>
                          {topics.map((_, i) => <Cell key={i} fill={TOPIC_COLORS[i % TOPIC_COLORS.length]} />)}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Dominant topic */}
                <div style={st.dominantBox}>
                  <div style={st.dominantIcon}>🏆</div>
                  <div><p style={st.infoLabel}>Dominant Topic</p><p style={{ fontSize: 20, fontWeight: 800, color: "#0f172a", margin: 0 }}>{dominant_topic}</p></div>
                </div>
              </>) : <p style={st.empty}>No topic results available.</p>}
            </div>

            {/* Chunk Analysis */}
            {chunk_results.length > 0 && (
              <div style={{ ...st.card, marginTop: 18 }}>
                <div style={st.cardHead}><span style={st.step}>🧩</span><div><h2 style={st.cardTitle}>Chunk Analysis</h2><p style={st.cardDesc}>Individual text segment analysis</p></div></div>
                <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 16 }}>
                  <select value={selectedTopic} onChange={(e) => setSelectedTopic(e.target.value)} style={st.select}>
                    <option value="all">All Topics</option>
                    {topics.map((t, i) => <option key={i} value={t.topic}>{t.topic}</option>)}
                  </select>
                  <input type="text" placeholder="🔍 Search chunks..." value={searchText} onChange={(e) => setSearchText(e.target.value)} style={st.searchInput} />
                </div>
                <Collapsible title="Chunk Details" count={filteredChunks.length}>
                  {filteredChunks.length > 0 ? filteredChunks.map((ch, i) => {
                    const cIdx = topics.findIndex(t => t.topic === ch.topic);
                    const color = cIdx >= 0 ? TOPIC_COLORS[cIdx % TOPIC_COLORS.length] : "#8b5cf6";
                    return (
                      <div key={ch.chunk_id || i} style={{ ...st.chunkCard, borderLeft: `3px solid ${color}` }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                          <span style={{ color: "#7c3aed", fontWeight: 700, fontSize: 13 }}>Chunk {ch.chunk_id || i + 1}</span>
                          <div style={{ display: "flex", gap: 8 }}>
                            <span style={{ padding: "4px 12px", borderRadius: 999, fontSize: 11, fontWeight: 600, background: `${color}12`, color, border: `1px solid ${color}20` }}>{ch.topic || "N/A"}</span>
                            <span style={{ fontSize: 12, color: "#94a3b8", fontWeight: 500 }}>Score: {ch.score || 0}</span>
                          </div>
                        </div>
                        <p style={{ color: "#475569", fontSize: 14, lineHeight: 1.7, margin: 0 }}>{ch.text || "No text"}</p>
                      </div>
                    );
                  }) : <p style={st.empty}>No chunks match your filter.</p>}
                </Collapsible>
              </div>
            )}
          </motion.div>
        );

      /* ── Report ── */
      case "report":
        return (
          <motion.div key="report" {...fadeAnim}>
            <div style={st.card}>
              <div style={st.cardHead}><span style={st.step}>📊</span><div><h2 style={st.cardTitle}>Final Report</h2><p style={st.cardDesc}>Complete analysis summary</p></div></div>
              <div style={st.textBox}>
                {(report || "No report available.").split("\n").map((ln, i) => <p key={i} style={{ marginBottom: 10, whiteSpace: "pre-wrap" }}>{ln}</p>)}
              </div>
              <ActionBtn onClick={() => dl(report, "report.txt", "text/plain")} icon="⬇">Download Report</ActionBtn>
            </div>
          </motion.div>
        );

      default: return null;
    }
  };

  return (
    <div style={st.page}>
      <div style={st.shape1} /><div style={st.shape2} /><div style={st.shape3} />

      <div style={st.container}>
        {/* ── Header ── */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <div style={st.heroRow}>
            <div>
              <div style={st.badge}><span style={st.badgeDot} />ANALYSIS COMPLETE</div>
              <h1 style={st.title}>Results <span style={{ color: "#7c3aed" }}>Dashboard</span></h1>
              <p style={st.subtitle}>Insights extracted from <strong style={{ color: "#0f172a" }}>{filename}</strong></p>
            </div>
            <button style={st.backBtn} onClick={onReset} title="Press Esc"
              onMouseEnter={(e) => { e.currentTarget.style.background = "linear-gradient(135deg,#7c3aed,#a855f7)"; e.currentTarget.style.color = "#fff"; e.currentTarget.style.borderColor = "transparent"; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = "#fff"; e.currentTarget.style.color = "#475569"; e.currentTarget.style.borderColor = "#e2e8f0"; }}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
              New Analysis
            </button>
          </div>

          {/* Task pills */}
          <div style={st.pillRow}>
            {selected_tasks.map((t, i) => <span key={i} style={st.pill}><span style={{ fontSize: 11 }}>✓</span> {t}</span>)}
          </div>
        </motion.div>

        {/* ── Tab Navigation ── */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.15 }}>
          <div style={st.tabBar}>
            {visibleTabs.map((tab) => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                style={{ ...st.tabBtn, ...(activeTab === tab.id ? st.tabBtnActive : {}) }}
              >
                <span style={{ fontSize: 14 }}>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
          <p style={st.tabHint}>Use ← → arrow keys to switch tabs • Esc to go back</p>
        </motion.div>

        {/* ── Tab Content ── */}
        <AnimatePresence mode="wait">
          {renderContent()}
        </AnimatePresence>
      </div>

      {/* Scroll to top */}
      <AnimatePresence>
        {showScrollTop && (
          <motion.button initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.8 }} transition={{ duration: 0.25 }}
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })} style={st.scrollTopBtn} aria-label="Scroll to top">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
}

/* ── Sub-components ────────────────────────────────────────── */
function StatCard({ icon, label, value, accent }) {
  return (
    <motion.div style={st.statCard} whileHover={{ y: -2, boxShadow: "0 8px 28px rgba(15,23,42,0.08)" }}>
      <div style={st.statIcon}>{icon}</div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={st.statLabel}>{label}</p>
        <p style={{ ...st.statVal, ...(accent ? { color: accent } : {}) }}>{value}</p>
      </div>
    </motion.div>
  );
}

function ActionBtn({ onClick, children, icon }) {
  return (
    <motion.button onClick={onClick} style={st.actionBtn} whileHover={{ y: -2, boxShadow: "0 8px 28px rgba(124,58,237,0.3)" }} whileTap={{ scale: 0.97 }}>
      {icon && <span style={{ marginRight: 6 }}>{icon}</span>}{children}
    </motion.button>
  );
}

const fadeAnim = {
  initial: { opacity: 0, y: 14 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
  transition: { duration: 0.35, ease: [0.4, 0, 0.2, 1] },
};

/* ═══ Styles ═════════════════════════════════════════════════ */
const st = {
  page: { minHeight: "100vh", display: "flex", justifyContent: "center", padding: "40px 20px 80px", position: "relative", overflow: "hidden" },
  shape1: { position: "fixed", width: 420, height: 420, borderRadius: "50%", background: "radial-gradient(circle, rgba(139,92,246,0.08), transparent 70%)", top: "-8%", left: "-8%", pointerEvents: "none" },
  shape2: { position: "fixed", width: 350, height: 350, borderRadius: "50%", background: "radial-gradient(circle, rgba(236,72,153,0.06), transparent 70%)", bottom: "-6%", right: "-6%", pointerEvents: "none" },
  shape3: { position: "fixed", width: 200, height: 200, borderRadius: "50%", background: "radial-gradient(circle, rgba(59,130,246,0.05), transparent 70%)", top: "45%", right: "15%", pointerEvents: "none" },

  container: { width: "100%", maxWidth: 820, position: "relative", zIndex: 2 },

  heroRow: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16, marginBottom: 16 },
  badge: { display: "inline-flex", alignItems: "center", gap: 8, background: "linear-gradient(135deg,#dcfce7,#d1fae5)", color: "#15803d", padding: "6px 18px", borderRadius: 999, fontWeight: 700, fontSize: 11, letterSpacing: 1.8, marginBottom: 12, boxShadow: "0 2px 8px rgba(34,197,94,0.1)" },
  badgeDot: { width: 7, height: 7, borderRadius: "50%", background: "#22c55e", boxShadow: "0 0 8px rgba(34,197,94,0.4)", animation: "pulse 2s ease-in-out infinite", display: "inline-block" },
  title: { fontSize: "clamp(28px, 5vw, 40px)", fontWeight: 800, color: "#0f172a", margin: 0, letterSpacing: -1.2, lineHeight: 1.15 },
  subtitle: { marginTop: 6, color: "#64748b", fontSize: 15, lineHeight: 1.7 },
  backBtn: { display: "flex", alignItems: "center", gap: 8, padding: "11px 22px", borderRadius: 14, border: "1.5px solid #e2e8f0", background: "#fff", color: "#475569", fontWeight: 600, cursor: "pointer", fontSize: 14, boxShadow: "0 2px 8px rgba(15,23,42,0.04)", transition: "all 0.25s ease", flexShrink: 0 },

  pillRow: { display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 24 },
  pill: { background: "linear-gradient(135deg,#ede9fe,#f5f3ff)", color: "#7c3aed", padding: "6px 16px", borderRadius: 999, fontWeight: 600, fontSize: 12, display: "inline-flex", alignItems: "center", gap: 6, border: "1px solid rgba(139,92,246,0.1)" },

  /* Tabs */
  tabBar: { display: "flex", gap: 6, flexWrap: "wrap", background: "rgba(255,255,255,0.7)", backdropFilter: "blur(16px)", borderRadius: 16, padding: 6, border: "1px solid rgba(226,232,240,0.8)", boxShadow: "0 4px 16px rgba(15,23,42,0.04)", marginBottom: 8 },
  tabBtn: { display: "flex", alignItems: "center", gap: 6, padding: "10px 18px", borderRadius: 12, border: "none", background: "transparent", color: "#64748b", fontWeight: 600, fontSize: 13, cursor: "pointer", transition: "all 0.2s ease", fontFamily: "inherit", whiteSpace: "nowrap" },
  tabBtnActive: { background: "linear-gradient(135deg,#7c3aed,#a855f7)", color: "#fff", boxShadow: "0 4px 16px rgba(124,58,237,0.25)" },
  tabHint: { color: "#b8c0cc", fontSize: 11, fontWeight: 500, marginBottom: 20, paddingLeft: 4 },

  /* Cards */
  card: { background: "rgba(255,255,255,0.82)", backdropFilter: "blur(20px)", borderRadius: 22, padding: "26px 28px", marginBottom: 18, border: "1px solid rgba(226,232,240,0.8)", boxShadow: "0 8px 30px rgba(15,23,42,0.06), 0 1px 3px rgba(15,23,42,0.04)" },
  cardHead: { display: "flex", alignItems: "center", gap: 14, marginBottom: 20 },
  step: { width: 38, height: 38, borderRadius: 12, background: "linear-gradient(135deg,#ede9fe,#f5f3ff)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 17, flexShrink: 0, border: "1px solid rgba(139,92,246,0.1)" },
  cardTitle: { fontSize: 18, fontWeight: 700, color: "#0f172a", margin: 0 },
  cardDesc: { fontSize: 13, color: "#94a3b8", margin: "2px 0 0 0" },

  /* Stats */
  statsGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12, marginBottom: 18 },
  statCard: { background: "rgba(255,255,255,0.88)", backdropFilter: "blur(16px)", borderRadius: 18, padding: "16px 18px", display: "flex", alignItems: "center", gap: 12, border: "1px solid rgba(226,232,240,0.7)", boxShadow: "0 4px 16px rgba(15,23,42,0.04)", transition: "all 0.25s ease", cursor: "default" },
  statIcon: { width: 42, height: 42, borderRadius: 12, background: "linear-gradient(135deg,#ede9fe,#f5f3ff)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, flexShrink: 0, border: "1px solid rgba(139,92,246,0.08)" },
  statLabel: { color: "#94a3b8", fontSize: 11, fontWeight: 600, margin: 0, marginBottom: 2, textTransform: "uppercase", letterSpacing: 0.5 },
  statVal: { color: "#0f172a", fontSize: 14, fontWeight: 700, margin: 0, wordBreak: "break-word", overflow: "hidden", textOverflow: "ellipsis" },

  /* Info */
  infoRow: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 14 },
  infoItem: { background: "#f8fafc", borderRadius: 14, padding: "14px 18px", border: "1px solid #f1f5f9" },
  infoLabel: { color: "#94a3b8", fontSize: 11, fontWeight: 600, margin: "0 0 3px 0", textTransform: "uppercase", letterSpacing: 0.3 },
  infoVal: { color: "#0f172a", fontSize: 14, fontWeight: 600, margin: 0, wordBreak: "break-word" },
  bigNum: { fontSize: 26, fontWeight: 800, color: "#0f172a", margin: 0 },
  linkBtn: { background: "none", border: "none", color: "#7c3aed", fontWeight: 600, fontSize: 13, cursor: "pointer", padding: "6px 0", fontFamily: "inherit" },
  bodyText: { color: "#334155", fontSize: 15, lineHeight: 1.9, margin: 0 },
  empty: { color: "#94a3b8", fontSize: 14, fontStyle: "italic" },
  microLabel: { fontSize: 11, fontWeight: 700, color: "#94a3b8", textTransform: "uppercase", letterSpacing: 1.5, margin: "0 0 12px 0" },

  /* Code */
  codeBox: { background: "linear-gradient(145deg, #0f172a, #1e293b)", borderRadius: 16, padding: 22, overflowX: "auto", maxHeight: 450, border: "1px solid rgba(139,92,246,0.15)" },
  code: { whiteSpace: "pre-wrap", lineHeight: 1.8, fontSize: 13, color: "#e2e8f0", margin: 0 },
  textBox: { background: "linear-gradient(135deg, #f8fafc, #faf8ff)", borderRadius: 16, padding: 22, border: "1px solid #f1f5f9" },

  /* Sentiment */
  sentLayout: { display: "grid", gridTemplateColumns: "minmax(240px,380px) 1fr", gap: 18, alignItems: "stretch" },
  chartCard: { background: "linear-gradient(135deg, #f8fafc, #faf8ff)", borderRadius: 18, padding: "22px 16px 16px 8px", border: "1px solid #f1f5f9" },
  insightCard: { background: "linear-gradient(135deg, #f8fafc, #faf8ff)", borderRadius: 18, padding: 24, border: "1px solid #f1f5f9", display: "flex", flexDirection: "column", justifyContent: "center" },
  sentCard: { padding: "16px 20px", borderRadius: 16, marginBottom: 10, borderLeft: "4px solid #3b82f6", border: "1px solid #f1f5f9", transition: "all 0.2s ease" },
  sentText: { color: "#334155", fontSize: 14, lineHeight: 1.7, margin: 0 },

  /* Collapsible */
  collWrap: { background: "linear-gradient(135deg, rgba(248,250,252,0.8), rgba(250,245,255,0.3))", borderRadius: 16, border: "1px solid rgba(226,232,240,0.7)", overflow: "hidden" },
  collHead: { display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%", padding: "14px 18px", background: "transparent", border: "none", cursor: "pointer", fontFamily: "inherit", transition: "all 0.2s ease" },
  collArrow: { width: 28, height: 28, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 },
  collCount: { padding: "4px 12px", borderRadius: 999, fontSize: 12, fontWeight: 600, flexShrink: 0 },

  /* Topics */
  topicGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 14 },
  topicCard: { background: "linear-gradient(145deg, #fff, #faf8ff)", borderRadius: 18, padding: "18px 20px", border: "1px solid #f1f5f9", boxShadow: "0 2px 8px rgba(15,23,42,0.04)", transition: "all 0.25s ease" },
  topicBar: { height: 6, borderRadius: 999, background: "#f1f5f9", overflow: "hidden", marginBottom: 8 },
  dominantBox: { display: "flex", alignItems: "center", gap: 18, marginTop: 22, background: "linear-gradient(135deg,#faf5ff,#f0e7ff)", borderRadius: 18, padding: "20px 24px", border: "1px solid #ede9fe", boxShadow: "0 4px 16px rgba(124,58,237,0.06)" },
  dominantIcon: { width: 52, height: 52, borderRadius: 16, background: "linear-gradient(135deg,#7c3aed,#a855f7)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24, flexShrink: 0, boxShadow: "0 4px 16px rgba(124,58,237,0.25)" },

  /* Chunks */
  select: { padding: "10px 16px", borderRadius: 14, border: "1.5px solid #e2e8f0", minWidth: 200, background: "#fff", color: "#1e293b", fontSize: 13, fontWeight: 500, outline: "none", fontFamily: "inherit" },
  searchInput: { padding: "10px 16px", borderRadius: 14, border: "1.5px solid #e2e8f0", flex: 1, minWidth: 200, background: "#fff", color: "#1e293b", fontSize: 13, fontWeight: 500, outline: "none", fontFamily: "inherit" },
  chunkCard: { background: "linear-gradient(135deg, #f8fafc, #fff)", padding: "16px 20px", borderRadius: 16, marginBottom: 10, border: "1px solid #f1f5f9", cursor: "default", transition: "all 0.2s ease" },

  /* Action btn */
  actionBtn: { marginTop: 16, padding: "11px 24px", borderRadius: 14, border: "none", cursor: "pointer", background: "linear-gradient(135deg,#7c3aed,#a855f7)", color: "#fff", fontWeight: 600, fontSize: 13, boxShadow: "0 4px 16px rgba(124,58,237,0.2)", display: "inline-flex", alignItems: "center", transition: "all 0.25s ease", fontFamily: "inherit" },

  scrollTopBtn: { position: "fixed", bottom: 28, right: 28, zIndex: 150, width: 48, height: 48, borderRadius: 14, border: "none", cursor: "pointer", background: "linear-gradient(135deg,#7c3aed,#a855f7)", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 8px 28px rgba(124,58,237,0.3)", animation: "scrollTopBounce 2s ease-in-out infinite" },
};

export default ResultsDashboard;