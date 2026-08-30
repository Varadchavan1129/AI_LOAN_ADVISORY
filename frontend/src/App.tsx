import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ChatInterface } from './components/ChatInterface';
import { AdminLogin } from './components/AdminLogin';
import { Dashboard } from './components/Dashboard';
import { DocumentManager } from './components/DocumentManager';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<ChatInterface />} />
        <Route path="/admin" element={<AdminLogin />} />
        <Route path="/admin/dashboard" element={<Dashboard />} />
        <Route path="/admin/documents" element={<DocumentManager />} />
      </Routes>
    </Router>
  );
}

export default App;
