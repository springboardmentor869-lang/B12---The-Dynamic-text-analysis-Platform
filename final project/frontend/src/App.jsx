import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import UploadPage from "./components/uploadpage";
import ResultsDashboard from "./components/resultsdashboard";

const pageVariants = {
  initial: { opacity: 0, y: 20, scale: 0.98 },
  animate: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.45, ease: [0.4, 0, 0.2, 1] } },
  exit: { opacity: 0, y: -16, scale: 0.98, transition: { duration: 0.3, ease: [0.4, 0, 0.2, 1] } },
};

function App() {
  const [analysisData, setAnalysisData] = useState(null);

  const hasValidAnalysis =
    analysisData &&
    typeof analysisData === "object" &&
    analysisData.filename;

  return (
    <AnimatePresence mode="wait">
      {hasValidAnalysis ? (
        <motion.div
          key="results"
          variants={pageVariants}
          initial="initial"
          animate="animate"
          exit="exit"
        >
          <ResultsDashboard
            analysis={analysisData}
            onReset={() => setAnalysisData(null)}
          />
        </motion.div>
      ) : (
        <motion.div
          key="upload"
          variants={pageVariants}
          initial="initial"
          animate="animate"
          exit="exit"
        >
          <UploadPage setAnalysisData={setAnalysisData} />
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default App;