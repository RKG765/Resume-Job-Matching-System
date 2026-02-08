import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Minus, Info, X } from 'lucide-react'

// Animated counter hook
function useCountUp(target, duration = 1500) {
    const [count, setCount] = useState(0)

    useEffect(() => {
        if (target === 0) { setCount(0); return }

        const startTime = Date.now()
        const animate = () => {
            const elapsed = Date.now() - startTime
            const progress = Math.min(elapsed / duration, 1)
            // Ease out quad
            const eased = 1 - (1 - progress) * (1 - progress)
            setCount(Math.round(target * eased))
            if (progress < 1) requestAnimationFrame(animate)
        }
        requestAnimationFrame(animate)
    }, [target, duration])

    return count
}

// Radial Gauge Component
function RadialGauge({ score, size = 180 }) {
    const animatedScore = useCountUp(score)
    const radius = (size - 20) / 2
    const circumference = 2 * Math.PI * radius
    const strokeDashoffset = circumference - (animatedScore / 100) * circumference

    const getColor = (s) => {
        if (s >= 70) return { stroke: '#10b981', bg: '#d1fae5', text: '#059669' }
        if (s >= 40) return { stroke: '#f59e0b', bg: '#fef3c7', text: '#d97706' }
        return { stroke: '#ef4444', bg: '#fee2e2', text: '#dc2626' }
    }

    const colors = getColor(animatedScore)

    return (
        <div className="gauge-container" style={{ width: size, height: size }}>
            <svg width={size} height={size} className="gauge-svg">
                {/* Background circle */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke="#e2e8f0"
                    strokeWidth="12"
                />
                {/* Progress circle */}
                <motion.circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={colors.stroke}
                    strokeWidth="12"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset }}
                    transition={{ duration: 1.5, ease: 'easeOut' }}
                    style={{ transform: 'rotate(-90deg)', transformOrigin: 'center' }}
                />
            </svg>
            <div className="gauge-value" style={{ color: colors.text }}>
                <span className="gauge-number">{animatedScore}</span>
                <span className="gauge-percent">%</span>
            </div>
            <div className="gauge-label" style={{ backgroundColor: colors.bg, color: colors.text }}>
                {animatedScore >= 70 ? 'Strong Match' : animatedScore >= 40 ? 'Partial Match' : 'Weak Match'}
            </div>
        </div>
    )
}

// Skill Chip Component
function SkillChip({ skill, type, onHover, onLeave }) {
    const classes = {
        matched: 'skill-chip matched',
        partial: 'skill-chip partial',
        missing: 'skill-chip missing'
    }

    return (
        <motion.span
            className={classes[type]}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            whileHover={{ scale: 1.05 }}
            onMouseEnter={() => onHover && onHover(skill)}
            onMouseLeave={() => onLeave && onLeave()}
        >
            {type === 'matched' && '✓ '}
            {type === 'missing' && '✗ '}
            {skill}
        </motion.span>
    )
}

export default function MatchDashboard({ result, jobSkills = [] }) {
    const [tooltip, setTooltip] = useState(null)
    const [showBreakdown, setShowBreakdown] = useState(false)

    if (!result) return null

    const score = Math.max(0, Math.min(100, Math.round((result.score || 0) * 100)))
    const contentSim = Math.max(0, Math.min(100, Math.round((result.content_similarity || 0) * 100)))
    const skillSim = Math.max(0, Math.min(100, Math.round((result.skill_similarity || 0) * 100)))
    const matchedSkills = result.matched_skills || []
    const missingSkills = result.missing_skills || []

    return (
        <motion.div
            className="match-dashboard"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
        >
            {/* Header */}
            <div className="dashboard-header">
                <div className="candidate-info">
                    <h3>{result.name}</h3>
                    <span className="rank-badge">#{result.rank || 1}</span>
                </div>
                <div className="score-trend">
                    {score >= 70 ? <TrendingUp className="trend-up" /> :
                        score >= 40 ? <Minus className="trend-neutral" /> :
                            <TrendingDown className="trend-down" />}
                </div>
            </div>

            {/* Main Score Gauge */}
            <div className="dashboard-main">
                <RadialGauge score={score} />

                <div className="score-details">
                    <div className="score-row">
                        <span className="score-label">BERT Semantic</span>
                        <div className="mini-bar">
                            <motion.div
                                className="mini-fill bert"
                                initial={{ width: 0 }}
                                animate={{ width: `${contentSim}%` }}
                                transition={{ duration: 1, delay: 0.3 }}
                            />
                        </div>
                        <span className="score-value">{contentSim}%</span>
                    </div>
                    <div className="score-row">
                        <span className="score-label">Skills Match</span>
                        <div className="mini-bar">
                            <motion.div
                                className="mini-fill skills"
                                initial={{ width: 0 }}
                                animate={{ width: `${skillSim}%` }}
                                transition={{ duration: 1, delay: 0.5 }}
                            />
                        </div>
                        <span className="score-value">{skillSim}%</span>
                    </div>
                </div>
            </div>

            {/* Formula Breakdown */}
            <button
                className="breakdown-toggle"
                onClick={() => setShowBreakdown(!showBreakdown)}
            >
                <Info size={16} />
                {showBreakdown ? 'Hide' : 'Show'} Score Formula
            </button>

            <AnimatePresence>
                {showBreakdown && (
                    <motion.div
                        className="formula-box"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                    >
                        <code>Score = (BERT × 0.4) + (Skills × 0.6)</code>
                        <p>= ({contentSim}% × 0.4) + ({skillSim}% × 0.6)</p>
                        <p>= {Math.round(contentSim * 0.4)}% + {Math.round(skillSim * 0.6)}%</p>
                        <p className="result">= <strong>{score}%</strong></p>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Skills Heatmap */}
            <div className="skills-heatmap">
                <div className="skills-section">
                    <h4>✓ Matched Skills ({matchedSkills.length})</h4>
                    <div className="skills-grid">
                        {matchedSkills.length > 0 ? (
                            matchedSkills.map((skill, i) => (
                                <SkillChip key={i} skill={skill} type="matched" />
                            ))
                        ) : (
                            <span className="no-skills">No matching skills found</span>
                        )}
                    </div>
                </div>

                <div className="skills-section">
                    <h4>✗ Missing Skills ({missingSkills.length})</h4>
                    <div className="skills-grid">
                        {missingSkills.length > 0 ? (
                            missingSkills.map((skill, i) => (
                                <SkillChip
                                    key={i}
                                    skill={skill}
                                    type="missing"
                                    onHover={(s) => setTooltip(s)}
                                    onLeave={() => setTooltip(null)}
                                />
                            ))
                        ) : (
                            <span className="no-skills">All required skills present! 🎉</span>
                        )}
                    </div>
                </div>
            </div>

            {/* Tooltip */}
            <AnimatePresence>
                {tooltip && (
                    <motion.div
                        className="skill-tooltip"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                    >
                        <strong>💡 Recommendation</strong>
                        <p>Add a project using <em>{tooltip}</em> to improve match by ~5%</p>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* AI Explanation */}
            {result.explanation && (
                <div className="ai-explanation">
                    <h4>🤖 AI Analysis</h4>
                    <p>{formatExplanation(result.explanation)}</p>
                </div>
            )}
        </motion.div>
    )
}

function formatExplanation(text) {
    if (!text) return ''
    return text
        .replace(/\*\*/g, '')
        .replace(/\*/g, '')
        .replace(/_/g, '')
        .split('\n')
        .filter(l => l.trim())
        .join(' ')
        .slice(0, 500)
}
