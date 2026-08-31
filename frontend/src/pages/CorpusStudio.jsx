import React, { useState, useEffect } from 'react';
import { Database, FileText, Layers, Play, RefreshCw, ExternalLink, Send } from 'lucide-react';
import { corpusApi, paperRequestApi } from '../api';

const CorpusStudio = () => {
  const [collectionInfo, setCollectionInfo] = useState(null);
  const [papers, setPapers] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Fallback State
  const [isLocalApiAvailable, setIsLocalApiAvailable] = useState(true);
  const [paperRequests, setPaperRequests] = useState([]);
  const [requestQuery, setRequestQuery] = useState('');
  const [isRequesting, setIsRequesting] = useState(false);

  // Form State
  const [queries, setQueries] = useState('');
  const [topK, setTopK] = useState(5);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchData();
    // Poll for jobs every 5 seconds
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      await fetchCollectionInfo();
      // If collection info succeeds, the local API is up.
      setIsLocalApiAvailable(true);
      await Promise.all([
        fetchPapers(),
        fetchJobs()
      ]);
    } catch (err) {
      // Local API is down
      setIsLocalApiAvailable(false);
      await fetchPaperRequests();
    } finally {
      setLoading(false);
    }
  };

  const fetchPaperRequests = async () => {
    try {
      const data = await paperRequestApi.list();
      setPaperRequests(data);
    } catch (err) {
      console.error('Failed to fetch paper requests', err);
    }
  };

  const fetchCollectionInfo = async () => {
    const data = await corpusApi.getCollectionInfo(); // Let error propagate to fetchData
    setCollectionInfo(data);
  };

  const fetchPapers = async () => {
    try {
      const data = await corpusApi.getPapers(50, 0);
      setPapers(data.papers || []);
    } catch (err) {
      console.error('Failed to fetch papers', err);
    }
  };

  const fetchJobs = async () => {
    try {
      const data = await corpusApi.getJobs();
      setJobs(data.sort((a, b) => new Date(b.started_at || 0) - new Date(a.started_at || 0)));
    } catch (err) {
      console.error('Failed to fetch jobs', err);
    }
  };

  const handleIngest = async (e) => {
    e.preventDefault();
    if (!queries.trim()) return;

    setIsSubmitting(true);
    try {
      const queryList = queries.split(',').map(q => q.trim()).filter(Boolean);
      await corpusApi.startIngestion(queryList, parseInt(topK, 10));
      setQueries('');
      // Immediately fetch jobs to show the pending one
      fetchJobs();
    } catch (err) {
      console.error('Failed to start ingestion', err);
      alert('Failed to start ingestion. Ensure Corpus Builder API is running on port 8001.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRequestSubmit = async (e) => {
    e.preventDefault();
    if (!requestQuery.trim()) return;

    setIsRequesting(true);
    try {
      await paperRequestApi.create(requestQuery.trim());
      setRequestQuery('');
      await fetchPaperRequests();
    } catch (err) {
      console.error('Failed to submit paper request', err);
      alert('Failed to submit request. Is the backend running?');
    } finally {
      setIsRequesting(false);
    }
  };

  if (!isLocalApiAvailable && !loading) {
    return (
      <div className="page-container" style={{ maxWidth: '800px', height: '100%' }}>
        <div className="page-header">
          <h1 className="page-title">Request Papers</h1>
          <p className="page-subtitle">The Corpus Builder API is unavailable. Submit a request for papers to be indexed by an administrator.</p>
        </div>

        <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
          <form className="ingest-form" style={{ padding: 0 }} onSubmit={handleRequestSubmit}>
            <div className="form-group">
              <label>What topic or papers do you need?</label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="e.g. latest research on LLM alignment" 
                value={requestQuery}
                onChange={(e) => setRequestQuery(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn-primary" disabled={isRequesting || !requestQuery.trim()} style={{ width: 'fit-content' }}>
              {isRequesting ? <RefreshCw className="animate-spin" size={18} /> : <Send size={18} />}
              Submit Request
            </button>
          </form>
        </div>

        <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)', fontSize: '1rem' }}>Recent Requests</h3>
        <div className="jobs-list" style={{ padding: 0 }}>
          {paperRequests.length === 0 && <p style={{ color: 'var(--text-secondary)' }}>No requests yet.</p>}
          {paperRequests.map((req) => (
            <div key={req.id} className="job-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: '500', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>{req.query}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  {new Date(req.created_at).toLocaleString()}
                </div>
              </div>
              <span className={`badge ${req.status === 'pending' ? 'PENDING' : 'COMPLETED'}`}>
                {req.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="page-container" style={{ maxWidth: '100%', height: '100%' }}>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title">Corpus Studio</h1>
          <p className="page-subtitle">Manage your research corpus and background ingestion jobs.</p>
        </div>
        <button className="btn-primary" onClick={fetchData} style={{ background: 'var(--bg-surface)' }}>
          <RefreshCw size={18} /> Refresh
        </button>
      </div>

      <div className="corpus-grid">
        
        {/* Left Column: Stats & Ingestion Form */}
        <div className="corpus-column">
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div className="glass-panel stat-card">
              <div className="stat-header">
                <Database size={16} /> Qdrant Vectors
              </div>
              <div className="stat-value">
                {collectionInfo?.vectors_count?.toLocaleString() || '0'}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                {collectionInfo?.exists ? `Status: ${collectionInfo.status}` : 'Collection not created'}
              </div>
            </div>

            <div className="glass-panel stat-card">
              <div className="stat-header">
                <FileText size={16} /> Indexed Papers
              </div>
              <div className="stat-value">
                {papers.length}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                Recorded in PostgreSQL
              </div>
            </div>
          </div>

          <div className="glass-panel">
            <div className="stat-card" style={{ borderBottom: '1px solid var(--border-light)', paddingBottom: '1rem' }}>
              <div className="stat-header"><Layers size={16}/> Start Ingestion</div>
            </div>
            <form className="ingest-form" onSubmit={handleIngest}>
              <div className="form-group">
                <label>Search Queries (comma separated)</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="e.g. transformer attention, diffusion models" 
                  value={queries}
                  onChange={(e) => setQueries(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label>Top K Papers (per query)</label>
                <input 
                  type="number" 
                  className="form-input" 
                  min="1" 
                  max="20"
                  value={topK}
                  onChange={(e) => setTopK(e.target.value)}
                  required
                />
              </div>
              <button type="submit" className="btn-primary" disabled={isSubmitting || !queries.trim()}>
                {isSubmitting ? <RefreshCw className="animate-spin" size={18} /> : <Play size={18} />}
                Start Indexing Job
              </button>
            </form>
          </div>

          <div className="glass-panel">
             <div className="stat-card" style={{ borderBottom: '1px solid var(--border-light)', paddingBottom: '1rem' }}>
              <div className="stat-header"><RefreshCw size={16}/> Recent Jobs</div>
            </div>
            <div className="jobs-list">
              {jobs.length === 0 && <p style={{ color: 'var(--text-secondary)' }}>No jobs found.</p>}
              {jobs.map((job) => (
                <div key={job.job_id} className="job-card">
                  <div className="job-header">
                    <span className="job-id">{job.job_id.substring(0, 8)}...</span>
                    <span className={`badge ${job.status}`}>{job.status}</span>
                  </div>
                  <div className="job-stats">
                    <span>Papers: {job.total_papers_processed || 0}</span>
                    <span>Chunks: {job.total_chunks_indexed || 0}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Column: Papers Table */}
        <div className="glass-panel papers-table-container">
           <div className="stat-card" style={{ padding: '0 0 1rem 0' }}>
              <div className="stat-header"><FileText size={16}/> Ingested Papers Directory</div>
            </div>
            <div className="table-wrapper">
              {loading && papers.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>Loading papers...</div>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>Title</th>
                      <th>Paper ID</th>
                      <th>Date Indexed</th>
                      <th>Link</th>
                    </tr>
                  </thead>
                  <tbody>
                    {papers.map((paper) => (
                      <tr key={paper.paper_id}>
                        <td className="title-cell">{paper.title}</td>
                        <td style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{paper.paper_id}</td>
                        <td className="date-cell">{new Date(paper.ingested_at).toLocaleDateString()}</td>
                        <td>
                          <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                            PDF <ExternalLink size={14} />
                          </a>
                        </td>
                      </tr>
                    ))}
                    {papers.length === 0 && (
                      <tr>
                        <td colSpan="4" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
                          No papers indexed yet. Start a job to populate the corpus.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              )}
            </div>
        </div>

      </div>
    </div>
  );
};

export default CorpusStudio;
