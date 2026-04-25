import { useEffect, useState } from "react";
import UploadPage from "./components/UploadPage";
import ResultsDashboard from "./components/ResultsDashboard";

function App() {
  const [analysisData, setAnalysisData] = useState(null);
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }, [analysisData]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  const hasValidAnalysis =
    analysisData &&
    typeof analysisData === "object" &&
    analysisData.filename;

  return (
    <div>
      <div style={{ position: 'fixed', top: 20, right: 20, zIndex: 100 }}>
        <button 
          onClick={toggleTheme}
          style={{
            background: 'var(--bg-card)',
            color: 'var(--text-main)',
            border: '1px solid var(--border-color)',
            padding: '8px 12px',
            borderRadius: '999px',
            boxShadow: 'var(--shadow-sm)',
            cursor: 'pointer',
            fontWeight: 600,
            fontSize: '13px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'all 0.2s ease'
          }}
        >
          {theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode'}
        </button>
      </div>

      {hasValidAnalysis ? (
        <ResultsDashboard
          analysis={analysisData}
          onReset={() => setAnalysisData(null)}
        />
      ) : (
        <UploadPage setAnalysisData={setAnalysisData} />
      )}
    </div>
  );
}

export default App;