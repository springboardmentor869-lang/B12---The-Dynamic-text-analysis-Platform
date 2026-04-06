import { useCallback, useEffect, useRef, useState } from 'react'
import { Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import './App.css'

interface EndpointConfig {
  label: string
  color: string
  mode: 'async' | 'sync'
}

type EndpointKey = 'analyze' | 'topic-model' | 'sentiment' | 'summarize'
type TabId = 'overview' | 'topic' | 'sentiment' | 'summary' | 'chunks' | 'sentences'

type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed'

interface DominantTopic {
  topic_id: number
  label: string
  avg_similarity_score: number
  chunks_matched: number
  total_chunks: number
}

interface TopicFound {
  topic_id: number
  label: string
  chunks_matched: number
  avg_score: number
}

interface ChunkDetail {
  chunk_id: number
  preview: string
  topic_id: number
  label: string
  score: number
  keywords: string[]
}

interface TopicModelingResult {
  dominant_topic: DominantTopic
  all_topics_found: TopicFound[]
  chunk_details: ChunkDetail[]
}

interface SentenceSentiment {
  sentence: string
  label: string
  score: number
  chunked?: boolean
}

interface SentimentSummary {
  positive: number
  negative: number
  neutral: number
}

interface SentimentResult {
  overall_sentiment: string
  summary?: SentimentSummary
  per_sentence: SentenceSentiment[]
}

interface SummarizationResult {
  summary: string
  word_count: number
}

interface AnalysisResults {
  file_name: string
  topic_modeling: TopicModelingResult
  sentiment_analysis: SentimentResult
  summarization: SummarizationResult
  processing_time_seconds: number
}

interface AnalyzeSubmitResponse {
  task_id: string
  status: string
  message: string
}

interface AnalyzeStatusResponse {
  task_id: string
  status: TaskStatus
  results?: AnalysisResults
  error?: string
  processing_time_seconds?: number
}

interface TopicModelResponse {
  dominant_topic: DominantTopic
  all_topics_found: TopicFound[]
  chunk_details: ChunkDetail[]
}

interface SentimentResponse {
  overall_sentiment: string
  per_sentence: SentenceSentiment[]
}

interface SummarizeResponse {
  summary: string
  word_count: number
}

interface DisplayResults {
  endpoint: EndpointKey
  filename: string
  processingTimeSeconds?: number
  topicModeling?: TopicModelingResult
  sentimentAnalysis?: SentimentResult
  summarization?: SummarizationResult
}

const ENDPOINTS: Record<EndpointKey, EndpointConfig> = {
  analyze: { label: 'Analyze Full Document', color: '#0d7377', mode: 'async' },
  'topic-model': { label: 'Topic Modeling', color: '#5b8def', mode: 'sync' },
  sentiment: { label: 'Sentiment Analysis', color: '#e67e22', mode: 'sync' },
  summarize: { label: 'Summarization', color: '#2eab59', mode: 'sync' }
}

const SENTIMENT_COLORS: Record<string, { bg: string; border: string; text: string; icon: string }> = {
  positive: { bg: 'rgba(46, 171, 89, 0.1)', border: '#2eab59', text: '#2eab59', icon: '+' },
  negative: { bg: 'rgba(231, 76, 60, 0.1)', border: '#e74c3c', text: '#e74c3c', icon: '-' },
  neutral: { bg: 'rgba(91, 141, 239, 0.1)', border: '#5b8def', text: '#5b8def', icon: 'o' }
}

function Header({ showBack = false, onBack }: { showBack?: boolean; onBack?: () => void }) {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <rect x="2" y="2" width="28" height="28" rx="6" stroke="currentColor" strokeWidth="2" />
            <path d="M8 12h16M8 16h12M8 20h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <circle cx="24" cy="20" r="3" fill="var(--accent-primary)" />
          </svg>
          <span className="logo-text">Dynamic Text</span>
        </div>
        <nav className="nav">
          {showBack ? (
            <button className="nav-back" onClick={onBack}>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M10 4L6 8l4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Back to Upload
            </button>
          ) : (
            <span className="nav-badge">PDF NLP Analysis</span>
          )}
        </nav>
      </div>
    </header>
  )
}

function DropZone({
  onFileSelect,
  isLoading,
  selectedFile
}: {
  onFileSelect: (file: File) => void
  isLoading: boolean
  selectedFile: File | null
}) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    const files = e.dataTransfer?.files
    if (files && files.length > 0) {
      onFileSelect(files[0])
    }
  }, [onFileSelect])

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      onFileSelect(files[0])
    }
  }, [onFileSelect])

  return (
    <div
      className={`dropzone ${isDragging ? 'dragging' : ''} ${selectedFile ? 'has-file' : ''} ${isLoading ? 'loading' : ''}`}
      onDragEnter={handleDragIn}
      onDragLeave={handleDragOut}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        onChange={handleChange}
        className="dropzone-input"
      />
      <div className="dropzone-content">
        {isLoading ? (
          <>
            <div className="dropzone-spinner">
              <svg width="48" height="48" viewBox="0 0 48 48" className="spinner">
                <circle cx="24" cy="24" r="20" stroke="var(--border-medium)" strokeWidth="4" fill="none" />
                <circle cx="24" cy="24" r="20" stroke="var(--accent-primary)" strokeWidth="4" fill="none" strokeDasharray="80 40" />
              </svg>
            </div>
            <p className="dropzone-text">Processing document...</p>
          </>
        ) : selectedFile ? (
          <>
            <div className="dropzone-icon file-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <rect x="8" y="4" width="24" height="32" rx="3" stroke="currentColor" strokeWidth="2" />
                <path d="M32 8h8a2 2 0 012 2v28a2 2 0 01-2 2H14a2 2 0 01-2-2V14l10-10z" stroke="currentColor" strokeWidth="2" />
                <path d="M26 4v10h10" stroke="currentColor" strokeWidth="2" />
                <path d="M16 20h16M16 26h12M16 32h8" stroke="var(--accent-primary)" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </div>
            <p className="dropzone-filename">{selectedFile.name}</p>
            <p className="dropzone-hint">Click or drag to replace</p>
          </>
        ) : (
          <>
            <div className="dropzone-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <rect x="8" y="14" width="32" height="24" rx="3" stroke="currentColor" strokeWidth="2" />
                <path d="M24 8v20M16 18l8-8 8 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <p className="dropzone-text">Drop PDF here or click to browse</p>
            <p className="dropzone-hint">Maximum file size: 50MB</p>
          </>
        )}
      </div>
    </div>
  )
}

function EndpointSelector({
  selectedEndpoint,
  onSelect,
  disabled
}: {
  selectedEndpoint: EndpointKey
  onSelect: (endpoint: EndpointKey) => void
  disabled: boolean
}) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className={`endpoint-selector ${disabled ? 'disabled' : ''}`}>
      <button
        className="endpoint-trigger"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
      >
        <span className="trigger-label">{ENDPOINTS[selectedEndpoint]?.label || 'Select Analysis'}</span>
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className={`trigger-arrow ${isOpen ? 'open' : ''}`}>
          <path d="M4 6l4 4 4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
      {isOpen && (
        <div className="endpoint-dropdown">
          {(Object.entries(ENDPOINTS) as [EndpointKey, EndpointConfig][]).map(([key, { label, color }]) => (
            <button
              key={key}
              className={`endpoint-option ${selectedEndpoint === key ? 'active' : ''}`}
              onClick={() => {
                onSelect(key)
                setIsOpen(false)
              }}
            >
              <span className="option-dot" style={{ background: color }} />
              {label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function AnalyzeButton({ onClick, isLoading, disabled }: { onClick: () => void; isLoading: boolean; disabled: boolean }) {
  return (
    <button className={`analyze-button ${isLoading ? 'loading' : ''}`} onClick={onClick} disabled={disabled || isLoading}>
      {isLoading ? (
        <>
          <svg width="20" height="20" viewBox="0 0 20 20" className="btn-spinner">
            <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2" fill="none" strokeDasharray="30 20" />
          </svg>
          Analyzing...
        </>
      ) : (
        <>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 2v4M10 14v4M2 10h4M14 10h4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <circle cx="10" cy="10" r="3" fill="currentColor" />
          </svg>
          Analyze Document
        </>
      )}
    </button>
  )
}

function StatusMessage({ status, error }: { status?: string | null; error?: string | null }) {
  if (!status && !error) return null

  return (
    <div className={`status-message ${error ? 'error' : 'success'}`}>
      {error ? (
        <>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2" />
            <path d="M10 6v5M10 13v1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <span>{error}</span>
        </>
      ) : (
        <>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2" />
            <path d="M6 10l3 3 5-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span>{status}</span>
        </>
      )}
    </div>
  )
}

async function pollAnalyzeTask(taskId: string): Promise<AnalyzeStatusResponse> {
  const maxAttempts = 120
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const response = await fetch(`/analyze/${taskId}`)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Polling failed with HTTP ${response.status}`)
    }

    const data = (await response.json()) as AnalyzeStatusResponse
    if (data.status === 'completed' || data.status === 'failed') {
      return data
    }

    await new Promise((resolve) => {
      window.setTimeout(resolve, 1500)
    })
  }

  throw new Error('Analysis timeout. Please try a smaller PDF or retry.')
}

function normalizeDisplayResults(endpoint: EndpointKey, filename: string, data: AnalysisResults | TopicModelResponse | SentimentResponse | SummarizeResponse): DisplayResults {
  if (endpoint === 'analyze') {
    const analyzed = data as AnalysisResults
    return {
      endpoint,
      filename: analyzed.file_name || filename,
      processingTimeSeconds: analyzed.processing_time_seconds,
      topicModeling: analyzed.topic_modeling,
      sentimentAnalysis: analyzed.sentiment_analysis,
      summarization: analyzed.summarization
    }
  }

  if (endpoint === 'topic-model') {
    return {
      endpoint,
      filename,
      topicModeling: data as TopicModelResponse
    }
  }

  if (endpoint === 'sentiment') {
    return {
      endpoint,
      filename,
      sentimentAnalysis: data as SentimentResponse
    }
  }

  return {
    endpoint,
    filename,
    summarization: data as SummarizeResponse
  }
}

function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedEndpoint, setSelectedEndpoint] = useState<EndpointKey>('analyze')
  const [isLoading, setIsLoading] = useState(false)
  const [status, setStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const handleFileSelect = useCallback((file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a PDF file')
      return
    }
    setSelectedFile(file)
    setError(null)
  }, [])

  const handleAnalyze = useCallback(async () => {
    if (!selectedFile) return

    setIsLoading(true)
    setError(null)
    setStatus('Uploading PDF...')

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      if (ENDPOINTS[selectedEndpoint].mode === 'async') {
        const submitResponse = await fetch('/analyze', {
          method: 'POST',
          body: formData
        })

        if (!submitResponse.ok) {
          const errorData = await submitResponse.json().catch(() => ({}))
          throw new Error(errorData.detail || `HTTP ${submitResponse.status}`)
        }

        const submitData = (await submitResponse.json()) as AnalyzeSubmitResponse
        setStatus('Running topic, sentiment, and summary pipelines...')

        const finalStatus = await pollAnalyzeTask(submitData.task_id)
        if (finalStatus.status === 'failed') {
          throw new Error(finalStatus.error || 'Analysis failed')
        }

        if (!finalStatus.results) {
          throw new Error('No results returned from backend')
        }

        const payload = normalizeDisplayResults(selectedEndpoint, selectedFile.name, finalStatus.results)
        navigate('/results', { state: { results: payload } })
        return
      }

      setStatus(`Running ${ENDPOINTS[selectedEndpoint].label.toLowerCase()}...`)
      
      const API_BASE = "http://127.0.0.1:8000";

      const response = await fetch(`${API_BASE}/${selectedEndpoint}`, {        
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }

      const data = (await response.json()) as TopicModelResponse | SentimentResponse | SummarizeResponse
      const payload = normalizeDisplayResults(selectedEndpoint, selectedFile.name, data)
      navigate('/results', { state: { results: payload } })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.')
    } finally {
      setIsLoading(false)
      setStatus(null)
    }
  }, [navigate, selectedEndpoint, selectedFile])

  return (
    <div className="upload-page">
      <div className="upload-section">
        <DropZone onFileSelect={handleFileSelect} isLoading={isLoading} selectedFile={selectedFile} />

        <div className="controls">
          <EndpointSelector selectedEndpoint={selectedEndpoint} onSelect={setSelectedEndpoint} disabled={isLoading} />
          <AnalyzeButton onClick={handleAnalyze} isLoading={isLoading} disabled={!selectedFile} />
        </div>

        <StatusMessage status={status} error={error} />
      </div>
    </div>
  )
}

function OverviewPanel({ results }: { results: DisplayResults }) {
  const stats: { label: string; value: string | number; subvalue?: string; icon: string }[] = [
    { label: 'Pipeline', value: ENDPOINTS[results.endpoint].label, icon: '◎' },
    { label: 'Filename', value: results.filename, icon: '▢' }
  ]

  if (results.processingTimeSeconds !== undefined) {
    stats.push({ label: 'Processing Time', value: `${results.processingTimeSeconds}s`, icon: '◷' })
  }

  if (results.topicModeling) {
    stats.push({ label: 'Dominant Topic', value: results.topicModeling.dominant_topic.label, icon: '◆' })
    stats.push({ label: 'Topic Chunks', value: results.topicModeling.dominant_topic.chunks_matched, icon: '#' })
  }

  if (results.sentimentAnalysis) {
    stats.push({ label: 'Overall Sentiment', value: results.sentimentAnalysis.overall_sentiment, icon: '◐' })
    stats.push({ label: 'Sentences', value: results.sentimentAnalysis.per_sentence.length, icon: '¶' })
  }

  if (results.summarization) {
    stats.push({ label: 'Summary Words', value: results.summarization.word_count, icon: '✎' })
  }

  return (
    <div className="panel overview-panel">
      <div className="stats-grid">
        {stats.map((stat, index) => (
          <div key={`${stat.label}-${index}`} className="stat-card" style={{ animationDelay: `${index * 80}ms` }}>
            <span className="stat-icon">{stat.icon}</span>
            <div className="stat-content">
              <span className="stat-value">{stat.value}</span>
              {stat.subvalue && <span className="stat-subvalue">{stat.subvalue}</span>}
              <span className="stat-label">{stat.label}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function TopicPanel({ topicModeling }: { topicModeling: TopicModelingResult }) {
  return (
    <div className="panel topic-panel">
      <div className="sentiment-summary">
        <div className="sentiment-badge" style={{ color: '#0d7377', borderColor: '#0d7377', background: 'rgba(13, 115, 119, 0.1)' }}>
          Topic #{topicModeling.dominant_topic.topic_id}
        </div>
        <div className="sentiment-score">
          <span className="score-value">{topicModeling.dominant_topic.label}</span>
          <span className="score-label">Dominant Topic</span>
        </div>
      </div>

      <div className="sentiment-breakdown">
        <h4 className="breakdown-title">All Topics Found</h4>
        <div className="breakdown-bars">
          {topicModeling.all_topics_found.map((topic) => (
            <div key={`${topic.topic_id}-${topic.label}`} className="breakdown-row">
              <span className="breakdown-label">{topic.label}</span>
              <div className="breakdown-bar-container">
                <div className="breakdown-bar" style={{ width: `${Math.min(100, topic.avg_score * 100)}%`, background: '#0d7377' }} />
              </div>
              <span className="breakdown-pct">{topic.avg_score.toFixed(2)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function ChunkPanel({ topicModeling }: { topicModeling: TopicModelingResult }) {
  return (
    <div className="panel sentiment-panel">
      <div className="sentiment-sentences">
        <h4 className="sentences-title">Chunk Level Matches</h4>
        <div className="sentences-list">
          {topicModeling.chunk_details.map((chunk) => (
            <div key={chunk.chunk_id} className="sentence-item" style={{ borderColor: 'rgba(13, 115, 119, 0.3)' }}>
              <span className="sentence-label" style={{ color: '#0d7377', background: 'rgba(13, 115, 119, 0.1)' }}>
                {chunk.label} {chunk.score.toFixed(2)}
              </span>
              <span className="sentence-text">{chunk.preview}</span>
            </div>
          ))}
          {topicModeling.chunk_details.length === 0 && <div className="empty-state">No chunk details returned.</div>}
        </div>
      </div>
    </div>
  )
}

function SentimentPanel({ sentimentAnalysis }: { sentimentAnalysis: SentimentResult }) {
  const colors = SENTIMENT_COLORS[sentimentAnalysis.overall_sentiment] || SENTIMENT_COLORS.neutral
  const grouped = sentimentAnalysis.per_sentence.reduce((acc, sentence) => {
    const label = sentence.label || 'neutral'
    if (!acc[label]) {
      acc[label] = []
    }
    acc[label].push(sentence)
    return acc
  }, {} as Record<string, SentenceSentiment[]>)

  return (
    <div className="panel sentiment-panel">
      <div className="sentiment-summary" style={{ background: colors.bg, borderColor: colors.border }}>
        <div className="sentiment-badge" style={{ color: colors.text, borderColor: colors.border }}>
          <span className="sentiment-icon">{colors.icon}</span>
          {sentimentAnalysis.overall_sentiment.toUpperCase()}
        </div>
        <div className="sentiment-score">
          <span className="score-value">{sentimentAnalysis.per_sentence.length}</span>
          <span className="score-label">Sentences Analyzed</span>
        </div>
      </div>

      <div className="sentiment-breakdown">
        <h4 className="breakdown-title">Sentiment Distribution</h4>
        <div className="breakdown-bars">
          {Object.entries(grouped).map(([label, items]) => {
            const percentage = sentimentAnalysis.per_sentence.length
              ? ((items.length / sentimentAnalysis.per_sentence.length) * 100).toFixed(1)
              : '0.0'
            const groupColor = SENTIMENT_COLORS[label] || SENTIMENT_COLORS.neutral
            return (
              <div key={label} className="breakdown-row">
                <span className="breakdown-label" style={{ color: groupColor.text }}>{label}</span>
                <div className="breakdown-bar-container">
                  <div className="breakdown-bar" style={{ width: `${percentage}%`, background: groupColor.border }} />
                </div>
                <span className="breakdown-pct">{percentage}%</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function SentencesPanel({ sentimentAnalysis }: { sentimentAnalysis: SentimentResult }) {
  return (
    <div className="panel sentiment-panel">
      <div className="sentiment-sentences">
        <h4 className="sentences-title">Per Sentence Scores</h4>
        <div className="sentences-list">
          {sentimentAnalysis.per_sentence.map((sentence, index) => {
            const colors = SENTIMENT_COLORS[sentence.label] || SENTIMENT_COLORS.neutral
            return (
              <div key={`${sentence.score}-${index}`} className="sentence-item" style={{ borderColor: colors.border }}>
                <span className="sentence-label" style={{ color: colors.text, background: colors.bg }}>
                  {sentence.label} {sentence.score.toFixed(2)}
                </span>
                <span className="sentence-text">{sentence.sentence}</span>
              </div>
            )
          })}
          {sentimentAnalysis.per_sentence.length === 0 && <div className="empty-state">No sentence sentiment data returned.</div>}
        </div>
      </div>
    </div>
  )
}

function SummaryPanel({ summarization }: { summarization: SummarizationResult }) {
  return (
    <div className="panel markdown-panel">
      <div className="markdown-toolbar">
        <span className="toolbar-label">Generated Summary</span>
        <span className="toolbar-badge">{summarization.word_count} words</span>
      </div>
      <pre className="markdown-content">{summarization.summary}</pre>
    </div>
  )
}

function AnalysisTabs({ results }: { results: DisplayResults }) {
  const tabs: { id: TabId; label: string }[] = [{ id: 'overview', label: 'Overview' }]

  if (results.topicModeling) {
    tabs.push({ id: 'topic', label: 'Topics' })
    tabs.push({ id: 'chunks', label: 'Chunks' })
  }

  if (results.sentimentAnalysis) {
    tabs.push({ id: 'sentiment', label: 'Sentiment' })
    tabs.push({ id: 'sentences', label: 'Sentences' })
  }

  if (results.summarization) {
    tabs.push({ id: 'summary', label: 'Summary' })
  }

  const [activeTab, setActiveTab] = useState<TabId>('overview')

  return (
    <div className="analysis-tabs">
      <div className="tabs-header">
        {tabs.map((tab) => (
          <button key={tab.id} className={`tab-button ${activeTab === tab.id ? 'active' : ''}`} onClick={() => setActiveTab(tab.id)}>
            {tab.label}
            {activeTab === tab.id && <span className="tab-indicator" />}
          </button>
        ))}
      </div>
      <div className="tabs-content">
        {activeTab === 'overview' && <OverviewPanel results={results} />}
        {activeTab === 'topic' && results.topicModeling && <TopicPanel topicModeling={results.topicModeling} />}
        {activeTab === 'chunks' && results.topicModeling && <ChunkPanel topicModeling={results.topicModeling} />}
        {activeTab === 'sentiment' && results.sentimentAnalysis && <SentimentPanel sentimentAnalysis={results.sentimentAnalysis} />}
        {activeTab === 'sentences' && results.sentimentAnalysis && <SentencesPanel sentimentAnalysis={results.sentimentAnalysis} />}
        {activeTab === 'summary' && results.summarization && <SummaryPanel summarization={results.summarization} />}
      </div>
    </div>
  )
}

function ResultsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const results = location.state?.results as DisplayResults | undefined

  useEffect(() => {
    if (!results) {
      navigate('/', { replace: true })
    }
  }, [navigate, results])

  if (!results) return null

  return (
    <div className="results-page">
      <div className="results-header">
        <div className="results-title-section">
          <h1 className="results-title">Analysis Results</h1>
          <p className="results-filename">{results.filename}</p>
        </div>
        <div className="results-meta">
          <span className="endpoint-badge">{ENDPOINTS[results.endpoint].label}</span>
        </div>
      </div>

      <div className="results-content">
        <AnalysisTabs results={results} />
      </div>
    </div>
  )
}

function HomePage() {
  return (
    <>
      <main className="main-content">
        <div className="hero-section">
          <h1 className="hero-title">
            <span className="title-line">Dynamic</span>
            <span className="title-line accent">Text Analyzer</span>
          </h1>
          <p className="hero-subtitle">
            Upload any PDF and run topic modeling, sentiment analysis, and summarization with your FastAPI NLP backend.
          </p>
        </div>

        <UploadPage />
      </main>

      <footer className="footer">
        <p>Powered by Docling, BERTopic, FinBERT, and Gemini or LM Studio</p>
      </footer>
    </>
  )
}

function App() {
  return (
    <div className="app">
      <div className="bg-pattern" />
      <Routes>
        <Route
          path="/"
          element={
            <>
              <Header />
              <HomePage />
            </>
          }
        />
        <Route
          path="/results"
          element={
            <>
              <Header showBack onBack={() => window.history.back()} />
              <ResultsPage />
            </>
          }
        />
      </Routes>
    </div>
  )
}

export default App
