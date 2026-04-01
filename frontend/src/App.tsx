import { useState, useRef } from 'react';
import type { ChangeEvent } from 'react';
import './App.css';
import type { 
  AnalysisResults, 
  TopicModelResponse, 
  SentimentResponse, 
  SummarizeResponse,
  ReportData 
} from './types';
import ReactMarkdown from 'react-markdown';
import jsPDF from 'jspdf';
import { 
  WordCloud, 
  SentimentDistributionChart, 
  TopicDistributionChart, 
  SentimentTrendChart
} from './Visualizations';

// --- Clean SVG Icons ---
const Icons = {
  Upload: () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>,
  File: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>,
  Download: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>,
  Activity: () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>,
  Check: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
};

const TASKS = [
  { id: 'topic-model', label: 'Topic Extraction', desc: 'Identifies dominant themes & subjects' },
  { id: 'sentiment', label: 'Sentiment Analysis', desc: 'Evaluates emotional tone & polarity' },
  { id: 'summarize', label: 'Executive Summary', desc: 'Generates a concise overview' }
];

const ConfidenceRing = ({ score }: { score: number }) => {
  const radius = 16;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - score * circumference;
  const color = score > 0.75 ? 'var(--success)' : score > 0.45 ? 'var(--warning)' : 'var(--danger)';

  return (
    <div className="confidence-ring-wrapper">
      <svg width="48" height="48" viewBox="0 0 48 48" className="confidence-ring-svg">
        <circle cx="24" cy="24" r={radius} fill="transparent" stroke="var(--border-light)" strokeWidth="4" />
        <circle 
          cx="24" cy="24" r={radius} fill="transparent" 
          stroke={color} strokeWidth="4" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset} 
          className="confidence-ring-circle"
        />
      </svg>
      <div className="confidence-ring-text">
        {Math.round(score * 100)}<span className="percentage-symbol">%</span>
      </div>
    </div>
  );
};

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [selectedTask, setSelectedTask] = useState<string>('analyze');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [statusMsg, setStatusMsg] = useState<string>('');
  const [reportData, setReportData] = useState<ReportData | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const reportRef = useRef<HTMLDivElement>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const isValid = /\.(pdf|docx|pptx|html|xml|txt|md)$/i.test(selectedFile.name);
      if (isValid) {
        setFile(selectedFile);
        setReportData(null);
      } else {
        alert("Please upload a supported document format.");
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

  const generatePDFReport = () => {
    if (!reportData) return;
    
    const doc = new jsPDF();
    let yPosition = 20;
    const pageHeight = doc.internal.pageSize.height;
    const margin = 20;
    const maxWidth = doc.internal.pageSize.width - 2 * margin;

    // Helper function to add text with wrapping
    const addWrappedText = (text: string, fontSize: number, isBold: boolean = false) => {
      doc.setFontSize(fontSize);
      doc.setFont('helvetica', isBold ? 'bold' : 'normal');
      const lines = doc.splitTextToSize(text, maxWidth);
      lines.forEach((line: string) => {
        if (yPosition > pageHeight - 20) {
          doc.addPage();
          yPosition = 20;
        }
        doc.text(line, margin, yPosition);
        yPosition += fontSize / 2.5;
      });
      yPosition += 5;
    };

    // Title
    doc.setTextColor(0, 0, 0);
    addWrappedText('Intelligence Report', 18, true);
    addWrappedText(`Document: ${reportData.filename}`, 11, false);
    addWrappedText(`Analysis Type: ${selectedTask.toUpperCase().replace('-', ' ')}`, 11, false);
    yPosition += 5;

    // Summary Section
    if (reportData.type === 'full' || reportData.type === 'summarize') {
      addWrappedText('Executive Summary', 14, true);
      const summary = reportData.type === 'full' 
        ? (reportData.data as AnalysisResults).summarization.summary 
        : (reportData.data as SummarizeResponse).summary;
      addWrappedText(summary || 'No summary available', 10, false);
      yPosition += 5;
    }

    // Topics Section
    if (reportData.type === 'full' || reportData.type === 'topic-model') {
      addWrappedText('Dominant Topics', 14, true);
      const topicData = reportData.type === 'full' 
        ? (reportData.data as AnalysisResults).topic_modeling 
        : (reportData.data as TopicModelResponse);
      
      addWrappedText(`Primary: ${topicData.dominant_topic.label}`, 11, true);
      addWrappedText(`Matched ${topicData.dominant_topic.chunks_matched} of ${topicData.dominant_topic.total_chunks} chunks`, 10, false);
      yPosition += 3;
      
      addWrappedText('Confidence Distribution:', 10, true);
      topicData.all_topics_found.forEach(t => {
        const score = Math.round(t.avg_score * 100);
        addWrappedText(`• ${t.label}: ${score}%`, 9, false);
      });
      yPosition += 5;
    }

    // Sentiment Section
    if (reportData.type === 'full' || reportData.type === 'sentiment') {
      addWrappedText('Sentiment Analysis', 14, true);
      const sentData = reportData.type === 'full' 
        ? (reportData.data as AnalysisResults).sentiment_analysis 
        : (reportData.data as SentimentResponse);
      
      addWrappedText(`Overall Tone: ${sentData.overall_sentiment}`, 11, true);
      yPosition += 3;
      
      addWrappedText('Sentence Level Breakdown:', 10, true);
      sentData.per_sentence.slice(0, 10).forEach(s => {
        const score = Math.round(s.score * 100);
        addWrappedText(`• [${s.label}] ${score}%: "${s.sentence}"`, 8, false);
      });
      if (sentData.per_sentence.length > 10) {
        addWrappedText(`... and ${sentData.per_sentence.length - 10} more sentences`, 9, false);
      }
    }

    doc.save('Nexus_Report.pdf');
  };

  const runAnalysis = async () => {
    if (!file) return;
    setIsProcessing(true);
    setStatusMsg('Initializing analytics engine...');
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      if (selectedTask === 'analyze') {
        setStatusMsg('Uploading to asynchronous pipeline...');
        const res = await fetch('/analyze', { method: 'POST', body: formData });
        const data = await res.json();
        
        setStatusMsg('Processing machine learning models...');
        const finalResults = await pollAsyncTask(data.task_id);
        setReportData({ type: 'full', filename: file.name, data: finalResults });
      } else {
        setStatusMsg(`Executing ${selectedTask.replace('-', ' ')}...`);
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
          <div className="logo-icon"><Icons.Activity /></div>
          <div>
            <h1 className="gradient-text">Analyze Documents</h1>
            <p>AI-Powered Intelligence</p>
          </div>
        </div>

        <div className="sidebar-scroll">
          <div className="task-group">
            <span className="task-label">1. Data Source</span>
            <div 
              className={`file-upload ${file ? 'has-file' : ''}`} 
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                type="file" ref={fileInputRef} accept=".pdf,.docx,.pptx,.txt,.html,.md" 
                className="file-input-hidden" onChange={handleFileChange}
                aria-label="Upload document file"
              />
              {file ? (
                <div className="file-active">
                  <Icons.File />
                  <span className="file-name">{file.name}</span>
                  <div className="file-check"><Icons.Check /></div>
                </div>
              ) : (
                <div className="file-prompt">
                  <Icons.Upload />
                  <p><strong>Click to browse</strong> or drag file here</p>
                  <span className="file-hint">Supports PDF, DOCX, TXT, MD</span>
                </div>
              )}
            </div>
          </div>

          <div className="task-group">
            <span className="task-label">2. Processing Profile</span>
            <div className="radio-group">
              {TASKS.map(task => (
                <div 
                  key={task.id} 
                  className={`radio-card ${selectedTask === task.id ? 'selected' : ''}`} 
                  onClick={() => setSelectedTask(task.id)}
                >
                  <div className="radio-card-content">
                    <strong>{task.label}</strong>
                    <p>{task.desc}</p>
                  </div>
                  <div className="radio-indicator"></div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="sidebar-footer">
          <button className="btn-primary" onClick={runAnalysis} disabled={!file || isProcessing}>
            {isProcessing ? (
              <span className="btn-content"><div className="spinner-small"></div> Processing...</span>
            ) : 'Initialize Analysis'}
          </button>
          <div className="status-container">
            {statusMsg && <p className="status-text pulse-text">{statusMsg}</p>}
          </div>
        </div>
      </aside>

      <main className="report-area">
        {!reportData && !isProcessing && (
          <div className="empty-state fade-in">
            <div className="empty-icon-wrapper"><Icons.File /></div>
            <h2>No Document Selected</h2>
            <p>Upload a file and run the analysis to generate intelligence insights.</p>
          </div>
        )}

        {isProcessing && !reportData && (
          <div className="empty-state fade-in">
            <div className="spinner-large"></div>
            <h2 className="processing-title">Analyzing Document</h2>
            <p>Extracting context and evaluating ML models...</p>
          </div>
        )}

        {reportData && (
          <div className="report-container fade-in" ref={reportRef}>
            <header className="report-header">
              <div className="header-titles">
                <div className="meta-tags">
                  <span className="tag"><Icons.File /> {reportData.filename}</span>
                  <span className="tag tag-accent">{selectedTask.toUpperCase().replace('-', ' ')}</span>
                </div>
              </div>
              <button className="btn-export" onClick={generatePDFReport}>
                <Icons.Download /> Export PDF
              </button>
            </header>

            <div className="report-grid">
              {/* SUMMARY BLOCK */}
              {(reportData.type === 'full' || reportData.type === 'summarize') && (
                <section className="content-card full-width">
                  <div className="card-header">
                    <h3 className="section-title">Executive Summary</h3>
                  </div>
                  <div className="summary-text prose">
                    <ReactMarkdown>
                      {reportData.type === 'full' 
                        ? (reportData.data as AnalysisResults).summarization.summary 
                        : (reportData.data as SummarizeResponse).summary}
                    </ReactMarkdown>
                  </div>
                </section>
              )}

              {/* TOPIC BLOCK */}
              {(reportData.type === 'full' || reportData.type === 'topic-model') && (() => {
                const topicData = reportData.type === 'full' 
                  ? (reportData.data as AnalysisResults).topic_modeling 
                  : (reportData.data as TopicModelResponse);
                return (
                  <>
                    <section className="content-card full-width">
                      <div className="card-header">
                        <h3 className="section-title">Topic Distribution</h3>
                      </div>
                      <TopicDistributionChart topicData={topicData} />
                    </section>



                    <section className="content-card">
                      <div className="card-header">
                        <h3 className="section-title">Dominant Topics</h3>
                      </div>
                      
                      <div className="primary-stat-box">
                        <div className="stat-label">Primary Classification</div>
                        <div className="stat-value">{topicData.dominant_topic.label}</div>
                        <div className="stat-sub">Matched {topicData.dominant_topic.chunks_matched} of {topicData.dominant_topic.total_chunks} chunks</div>
                      </div>
                      
                      <h4 className="sub-heading">Confidence Distribution</h4>
                      <div className="topic-list">
                        {topicData.all_topics_found.map(t => (
                          <div key={t.topic_id} className="topic-row">
                            <span className="topic-name">{t.label}</span>
                            <ConfidenceRing score={t.avg_score} />
                          </div>
                        ))}
                      </div>
                    </section>
                  </>
                );
              })()}

              {/* SENTIMENT BLOCK */}
              {(reportData.type === 'full' || reportData.type === 'sentiment') && (() => {
                const sentData = reportData.type === 'full' 
                  ? (reportData.data as AnalysisResults).sentiment_analysis 
                  : (reportData.data as SentimentResponse);
                
                const overallSent = sentData.overall_sentiment.toLowerCase();
                const sentimentColor = overallSent.includes('positive') ? 'success' : overallSent.includes('negative') ? 'danger' : 'neutral';

                return (
                  <>
                    <section className="content-card">
                      <div className="card-header">
                        <h3 className="section-title">Sentiment Analysis</h3>
                      </div>
                      
                      <div className={`primary-stat-box sentiment-${sentimentColor}`}>
                        <div className="stat-label">Overall Document Tone</div>
                        <div className="stat-value capitalize">{sentData.overall_sentiment}</div>
                      </div>

                      <h4 className="sub-heading">Sentence Level Breakdown</h4>
                      <div className="sentence-list">
                        {sentData.per_sentence.slice(0, 5).map((s, i) => (
                          <div key={i} className="sentence-row">
                            <div className="sentence-meta">
                              <span className={`pill pill-${s.label.toLowerCase()}`}>{s.label}</span>
                              <span className="confidence-text">{Math.round(s.score * 100)}% Match</span>
                            </div>
                            <p className="sentence-content">"{s.sentence}"</p>
                          </div>
                        ))}
                      </div>
                    </section>

                    <section className="content-card">
                      <div className="card-header">
                        <h3 className="section-title">Sentiment Distribution</h3>
                      </div>
                      <SentimentDistributionChart sentimentData={sentData} />
                    </section>

                    <section className="content-card full-width">
                      <div className="card-header">
                        <h3 className="section-title">Sentiment Trend Analysis</h3>
                      </div>
                      <SentimentTrendChart sentimentData={sentData} />
                    </section>
                  </>
                );
              })()}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}