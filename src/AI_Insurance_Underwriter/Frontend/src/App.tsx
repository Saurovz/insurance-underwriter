// src/App.tsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Layout';
import { FloatingChatbot } from './components/Chatbot';
import { HomePage } from './pages/HomePage';
import { Application } from './pages/Application';
import { Detail } from './pages/Detail';
import { Configuration } from './pages/Configuration';
import { Toaster } from 'react-hot-toast';

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <Navbar />
        <Toaster position="top-right" />
        
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/application" element={<Application />} />
          <Route path="/detail" element={<Detail />} />
          <Route path="/configuration" element={<Configuration />} />
        </Routes>

        <FloatingChatbot />
      </div>
    </Router>
  );
}

export default App;
