import React, { useState, useRef } from 'react';
import './App.css';
import type { ChangeEvent } from 'react';
import type { 
  AnalysisResults, 
  TopicModelResponse, 
  SentimentResponse, 
  SummarizeResponse,
  ReportData 
} from './types';
import ReactMarkdown from 'react-markdown';
import generatePDF from 'react-to-pdf'; // <-- Added PDF Export

const TASKS = [
  { id: 'topic-model', label: 'Topic Extraction', desc: 'Identifies dominant themes' },
  { id: 'sentiment', label: 'Sentiment Analysis', desc: 'Evaluates emotional tone' },
  { id: 'summarize', label: 'Executive Summary', desc: 'Generates a concise overview' }
];

// Reusable SVG Ring Component
const ConfidenceRing = ({ score }: { score: number }) => {
  const radius = 14;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - score * circumference;
  const color = score > 0.7 ? '#10b981' : score > 0.4 ? '#f59e0b' : '#ef4444';

  return (
    <svg width="40" height="40" viewBox="0 0 40 40" style={{ transform: 'rotate(-90deg)' }}>
      <circle cx="20" cy="20" r={radius} fill="transparent" stroke="var(--border)" strokeWidth="4" />
      <circle 
        cx="20" cy="20" r={radius} fill="transparent" 
        stroke={color} strokeWidth="4" strokeLinecap="round"
        strokeDasharray={circumference} strokeDashoffset={offset} 
        style={{ transition: 'stroke-dashoffset 1.5s ease-in-out' }}
      />
      <text x="20" y="20" fill="var(--text-main)" fontSize="10" fontWeight="bold" textAnchor="middle" dy=".3em" style={{ transform: 'rotate(90deg)', transformOrigin: 'center' }}>
        {Math.round(score * 100)}
      </text>
    </svg>
  );
};

// Helper function for Sentiment Emojis
const getSentimentEmoji = (sentiment: string) => {
  const s = sentiment.toLowerCase();
  if (s.includes('positive')) return '🟢 😊';
  if (s.includes('negative')) return '🔴 😠';
  return '⚪ 😐';
};

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [selectedTask, setSelectedTask] = useState<string>('analyze');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [statusMsg, setStatusMsg] = useState<string>('');
  const [reportData, setReportData] = useState<ReportData | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const reportRef = useRef<HTMLDivElement>(null); // <-- Reference for PDF Export

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const isValid = /\.(pdf|docx|pptx|html|xml|txt|md)$/i.test(selectedFile.name);
      if (isValid) {
        setFile(selectedFile);
        setReportData(null);
      } else {
        alert("Please upload a supported document (.pdf, .docx, .pptx, .txt, etc).");
      }
    }
  };

  const pollAsyncTask = async (taskId: string): Promise<AnalysisResults> => {
    for (let i = 0; i < 300; i++) {
      const res = await fetch(`/analyze/${taskId}`);
      const data = await res.json();
      if (data.status === 'completed') return data.results;
      if (data.status === 'failed') throw new Error(`Backend Error: ${data.error}`);
      await new Promise(r => setTimeout(r, 1500));
    }
    throw new Error("Analysis timeout. Check backend logs.");
  };

  const runAnalysis = async () => {
    if (!file) return;
    setIsProcessing(true);
    setStatusMsg('Initializing engine...');
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      if (selectedTask === 'analyze') {
        setStatusMsg('Uploading to async pipeline...');
        const res = await fetch('/analyze', { method: 'POST', body: formData });
        const data = await res.json();
        
        setStatusMsg('Processing (this may take a minute)...');
        const finalResults = await pollAsyncTask(data.task_id);
        setReportData({ type: 'full', filename: file.name, data: finalResults });
      } else {
        setStatusMsg(`Running ${selectedTask}...`);
        const res = await fetch(`/${selectedTask}`, { method: 'POST', body: formData });
        const data = await res.json();
        setReportData({ type: selectedTask as ReportData['type'], filename: file.name, data: data });
      }
      setStatusMsg('');
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div className="logo-area">
          <p>Text Analytics Engine</p>
        </div>

        <div className="task-selector">
          <span className="task-label">1. Upload Document</span>
          <div className={`file-upload ${file ? 'has-file' : ''}`} onClick={() => fileInputRef.current?.click()}>
            <input 
              type="file" ref={fileInputRef} accept=".pdf,.docx,.pptx,.txt,.html,.md" 
              className="file-input-hidden" onChange={handleFileChange} 
              aria-label="Upload Document" title="Upload Document"
            />
            {file ? (
              <p>📄 <strong style={{color: 'var(--accent)'}}>{file.name}</strong></p>
            ) : (
              <p>+ Click to select Document</p>
            )}
          </div>
        </div>

        <div className="task-selector">
          <span className="task-label">2. Select Processing Mode</span>
          {TASKS.map(task => (
            <div key={task.id} className={`radio-card ${selectedTask === task.id ? 'selected' : ''}`} onClick={() => setSelectedTask(task.id)}>
              <input 
                type="radio" name="task_selection" checked={selectedTask === task.id} 
                readOnly aria-label={task.label} title={task.label}
              />
              <div>
                <strong>{task.label}</strong>
                <p style={{fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px'}}>{task.desc}</p>
              </div>
            </div>
          ))}
        </div>

        <button className="btn-primary" onClick={runAnalysis} disabled={!file || isProcessing}>
          {isProcessing ? 'Processing Engine...' : 'Run Analysis'}
        </button>
        {statusMsg && <p className="status-text pulse-text">{statusMsg}</p>}
      </aside>

      <main className="report-area">
        {!reportData && !isProcessing && (
          <div className="empty-state fade-in">
            <div style={{fontSize: '4rem', marginBottom: '2rem', opacity: 0.5}}>📄</div>
            <p>Upload a file to generate intelligence insights.</p>
          </div>
        )}

        {isProcessing && !reportData && (
          <div className="empty-state fade-in">
            <div className="spinner"></div>
            <h2 style={{marginTop: '2rem'}}>Analyzing Document...</h2>
            <p style={{color: 'var(--text-muted)'}}>Extracting text and running ML models</p>
          </div>
        )}

        {reportData && (
          <div className="report-content fade-in" ref={reportRef}>
            
            {/* Beautiful Header with Export Button */}
            <div className="report-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2>Intelligence Report</h2>
                <div style={{marginTop: '0.5rem'}}>
                  <span className="badge">File: {reportData.filename}</span>
                  <span className="badge">Mode: {selectedTask.toUpperCase()}</span>
                </div>
              </div>
              
              <button 
                className="btn-export"
                onClick={() => generatePDF(reportRef, {filename: 'Nexus_Report.pdf'})}
              >
                📥 Download PDF
              </button>
            </div>

            {/* SUMMARY BLOCK */}
            {(reportData.type === 'full' || reportData.type === 'summarize') && (
              <div className="content-card">
                <h3 className="section-title">📝 Executive Summary</h3>
                <div className="summary-text">
                  <ReactMarkdown>
                    {reportData.type === 'full' 
                      ? (reportData.data as AnalysisResults).summarization.summary 
                      : (reportData.data as SummarizeResponse).summary}
                  </ReactMarkdown>
                </div>
              </div>
            )}

            {/* TOPIC BLOCK */}
            {(reportData.type === 'full' || reportData.type === 'topic-model') && (() => {
              const topicData = reportData.type === 'full' 
                ? (reportData.data as AnalysisResults).topic_modeling 
                : (reportData.data as TopicModelResponse);
              return (
                <div className="content-card">
                  <h3 className="section-title">🎯 Dominant Topic Analysis</h3>
                  <div className="stats-grid">
                    <div className="stat-box">
                      <div className="val">{topicData.dominant_topic.label}</div>
                      <div className="lbl">Primary Classification</div>
                    </div>
                    <div className="stat-box">
                      <div className="val">{topicData.dominant_topic.chunks_matched} / {topicData.dominant_topic.total_chunks}</div>
                      <div className="lbl">Document Chunks Matched</div>
                    </div>
                  </div>
                  
                  <h4 style={{marginBottom: '1rem', color: 'var(--text-muted)'}}>All Topics Detected:</h4>
                  {topicData.all_topics_found.map(t => (
                    <div key={t.topic_id} className="data-row" style={{ alignItems: 'center' }}>
                      <span style={{ fontWeight: 500, fontSize: '1.05rem' }}>{t.label}</span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <span className="badge" style={{ margin: 0, background: 'rgba(255,255,255,0.05)' }}>
                          Score: {(t.avg_score * 100).toFixed(1)}%
                        </span>
                        <ConfidenceRing score={t.avg_score} />
                      </div>
                    </div>
                  ))}
                </div>
              );
            })()}

            {/* SENTIMENT BLOCK */}
            {(reportData.type === 'full' || reportData.type === 'sentiment') && (() => {
              const sentData = reportData.type === 'full' 
                ? (reportData.data as AnalysisResults).sentiment_analysis 
                : (reportData.data as SentimentResponse);
              return (
                <div className="content-card">
                  <h3 className="section-title">🎭 Sentiment Breakdown</h3>
                  <div className="stats-grid" style={{marginBottom: '2rem'}}>
                    <div className="stat-box" style={{borderLeft: '4px solid var(--accent)'}}>
                      <div className="val" style={{textTransform: 'capitalize'}}>
                        {getSentimentEmoji(sentData.overall_sentiment)} {sentData.overall_sentiment}
                      </div>
                      <div className="lbl">Overall Document Tone</div>
                    </div>
                  </div>

                  <h4 style={{marginBottom: '1rem', color: 'var(--text-muted)'}}>Sentence Level Analysis:</h4>
                  {sentData.per_sentence.map((s, i) => (
                    <div key={i} className="data-row" style={{flexDirection: 'column', gap: '0.75rem', alignItems: 'flex-start', padding: '1.5rem 0'}}>
                      <span className={`pill ${s.label}`}>{s.label.toUpperCase()} ({Math.round(s.score * 100)}% Confident)</span>
                      <span style={{fontSize: '0.95rem', color: '#e2e8f0', lineHeight: 1.5, fontStyle: 'italic'}}>"{s.sentence}"</span>
                    </div>
                  ))}
                </div>
              );
            })()}
          </div>
        )}
      </main>
    </div>
  );
}