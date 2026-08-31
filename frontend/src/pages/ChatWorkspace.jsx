import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Send, Plus, Bot, User, FileText, Pencil, Trash2, Check, X } from 'lucide-react';
import { conversationApi } from '../api';

const ChatWorkspace = () => {
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  // Edit state
  const [editingConvId, setEditingConvId] = useState(null);
  const [editTitleValue, setEditTitleValue] = useState('');
  
  const messagesEndRef = useRef(null);

  // Load conversations on mount
  useEffect(() => {
    fetchConversations();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Load messages when active conversation changes
  useEffect(() => {
    if (activeConvId) {
      fetchMessages(activeConvId);
    } else {
      setMessages([]);
    }
  }, [activeConvId]);

  const fetchConversations = async () => {
    try {
      const data = await conversationApi.list();
      // Sort by newest first
      const sorted = data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      setConversations(sorted);
      if (sorted.length > 0 && !activeConvId) {
        setActiveConvId(sorted[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch conversations:', err);
    }
  };

  const fetchMessages = async (id) => {
    try {
      const data = await conversationApi.getMessages(id);
      setMessages(data);
    } catch (err) {
      console.error('Failed to fetch messages:', err);
    }
  };

  const handleNewChat = async () => {
    try {
      const conv = await conversationApi.create('New Research Session');
      setConversations([conv, ...conversations]);
      setActiveConvId(conv.id);
      setMessages([]);
    } catch (err) {
      console.error('Failed to create conversation:', err);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this conversation?")) return;
    
    try {
      await conversationApi.delete(id);
      const newConvs = conversations.filter(c => c.id !== id);
      setConversations(newConvs);
      if (activeConvId === id) {
        if (newConvs.length > 0) {
          setActiveConvId(newConvs[0].id);
        } else {
          setActiveConvId(null);
          setMessages([]);
        }
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  };

  const startEditing = (conv, e) => {
    e.stopPropagation();
    setEditingConvId(conv.id);
    setEditTitleValue(conv.title || 'Untitled Session');
  };

  const cancelEditing = (e) => {
    e?.stopPropagation();
    setEditingConvId(null);
    setEditTitleValue('');
  };

  const saveEdit = async (id, e) => {
    e?.stopPropagation();
    if (!editTitleValue.trim()) return cancelEditing();
    
    try {
      // Optimistic update
      setConversations(conversations.map(c => 
        c.id === id ? { ...c, title: editTitleValue.trim() } : c
      ));
      setEditingConvId(null);
      
      await conversationApi.updateTitle(id, editTitleValue.trim());
    } catch (err) {
      console.error("Failed to update title:", err);
      fetchConversations(); // Revert on failure
    }
  };

  const handleEditKeyDown = (id, e) => {
    if (e.key === 'Enter') saveEdit(id, e);
    if (e.key === 'Escape') cancelEditing(e);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || !activeConvId || isTyping) return;

    const query = input.trim();
    setInput('');
    
    // Optimistic UI update
    const userMsg = { id: Date.now(), role: 'user', content: query };
    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const res = await conversationApi.chat(activeConvId, query);
      
      const assistantMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: res.answer,
        citations: res.citations
      };
      
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Failed to send message:', err);
      // Optional: Add an error message to chat
      setMessages((prev) => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: '**Error:** Failed to get response from the assistant. Is the backend running?'
      }]);
    } finally {
      setIsTyping(false);
      // Refresh conversation list to get updated titles if backend auto-generates them
      fetchConversations();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  return (
    <div className="page-container" style={{ padding: '1rem', maxWidth: '100%', height: '100%' }}>
      <div className="chat-workspace">
        
        {/* Sidebar for Conversations */}
        <div className="glass-panel conv-sidebar">
          <button className="new-chat-btn" onClick={handleNewChat}>
            <Plus size={18} /> New Chat
          </button>
          
          <div style={{ flex: 1, overflowY: 'auto' }}>
            {conversations.map((conv) => (
              <div 
                key={conv.id} 
                className={`conv-item ${activeConvId === conv.id ? 'active' : ''}`}
                onClick={() => {
                  if (editingConvId !== conv.id) setActiveConvId(conv.id);
                }}
                title={conv.title || 'Untitled Session'}
              >
                {editingConvId === conv.id ? (
                  <div style={{ display: 'flex', width: '100%', gap: '0.25rem' }}>
                    <input 
                      autoFocus
                      className="conv-title-input"
                      value={editTitleValue}
                      onChange={(e) => setEditTitleValue(e.target.value)}
                      onKeyDown={(e) => handleEditKeyDown(conv.id, e)}
                      onClick={(e) => e.stopPropagation()}
                    />
                    <button className="conv-action-btn" onClick={(e) => saveEdit(conv.id, e)}>
                      <Check size={14} />
                    </button>
                    <button className="conv-action-btn" onClick={cancelEditing}>
                      <X size={14} />
                    </button>
                  </div>
                ) : (
                  <>
                    <div className="conv-item-title">
                      {conv.title || 'Untitled Session'}
                    </div>
                    <div className="conv-actions">
                      <button 
                        className="conv-action-btn" 
                        onClick={(e) => startEditing(conv, e)}
                        title="Edit Title"
                      >
                        <Pencil size={14} />
                      </button>
                      <button 
                        className="conv-action-btn delete" 
                        onClick={(e) => handleDelete(conv.id, e)}
                        title="Delete Chat"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Chat Thread */}
        <div className="glass-panel chat-thread-container">
          
          <div className="messages-area">
            {messages.length === 0 && !isTyping && (
              <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--text-secondary)' }}>
                <Bot size={48} style={{ opacity: 0.5, marginBottom: '1rem' }} />
                <h3>Research Assistant Ready</h3>
                <p>Ask a question based on your indexed corpus.</p>
              </div>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                </div>
                
                <div className="message-bubble">
                  <div className="message-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                  
                  {/* Citations block */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="citations-list">
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <FileText size={14} /> Sources
                      </div>
                      {msg.citations.map((cite, idx) => (
                        <div key={idx} className="citation-card">
                          <a href={cite.pdf_url} target="_blank" rel="noopener noreferrer">
                            [{idx + 1}] {cite.title}
                          </a>
                          <span>{cite.authors?.join(', ')} • {new Date(cite.published).getFullYear()}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="message assistant">
                <div className="message-avatar">
                  <Bot size={20} />
                </div>
                <div className="message-bubble typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
            <form className="input-container" onSubmit={handleSend}>
              <textarea 
                className="chat-input"
                placeholder="Ask about fine-tuning, transformers, etc..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
              />
              <button 
                type="submit" 
                className="send-btn"
                disabled={!input.trim() || !activeConvId || isTyping}
              >
                <Send size={20} />
              </button>
            </form>
          </div>

        </div>
      </div>
    </div>
  );
};

export default ChatWorkspace;
