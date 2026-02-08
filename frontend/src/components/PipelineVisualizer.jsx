import { motion, AnimatePresence } from 'framer-motion'
import { FileText, Brain, Ruler, Search, CheckCircle2, Loader2, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'

const steps = [
    { id: 1, icon: FileText, label: 'Parsing Documents', detail: 'Extracting text from PDF/TXT files' },
    { id: 2, icon: Brain, label: 'Generating BERT Vectors', detail: 'Creating 384-dim embeddings' },
    { id: 3, icon: Ruler, label: 'Calculating Similarity', detail: 'Computing cosine distance' },
    { id: 4, icon: Search, label: 'Analyzing Skill Gaps', detail: 'Matching skills with synonyms' },
    { id: 5, icon: CheckCircle2, label: 'Ranking Results', detail: 'Sorting by weighted score' },
]

export default function PipelineVisualizer({ currentStep = 0, isProcessing = false, expanded = false, onToggle }) {
    const completedSteps = Math.min(currentStep, steps.length)
    const progress = (completedSteps / steps.length) * 100

    return (
        <div className="pipeline-container">
            {/* Collapsed View */}
            <div className="pipeline-header" onClick={onToggle}>
                <div className="pipeline-summary">
                    <span className="pipeline-title">
                        {isProcessing ? (
                            <>
                                <Loader2 className="spin-icon" size={18} />
                                Processing Step {currentStep}/{steps.length}...
                            </>
                        ) : currentStep === steps.length ? (
                            <>
                                <CheckCircle2 className="check-icon" size={18} />
                                Analysis Complete
                            </>
                        ) : (
                            'Ready to Analyze'
                        )}
                    </span>
                    <button className="toggle-btn">
                        {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                    </button>
                </div>

                {/* Progress Bar */}
                <div className="progress-track">
                    <motion.div
                        className="progress-fill"
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.5, ease: 'easeOut' }}
                    />
                </div>
            </div>

            {/* Expanded View */}
            <AnimatePresence>
                {expanded && (
                    <motion.div
                        className="pipeline-steps"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: 'easeInOut' }}
                    >
                        {steps.map((step, index) => {
                            const StepIcon = step.icon
                            const isActive = currentStep === index + 1
                            const isComplete = currentStep > index + 1 || (currentStep === steps.length && index + 1 === steps.length)
                            const isPending = currentStep < index + 1

                            return (
                                <motion.div
                                    key={step.id}
                                    className={`pipeline-step ${isComplete ? 'complete' : isActive ? 'active' : 'pending'}`}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    layout
                                >
                                    <div className={`step-icon-wrapper ${isComplete ? 'complete' : isActive ? 'active' : ''}`}>
                                        {isActive && isProcessing ? (
                                            <Loader2 className="spin-icon" size={20} />
                                        ) : isComplete ? (
                                            <CheckCircle2 size={20} />
                                        ) : (
                                            <StepIcon size={20} />
                                        )}
                                    </div>
                                    <div className="step-content">
                                        <span className="step-label">{step.label}</span>
                                        <span className="step-detail">{step.detail}</span>
                                    </div>
                                    {isActive && (
                                        <motion.div
                                            className="step-pulse"
                                            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                                            transition={{ repeat: Infinity, duration: 1.5 }}
                                        />
                                    )}
                                </motion.div>
                            )
                        })}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}
