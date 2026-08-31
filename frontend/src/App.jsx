import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { LogIn } from 'lucide-react'
import Sidebar from './components/Sidebar'
import ChatWorkspace from './pages/ChatWorkspace'
import CorpusStudio from './pages/CorpusStudio'
import './App.css'
import './index.css'

function App() {
  const [userId, setUserId] = useState(localStorage.getItem('userId') || '');
  const [inputName, setInputName] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    if (!inputName.trim()) return;
    const formattedId = inputName.trim().toLowerCase().replace(/\s+/g, '-');
    localStorage.setItem('userId', formattedId);
    setUserId(formattedId);
  };

  const handleLogout = () => {
    localStorage.removeItem('userId');
    setUserId('');
  };

  if (!userId) {
    return (
      <div className="app-container" style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div className="glass-panel" style={{ padding: '2.5rem', width: '100%', maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '1.5rem', textAlign: 'center' }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem' }}>
            <div style={{ background: 'var(--accent-primary)', width: '64px', height: '64px', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
              <LogIn size={32} />
            </div>
          </div>
          <div>
            <h1 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Welcome to Research AI</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Please enter a username to access your workspace.</p>
          </div>
          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <input
              type="text"
              autoFocus
              className="form-input"
              placeholder="e.g. samarth"
              value={inputName}
              onChange={(e) => setInputName(e.target.value)}
              required
            />
            <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
              Enter Workspace
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className="app-container">
        <Sidebar userId={userId} onLogout={handleLogout} />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<ChatWorkspace />} />
            <Route path="/corpus" element={<CorpusStudio />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
