import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect, useCallback } from 'react'
import { Edit3, Save, X, Sparkles, AlertCircle } from 'lucide-react'

/**
 * LiveResumeEditor - Real-time resume editor with skill highlighting
 * Features:
 * - Live editing with auto-save
 * - Skill highlighting as you type
 * - Character count
 * - Ceramic Light theme styling
 */
export default function LiveResumeEditor({
    initialContent = '',
    onSave,
    onSkillsExtract,
    skills = [],
    readOnly = false
}) {
    const [content, setContent] = useState(initialContent)
    const [isEditing, setIsEditing] = useState(false)
    const [isSaving, setIsSaving] = useState(false)
    const [extractedSkills, setExtractedSkills] = useState(skills)
    const [showSkillHighlight, setShowSkillHighlight] = useState(true)

    // Update content when initialContent changes
    useEffect(() => {
        setContent(initialContent)
    }, [initialContent])

    // Debounced skill extraction
    const extractSkills = useCallback(async (text) => {
        if (!onSkillsExtract || text.length < 50) return

        try {
            const skills = await onSkillsExtract(text)
            setExtractedSkills(skills || [])
        } catch (e) {
            console.log('Skill extraction failed:', e)
        }
    }, [onSkillsExtract])

    useEffect(() => {
        const timer = setTimeout(() => {
            if (content && content !== initialContent) {
                extractSkills(content)
            }
        }, 800)
        return () => clearTimeout(timer)
    }, [content, extractSkills, initialContent])

    // Highlight skills in text
    const highlightSkills = (text) => {
        if (!showSkillHighlight || extractedSkills.length === 0) return text

        let highlighted = text
        extractedSkills.forEach(skill => {
            const regex = new RegExp(`\\b(${skill})\\b`, 'gi')
            highlighted = highlighted.replace(regex, '【$1】')
        })
        return highlighted
    }

    const handleSave = async () => {
        if (!onSave) return
        setIsSaving(true)
        try {
            await onSave(content, extractedSkills)
            setIsEditing(false)
        } catch (e) {
            console.error('Save failed:', e)
        } finally {
            setIsSaving(false)
        }
    }

    const charCount = content.length
    const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0

    return (
        <motion.div
            className="live-editor"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
        >
            {/* Header */}
            <div className="editor-header">
                <div className="editor-title">
                    <Edit3 size={18} />
                    <span>Resume Content</span>
                    {extractedSkills.length > 0 && (
                        <span className="skill-badge">
                            <Sparkles size={12} />
                            {extractedSkills.length} skills
                        </span>
                    )}
                </div>
                <div className="editor-actions">
                    <button
                        className={`toggle-highlight ${showSkillHighlight ? 'active' : ''}`}
                        onClick={() => setShowSkillHighlight(!showSkillHighlight)}
                        title="Toggle skill highlighting"
                    >
                        <Sparkles size={14} />
                    </button>
                    {!readOnly && (
                        <>
                            {isEditing ? (
                                <>
                                    <button
                                        className="btn-save"
                                        onClick={handleSave}
                                        disabled={isSaving}
                                    >
                                        <Save size={14} />
                                        {isSaving ? 'Saving...' : 'Save'}
                                    </button>
                                    <button
                                        className="btn-cancel"
                                        onClick={() => {
                                            setContent(initialContent)
                                            setIsEditing(false)
                                        }}
                                    >
                                        <X size={14} />
                                    </button>
                                </>
                            ) : (
                                <button
                                    className="btn-edit"
                                    onClick={() => setIsEditing(true)}
                                >
                                    <Edit3 size={14} />
                                    Edit
                                </button>
                            )}
                        </>
                    )}
                </div>
            </div>

            {/* Content Area */}
            <div className="editor-content-wrapper">
                {isEditing ? (
                    <textarea
                        className="editor-textarea"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder="Paste or type resume content here..."
                        autoFocus
                    />
                ) : (
                    <div className="editor-display">
                        {content ? (
                            <p className="content-text">
                                {showSkillHighlight ? (
                                    // Render with highlighted skills
                                    content.split(/(\s+)/).map((word, i) => {
                                        const isSkill = extractedSkills.some(
                                            skill => word.toLowerCase().includes(skill.toLowerCase())
                                        )
                                        return isSkill ? (
                                            <mark key={i} className="skill-highlight">{word}</mark>
                                        ) : (
                                            <span key={i}>{word}</span>
                                        )
                                    })
                                ) : (
                                    content
                                )}
                            </p>
                        ) : (
                            <div className="empty-state">
                                <AlertCircle size={24} />
                                <p>No content yet. Click Edit to add resume text.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Footer Stats */}
            <div className="editor-footer">
                <span className="stat">{charCount.toLocaleString()} characters</span>
                <span className="stat">{wordCount.toLocaleString()} words</span>
                {extractedSkills.length > 0 && (
                    <div className="extracted-skills">
                        {extractedSkills.slice(0, 8).map((skill, i) => (
                            <motion.span
                                key={i}
                                className="skill-tag"
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: i * 0.05 }}
                            >
                                {skill}
                            </motion.span>
                        ))}
                        {extractedSkills.length > 8 && (
                            <span className="skill-more">+{extractedSkills.length - 8} more</span>
                        )}
                    </div>
                )}
            </div>

            <style>{`
                .live-editor {
                    background: var(--bg-card, #ffffff);
                    border: 1px solid var(--border, #e2e8f0);
                    border-radius: var(--radius, 16px);
                    overflow: hidden;
                    box-shadow: var(--shadow, 0 4px 6px -1px rgba(0,0,0,0.05));
                }

                .editor-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1rem 1.25rem;
                    border-bottom: 1px solid var(--border, #e2e8f0);
                    background: var(--bg-elevated, #f8f7f5);
                }

                .editor-title {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    font-weight: 600;
                    font-size: 0.95rem;
                    color: var(--text-primary, #1e293b);
                }

                .skill-badge {
                    display: flex;
                    align-items: center;
                    gap: 0.25rem;
                    background: var(--accent, #7c3aed);
                    color: white;
                    font-size: 0.7rem;
                    font-weight: 500;
                    padding: 0.2rem 0.5rem;
                    border-radius: 12px;
                    margin-left: 0.5rem;
                }

                .editor-actions {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }

                .toggle-highlight {
                    width: 32px;
                    height: 32px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: transparent;
                    border: 1px solid var(--border, #e2e8f0);
                    border-radius: 6px;
                    color: var(--text-muted, #94a3b8);
                    cursor: pointer;
                    transition: all 0.2s;
                }

                .toggle-highlight:hover,
                .toggle-highlight.active {
                    background: var(--accent-light, #ede9fe);
                    color: var(--accent, #7c3aed);
                    border-color: var(--accent, #7c3aed);
                }

                .btn-edit, .btn-save, .btn-cancel {
                    display: flex;
                    align-items: center;
                    gap: 0.35rem;
                    padding: 0.45rem 0.8rem;
                    border-radius: 6px;
                    font-size: 0.8rem;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s;
                }

                .btn-edit {
                    background: var(--bg-card, #ffffff);
                    border: 1px solid var(--border, #e2e8f0);
                    color: var(--text-secondary, #64748b);
                }

                .btn-edit:hover {
                    border-color: var(--accent, #7c3aed);
                    color: var(--accent, #7c3aed);
                }

                .btn-save {
                    background: var(--accent, #7c3aed);
                    border: none;
                    color: white;
                }

                .btn-save:hover:not(:disabled) {
                    background: var(--accent-hover, #6d28d9);
                }

                .btn-save:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }

                .btn-cancel {
                    background: transparent;
                    border: 1px solid var(--border, #e2e8f0);
                    color: var(--text-muted, #94a3b8);
                }

                .btn-cancel:hover {
                    border-color: var(--danger, #ef4444);
                    color: var(--danger, #ef4444);
                }

                .editor-content-wrapper {
                    min-height: 200px;
                    max-height: 400px;
                    overflow-y: auto;
                }

                .editor-textarea {
                    width: 100%;
                    min-height: 200px;
                    padding: 1rem 1.25rem;
                    border: none;
                    background: var(--bg-card, #ffffff);
                    color: var(--text-primary, #1e293b);
                    font-family: inherit;
                    font-size: 0.9rem;
                    line-height: 1.7;
                    resize: vertical;
                }

                .editor-textarea:focus {
                    outline: none;
                    background: var(--bg-elevated, #f8f7f5);
                }

                .editor-display {
                    padding: 1rem 1.25rem;
                }

                .content-text {
                    font-size: 0.9rem;
                    line-height: 1.7;
                    color: var(--text-primary, #1e293b);
                    white-space: pre-wrap;
                    word-break: break-word;
                }

                .skill-highlight {
                    background: var(--accent-light, #ede9fe);
                    color: var(--accent, #7c3aed);
                    padding: 0.1rem 0.3rem;
                    border-radius: 4px;
                    font-weight: 500;
                }

                .empty-state {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 3rem;
                    color: var(--text-muted, #94a3b8);
                    text-align: center;
                }

                .empty-state p {
                    margin-top: 0.75rem;
                    font-size: 0.9rem;
                }

                .editor-footer {
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    padding: 0.75rem 1.25rem;
                    border-top: 1px solid var(--border, #e2e8f0);
                    background: var(--bg-elevated, #f8f7f5);
                    flex-wrap: wrap;
                }

                .stat {
                    font-size: 0.75rem;
                    color: var(--text-muted, #94a3b8);
                }

                .extracted-skills {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 0.35rem;
                    margin-left: auto;
                }

                .skill-tag {
                    background: var(--success-light, #d1fae5);
                    color: var(--success, #10b981);
                    font-size: 0.7rem;
                    font-weight: 500;
                    padding: 0.2rem 0.5rem;
                    border-radius: 10px;
                }

                .skill-more {
                    font-size: 0.7rem;
                    color: var(--text-muted, #94a3b8);
                    padding: 0.2rem 0.4rem;
                }
            `}</style>
        </motion.div>
    )
}
