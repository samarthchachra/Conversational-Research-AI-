import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import ChatWorkspace from './pages/ChatWorkspace'
import CorpusStudio from './pages/CorpusStudio'
import './App.css'
import './index.css'

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Sidebar />
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
