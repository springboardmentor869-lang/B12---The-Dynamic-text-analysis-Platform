import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter } from 'recharts';
import type { TopicModelResponse, SentimentResponse } from './types';

// Word Cloud Component
export const WordCloud = ({ keywords, scores }: { keywords: string[]; scores: number[] }) => {
  // Filter out empty keywords and mismatched length
  const validKeywords = keywords.filter(k => k && k.trim().length > 0);
  const validScores = scores.slice(0, validKeywords.length);

  if (!validKeywords || validKeywords.length === 0) {
    return (
      <div className="word-cloud-container">
        <div className="word-cloud empty-state">
          <p className="no-data-text">No keywords extracted</p>
        </div>
      </div>
    );
  }

  const maxScore = Math.max(...validScores);
  const minScore = Math.min(...validScores);
  const range = maxScore - minScore || 1;

  // Group keywords with their scores
  const wordData = validKeywords.map((keyword, i) => ({
    word: keyword,
    score: validScores[i] || 0
  })).sort((a, b) => b.score - a.score).slice(0, 50); // Top 50 words

  return (
    <div className="word-cloud-container">
      <div className="word-cloud">
        {wordData.map((item, idx) => {
          const normalized = (item.score - minScore) / (range || 1);
          const bucket = Math.min(10, Math.max(0, Math.round(normalized * 10)));

          return (
            <span
              key={idx}
              className={`word-cloud-item weight-${bucket}`}
              title={`Relevance: ${(item.score * 100).toFixed(1)}%`}
            >
              {item.word}
            </span>
          );
        })}
      </div>
    </div>
  );
};

// Sentiment Distribution Pie Chart
export const SentimentDistributionChart = ({ sentimentData }: { sentimentData: SentimentResponse }) => {
  const sentimentCounts: { [key: string]: number } = {};
  
  sentimentData.per_sentence.forEach(s => {
    const label = s.label.toLowerCase();
    sentimentCounts[label] = (sentimentCounts[label] || 0) + 1;
  });

  const chartData = Object.entries(sentimentCounts).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
    percentage: ((value / sentimentData.per_sentence.length) * 100).toFixed(1)
  }));

  const COLORS = {
    'Positive': '#10b981',
    'Negative': '#ef4444',
    'Neutral': '#6b7280'
  };

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percentage }) => `${name}: ${percentage}%`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                className={`pie-cell pie-${entry.name.toLowerCase()}`}
              />
            ))}
          </Pie>
          <Tooltip formatter={(value) => `${value} sentences`} />
        </PieChart>
      </ResponsiveContainer>
      <div className="chart-legend">
        {chartData.map((item, idx) => (
          <div key={idx} className="legend-item">
            <div 
              className="legend-color" 
              style={{ backgroundColor: COLORS[item.name as keyof typeof COLORS] }}
            />
            <span>{item.name}: {item.value} ({item.percentage}%)</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Topic Distribution Bar Chart
export const TopicDistributionChart = ({ topicData }: { topicData: TopicModelResponse }) => {
  const chartData = topicData.all_topics_found
    .map(t => ({
      name: t.label.substring(0, 20),
      score: Math.round(t.avg_score * 100),
      matches: t.chunks_matched,
      fullLabel: t.label
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 10);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="label">{payload[0].payload.fullLabel}</p>
          <p>Confidence: {payload[0].value}%</p>
          <p>Matched: {payload[0].payload.matches} chunks</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis 
            dataKey="name" 
            angle={-45} 
            textAnchor="end" 
            height={120}
            stroke="rgba(255,255,255,0.5)"
          />
          <YAxis stroke="rgba(255,255,255,0.5)" />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="score" fill="#6366f1" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

// Sentiment Trend Chart (Per-sentence visualization)
export const SentimentTrendChart = ({ sentimentData }: { sentimentData: SentimentResponse }) => {
  if (!sentimentData.per_sentence || sentimentData.per_sentence.length === 0) {
    return (
      <div className="chart-container">
        <div className="no-data-box">
          <p>No sentiment data available</p>
        </div>
      </div>
    );
  }

  const chartData = sentimentData.per_sentence.slice(0, 25).map((s, idx) => ({
    sentence: idx + 1,
    score: Math.round(s.score * 100),
    label: s.label.toUpperCase(),
    text: s.sentence.substring(0, 50)
  }));

  const sentimentColors = {
    'POSITIVE': '#10b981',
    'NEGATIVE': '#ef4444',
    'NEUTRAL': '#6b7280'
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <p className="label">Sentence {data.sentence}</p>
          <p>Sentiment: <span className={`sentiment-label sentiment-${data.label.toLowerCase()}`}>{data.label}</span></p>
          <p>Confidence: {data.score}%</p>
          <p className="text sentiment-text">"{data.text}..."</p>
        </div>
      );
    }
    return null;
  };

  // Group data by sentiment for better rendering
  const positiveData = chartData.filter(d => d.label === 'POSITIVE');
  const negativeData = chartData.filter(d => d.label === 'NEGATIVE');
  const neutralData = chartData.filter(d => d.label === 'NEUTRAL');

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={350}>
        <ScatterChart 
          data={chartData}
          margin={{ top: 20, right: 30, bottom: 60, left: 60 }}
          className="sentiment-scatter"
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis 
            type="number"
            dataKey="sentence" 
            name="Sentence Index"
            stroke="rgba(255,255,255,0.5)"
            label={{ value: 'Sentence Number', position: 'bottom', offset: 10 }}
            domain={[0, Math.max(...chartData.map(d => d.sentence)) + 1]}
          />
          <YAxis 
            type="number"
            dataKey="score" 
            name="Confidence"
            stroke="rgba(255,255,255,0.5)"
            domain={[0, 100]}
            label={{ value: 'Confidence %', angle: -90, position: 'insideLeft', offset: -10 }}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
          {positiveData.length > 0 && (
            <Scatter name="Positive" data={positiveData} fill={sentimentColors['POSITIVE']} />
          )}
          {negativeData.length > 0 && (
            <Scatter name="Negative" data={negativeData} fill={sentimentColors['NEGATIVE']} />
          )}
          {neutralData.length > 0 && (
            <Scatter name="Neutral" data={neutralData} fill={sentimentColors['NEUTRAL']} />
          )}
        </ScatterChart>
      </ResponsiveContainer>
      <div className="chart-legend chart-legend-margin-top">
        {positiveData.length > 0 && (
          <div className="legend-item">
            <div className="legend-color legend-color-positive" />
            <span>Positive ({positiveData.length})</span>
          </div>
        )}
        {negativeData.length > 0 && (
          <div className="legend-item">
            <div className="legend-color legend-color-negative" />
            <span>Negative ({negativeData.length})</span>
          </div>
        )}
        {neutralData.length > 0 && (
          <div className="legend-item">
            <div className="legend-color legend-color-neutral" />
            <span>Neutral ({neutralData.length})</span>
          </div>
        )}
      </div>
    </div>
  );
};

// Keyword Frequency Chart
export const KeywordFrequencyChart = ({ keywords }: { keywords: string[] }) => {
  const keywordCounts: { [key: string]: number } = {};
  
  keywords.forEach(k => {
    keywordCounts[k] = (keywordCounts[k] || 0) + 1;
  });

  const chartData = Object.entries(keywordCounts)
    .map(([keyword, count]) => ({
      keyword: keyword.length > 15 ? keyword.substring(0, 12) + '...' : keyword,
      count,
      fullKeyword: keyword
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 12);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="label">{payload[0].payload.fullKeyword}</p>
          <p>Frequency: {payload[0].value}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 200, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis type="number" stroke="rgba(255,255,255,0.5)" />
          <YAxis dataKey="keyword" type="category" stroke="rgba(255,255,255,0.5)" width={190} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="count" fill="#8884d8" radius={[0, 8, 8, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
