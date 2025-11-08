import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Header } from './components/Header';
import { ChatInput } from './components/ChatInput';
import { Footer } from './components/Footer';
import { AnalysisResults } from './components/AnalysisResults';
import { AnalysisReport } from './services/api';

function HomePage() {
  const navigate = useNavigate();

  const handleAnalyzeComplete = (report: AnalysisReport) => {
    navigate('/results', { state: { report } });
  };

  return (
    <>
      <div className="bg-gradient-to-b from-gray-50 via-amber-50 to-orange-100 min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 flex items-center justify-center px-4 py-8">
          <ChatInput onAnalyzeComplete={handleAnalyzeComplete} />
        </main>
        <Footer />
      </div>
    </>
  );
}

function ResultsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const report = location.state?.report as AnalysisReport | undefined;

  const handleBack = () => {
    navigate('/');
  };

  return (
    <div className="bg-gray-50 min-h-screen flex flex-col">
      <main className="flex-1">
        <AnalysisResults onBack={handleBack} report={report} />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/results" element={<ResultsPage />} />
      </Routes>
    </Router>
  );
}
