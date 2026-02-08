import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, FileText, Sparkles, Settings, Check, AlertCircle, Trash2, RefreshCw, Edit3, Eye, EyeOff } from 'lucide-react'
import PipelineVisualizer from './components/PipelineVisualizer'
import MatchDashboard from './components/MatchDashboard'
import LiveResumeEditor from './components/LiveResumeEditor'
import './App.css'

const API_BASE_URL = ''

function App() {
  // State
  const [jobDescription, setJobDescription] = useState('')
  const [jdSkills, setJdSkills] = useState([])
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [backendConnected, setBackendConnected] = useState(false)
  const [healthData, setHealthData] = useState(null)

  // Pipeline state
  const [currentStep, setCurrentStep] = useState(0)
  const [pipelineExpanded, setPipelineExpanded] = useState(false)

  // UI state
  const [showHowItWorks, setShowHowItWorks] = useState(false)
  const [expandedFileIndex, setExpandedFileIndex] = useState(null) // For extracted text preview

  // Check backend connection
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/health`)
        if (response.ok) {
          const data = await response.json()
          setBackendConnected(true)
          setHealthData(data)
        }
      } catch {
        setBackendConnected(false)
        setTimeout(checkConnection, 3000)
      }
    }
    checkConnection()
  }, [])

  // Extract skills from JD (debounced)
  const extractJDSkills = useCallback(async () => {
    if (!jobDescription.trim() || !backendConnected) {
      setJdSkills([])
      return
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/extract-skills`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: jobDescription })
      })
      const data = await response.json()
      setJdSkills(data.skills || [])
    } catch (e) {
      console.log('Skill extraction failed:', e)
    }
  }, [jobDescription, backendConnected])

  useEffect(() => {
    const timer = setTimeout(extractJDSkills, 600)
    return () => clearTimeout(timer)
  }, [extractJDSkills])

  // Handle file upload
  const handleFileUpload = async (files) => {
    const newFiles = []
    for (const file of files) {
      const formData = new FormData()
      formData.append('file', file)

      try {
        const response = await fetch(`${API_BASE_URL}/api/upload-file`, {
          method: 'POST',
          body: formData
        })
        const data = await response.json()

        // Check if we got valid extracted text (not binary data)
        let content = data.text || ''
        let extractionSuccess = data.success && content.length > 0 && !content.includes('%PDF')

        if (!extractionSuccess) {
          // Try text extraction endpoint
          const textResponse = await fetch(`${API_BASE_URL}/api/extract-text`, {
            method: 'POST',
            body: formData
          })
          if (textResponse.ok) {
            const textData = await textResponse.json()
            content = textData.text || ''
            extractionSuccess = content.length > 0 && !content.includes('%PDF')
          }
        }

        if (extractionSuccess) {
          newFiles.push({
            name: file.name.replace(/\.[^/.]+$/, ''),
            content: content,
            skills: data.skills || [],
            charCount: content.length
          })
        } else {
          // Fallback for text files
          if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
            const text = await file.text()
            newFiles.push({
              name: file.name.replace(/\.[^/.]+$/, ''),
              content: text,
              skills: [],
              charCount: text.length
            })
          } else {
            newFiles.push({
              name: file.name.replace(/\.[^/.]+$/, ''),
              content: `[PDF extraction failed - please try a .txt file]`,
              skills: [],
              charCount: 0,
              error: true
            })
          }
        }
      } catch (e) {
        console.log('Upload failed:', e)
        try {
          const text = await file.text()
          if (text && !text.includes('%PDF')) {
            newFiles.push({
              name: file.name.replace(/\.[^/.]+$/, ''),
              content: text,
              skills: [],
              charCount: text.length
            })
          }
        } catch { }
      }
    }
    setUploadedFiles(prev => [...prev, ...newFiles])
  }

  // Handle JD file upload
  const handleJDUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_BASE_URL}/api/upload-file`, {
        method: 'POST',
        body: formData
      })
      const data = await response.json()
      if (data.success && data.text && !data.text.includes('%PDF')) {
        setJobDescription(data.text)
        setJdSkills(data.skills || [])
      } else {
        // Try reading as text directly
        const text = await file.text()
        if (!text.includes('%PDF')) {
          setJobDescription(text)
        }
      }
    } catch (e) {
      try {
        const text = await file.text()
        setJobDescription(text)
      } catch { }
    }
  }

  // Run matching
  const runMatching = async () => {
    if (!jobDescription.trim() || uploadedFiles.length === 0) {
      alert('Please provide a job description and at least one resume')
      return
    }

    setLoading(true)
    setResults(null)
    setCurrentStep(0)
    setPipelineExpanded(true)

    // Simulate pipeline steps
    const stepDelay = async (step, delay) => {
      setCurrentStep(step)
      await new Promise(r => setTimeout(r, delay))
    }

    await stepDelay(1, 400)  // Parsing
    await stepDelay(2, 500)  // BERT
    await stepDelay(3, 300)  // Similarity
    await stepDelay(4, 400)  // Skills

    try {
      const response = await fetch(`${API_BASE_URL}/api/manual-match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_description: jobDescription,
          job_skills: jdSkills,
          resumes: uploadedFiles.map(file => ({
            name: file.name,
            content: file.content,
            skills: file.skills || []
          }))
        })
      })

      await stepDelay(5, 200)  // Ranking

      const data = await response.json()
      setResults(data)
      setJdSkills(data.job_skills_detected || jdSkills)

    } catch (error) {
      console.error('Matching failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <Sparkles className="logo-icon" />
            <div>
              <h1>Resume Matcher</h1>
              <span className="tagline">AI-Powered Candidate Matching</span>
            </div>
          </div>
          <div className="header-actions">
            <button
              className={`btn-secondary ${showHowItWorks ? 'active' : ''}`}
              onClick={() => setShowHowItWorks(!showHowItWorks)}
            >
              <Settings size={18} />
              How It Works
            </button>
            <div className={`status-badge ${backendConnected ? 'connected' : 'disconnected'}`}>
              {backendConnected ? <Check size={14} /> : <AlertCircle size={14} />}
              {backendConnected ? 'Connected' : 'Connecting...'}
            </div>
          </div>
        </div>
      </header>

      {/* How It Works Panel */}
      <AnimatePresence>
        {showHowItWorks && (
          <motion.section
            className="how-it-works"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
          >
            <div className="info-container">
              <div className="info-card">
                <div className="info-icon">🧠</div>
                <h3>BERT Embeddings</h3>
                <p>Converts text into 384-dimensional vectors that capture semantic meaning. "React developer" matches "Frontend engineer" even with different words.</p>
              </div>
              <div className="info-card">
                <div className="info-icon">🔍</div>
                <h3>Skill Extraction</h3>
                <p>Identifies 200+ technical skills using pattern matching and synonyms. "js" → "javascript", "k8s" → "kubernetes".</p>
              </div>
              <div className="info-card">
                <div className="info-icon">📊</div>
                <h3>Hybrid Scoring</h3>
                <p>Final Score = (BERT × 40%) + (Skills × 60%). Balances semantic understanding with concrete skill matching.</p>
              </div>
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="main">
        {/* Step 1: Input */}
        <section className="section">
          <div className="section-header">
            <span className="step-number">1</span>
            <h2>Input Data</h2>
          </div>

          <div className="input-grid">
            {/* Job Description Card */}
            <div className="card">
              <div className="card-header">
                <h3><FileText size={18} /> Job Description</h3>
                <div className="card-actions">
                  <input type="file" id="jd-upload" accept=".pdf,.txt" onChange={handleJDUpload} hidden />
                  <label htmlFor="jd-upload" className="btn-icon" title="Upload file">
                    <Upload size={16} />
                  </label>
                  <button className="btn-icon" onClick={() => setJobDescription('')} title="Clear">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              <textarea
                className="textarea"
                placeholder="Paste job description here...

Example:
We're looking for a Senior Software Engineer with 5+ years of experience in React, Node.js, and AWS. Strong problem-solving skills required."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
              />
              {jdSkills.length > 0 && (
                <motion.div
                  className="skills-preview"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <span className="skills-label">{jdSkills.length} skills detected:</span>
                  <div className="skill-pills">
                    {jdSkills.map((skill, i) => (
                      <span key={i} className="skill-pill">{skill}</span>
                    ))}
                  </div>
                </motion.div>
              )}
            </div>

            {/* Resume Upload Card */}
            <div className="card">
              <div className="card-header">
                <h3><FileText size={18} /> Resumes</h3>
                <button
                  className="btn-danger-sm"
                  onClick={() => setUploadedFiles([])}
                  disabled={uploadedFiles.length === 0}
                >
                  Clear All
                </button>
              </div>
              <div
                className="dropzone"
                onDrop={(e) => { e.preventDefault(); handleFileUpload(Array.from(e.dataTransfer.files)) }}
                onDragOver={(e) => e.preventDefault()}
                onClick={() => document.getElementById('resume-upload').click()}
              >
                <input
                  type="file"
                  id="resume-upload"
                  multiple
                  accept=".pdf,.txt"
                  onChange={(e) => handleFileUpload(Array.from(e.target.files))}
                  hidden
                />
                <Upload className="drop-icon" />
                <p className="drop-text">Drop resumes here</p>
                <span className="drop-hint">or click to browse • PDF, TXT</span>
              </div>

              {uploadedFiles.length > 0 && (
                <div className="file-list">
                  {uploadedFiles.map((file, i) => (
                    <motion.div
                      key={i}
                      className={`file-item-wrapper`}
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <div className={`file-item ${file.error ? 'error' : ''}`}>
                        <FileText size={16} className="file-icon" />
                        <span className="file-name">{file.name}</span>
                        <span className="file-chars">{file.charCount} chars</span>
                        <button
                          className="file-preview-btn"
                          onClick={(e) => {
                            e.stopPropagation()
                            setExpandedFileIndex(expandedFileIndex === i ? null : i)
                          }}
                          title="View extracted text"
                        >
                          {expandedFileIndex === i ? <EyeOff size={14} /> : <Eye size={14} />}
                        </button>
                        <button
                          className="file-remove"
                          onClick={(e) => {
                            e.stopPropagation()
                            setUploadedFiles(prev => prev.filter((_, j) => j !== i))
                          }}
                        >×</button>
                      </div>
                      <AnimatePresence>
                        {expandedFileIndex === i && (
                          <motion.div
                            className="extracted-text-preview"
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                          >
                            <div className="extracted-text-header">
                              <span>📄 Extracted Text Preview</span>
                              <span className="extracted-skills">
                                {file.skills?.length > 0 && `${file.skills.length} skills detected`}
                              </span>
                            </div>
                            <pre className="extracted-text-content">{file.content || 'No content extracted'}</pre>
                            {file.skills?.length > 0 && (
                              <div className="extracted-skills-list">
                                <span>Skills: </span>
                                {file.skills.map((skill, j) => (
                                  <span key={j} className="skill-pill small">{skill}</span>
                                ))}
                              </div>
                            )}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Match Button */}
          <motion.button
            className="btn-primary"
            onClick={runMatching}
            disabled={loading || !jobDescription.trim() || uploadedFiles.length === 0}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {loading ? (
              <>
                <RefreshCw className="spin" size={20} />
                Analyzing...
              </>
            ) : (
              <>
                <Sparkles size={20} />
                Match Resumes
              </>
            )}
          </motion.button>
        </section>

        {/* Step 2: Pipeline */}
        {(loading || currentStep > 0) && (
          <section className="section">
            <div className="section-header">
              <span className="step-number">2</span>
              <h2>Processing Pipeline</h2>
            </div>
            <PipelineVisualizer
              currentStep={currentStep}
              isProcessing={loading}
              expanded={pipelineExpanded}
              onToggle={() => setPipelineExpanded(!pipelineExpanded)}
            />
          </section>
        )}

        {/* Step 3: Results */}
        {results && results.results && (
          <section className="section results-section">
            <div className="section-header">
              <span className="step-number">3</span>
              <h2>Results</h2>
              <span className="results-count">{results.total_resumes} candidates analyzed</span>
            </div>
            <div className="results-grid">
              {results.results.map((result, index) => (
                <MatchDashboard
                  key={index}
                  result={{ ...result, rank: index + 1 }}
                  jobSkills={jdSkills}
                />
              ))}
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>Resume Matcher v2.0 • Powered by Sentence-BERT • {healthData?.version || 'IR Project 2026'}</p>
      </footer>
    </div>
  )
}

export default App
