import React from 'react';
import { NavLink } from 'react-router-dom';
import { MessageSquare, Database, BrainCircuit } from 'lucide-react';

const Sidebar = () => {
  return (
    <div className="sidebar">
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
  );
};

export default Sidebar;
