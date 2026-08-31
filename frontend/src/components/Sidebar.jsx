import React from 'react';
import { NavLink } from 'react-router-dom';
import { MessageSquare, Database, BrainCircuit, User, LogOut } from 'lucide-react';

const Sidebar = ({ userId, onLogout }) => {
  return (
    <div className="sidebar" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div>
        <div className="sidebar-header">
          <BrainCircuit size={28} className="text-accent" />
          <span>Research AI</span>
        </div>
        
        <div className="nav-links">
          <NavLink 
            to="/" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <MessageSquare size={20} />
            <span>Chat Workspace</span>
          </NavLink>
          
          <NavLink 
            to="/corpus" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Database size={20} />
            <span>Corpus Studio</span>
          </NavLink>
        </div>
      </div>

      <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-light)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
          <div style={{ background: 'var(--bg-surface)', padding: '0.5rem', borderRadius: '50%' }}>
            <User size={16} />
          </div>
          <span style={{ fontSize: '0.9rem', fontWeight: '500' }}>@{userId}</span>
        </div>
        <button onClick={onLogout} style={{ color: 'var(--text-secondary)', padding: '0.5rem', borderRadius: '8px' }} title="Switch User">
          <LogOut size={16} />
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
