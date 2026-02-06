/**
 * 📤 Upload Page
 * Video upload with drag & drop and real-time progress
 */

import { useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

import './Upload.css'

export default function Upload() {
    const [file, setFile] = useState(null)
    const [isDragging, setIsDragging] = useState(false)
    const [uploadProgress, setUploadProgress] = useState(0)
    const [analysisProgress, setAnalysisProgress] = useState(0)
    const [status, setStatus] = useState('idle') // idle, uploading, analyzing, completed, error
    const [error, setError] = useState(null)
    const [analysisId, setAnalysisId] = useState(null)

    const fileInputRef = useRef(null)
    const navigate = useNavigate()

    // Handle drag events
    const handleDragOver = useCallback((e) => {
        e.preventDefault()
        setIsDragging(true)
    }, [])

    const handleDragLeave = useCallback(() => {
        setIsDragging(false)
    }, [])

    const handleDrop = useCallback((e) => {
        e.preventDefault()
        setIsDragging(false)

        const droppedFile = e.dataTransfer.files[0]
        if (droppedFile && isValidVideo(droppedFile)) {
            setFile(droppedFile)
            setError(null)
        } else {
            setError('지원되지 않는 파일 형식입니다. MP4, AVI, MOV, MKV 파일을 업로드하세요.')
        }
    }, [])

    const handleFileSelect = (e) => {
        const selectedFile = e.target.files[0]
        if (selectedFile && isValidVideo(selectedFile)) {
            setFile(selectedFile)
            setError(null)
        } else {
            setError('지원되지 않는 파일 형식입니다.')
        }
    }

    const isValidVideo = (file) => {
        const validTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska', 'video/webm']
        return validTypes.includes(file.type) ||
            /\.(mp4|avi|mov|mkv|webm)$/i.test(file.name)
    }

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes'
        const k = 1024
        const sizes = ['Bytes', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const handleUpload = async () => {
        if (!file) return

        setStatus('uploading')
        setUploadProgress(0)
        setError(null)

        try {
            const formData = new FormData()
            formData.append('file', file)

            // Simulate upload progress
            const uploadInterval = setInterval(() => {
                setUploadProgress(prev => {
                    if (prev >= 90) {
                        clearInterval(uploadInterval)
                        return prev
                    }
                    return prev + 10
                })
            }, 200)

            const response = await fetch('/api/v1/analysis/upload', {
                method: 'POST',
                body: formData
            })

            clearInterval(uploadInterval)
            setUploadProgress(100)

            if (!response.ok) {
                throw new Error('업로드 실패')
            }

            const data = await response.json()
            setAnalysisId(data.id)

            // Start analysis
            await startAnalysis(data.id)

        } catch (err) {
            setStatus('error')
            setError(err.message || '업로드 중 오류가 발생했습니다')
        }
    }

    const startAnalysis = async (videoId) => {
        setStatus('analyzing')
        setAnalysisProgress(0)

        try {
            // Start analysis
            await fetch('/api/v1/analysis/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ video_id: videoId })
            })

            // Connect to WebSocket for progress
            const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/analysis/${videoId}`)

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data)

                if (data.type === 'progress') {
                    setAnalysisProgress(data.progress)
                } else if (data.type === 'complete') {
                    setStatus('completed')
                    setAnalysisProgress(100)
                    ws.close()
                } else if (data.type === 'error') {
                    setStatus('error')
                    setError(data.error)
                    ws.close()
                }
            }

            ws.onerror = () => {
                // Fallback to polling if WebSocket fails
                pollAnalysisStatus(videoId)
            }

        } catch (err) {
            // Fallback to polling
            pollAnalysisStatus(videoId)
        }
    }

    const pollAnalysisStatus = async (videoId) => {
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`/api/v1/analysis/${videoId}/status`)
                const data = await response.json()

                setAnalysisProgress(data.progress)

                if (data.status === 'completed') {
                    setStatus('completed')
                    clearInterval(interval)
                } else if (data.status === 'failed') {
                    setStatus('error')
                    setError('분석 실패')
                    clearInterval(interval)
                }
            } catch (err) {
                // Continue polling
            }
        }, 2000)
    }

    const handleViewResult = () => {
        navigate(`/analysis/${analysisId}`)
    }

    const handleReset = () => {
        setFile(null)
        setStatus('idle')
        setUploadProgress(0)
        setAnalysisProgress(0)
        setError(null)
        setAnalysisId(null)
    }

    return (
        <div className="upload-page">
            <header className="page-header">
                <h1>📤 영상 업로드</h1>
                <p>수업 영상을 업로드하여 AI 분석을 시작하세요</p>
            </header>

            <div className="upload-container">
                <AnimatePresence mode="wait">
                    {status === 'idle' && (
                        <motion.div
                            key="dropzone"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                        >
                            {/* Dropzone */}
                            <div
                                className={`dropzone glass-card ${isDragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="video/*"
                                    onChange={handleFileSelect}
                                    hidden
                                />

                                {!file ? (
                                    <div className="dropzone-content">
                                        <span className="dropzone-icon">🎬</span>
                                        <h3>영상 파일을 드래그하거나 클릭하여 선택</h3>
                                        <p>MP4, AVI, MOV, MKV 지원 (최대 2GB)</p>
                                    </div>
                                ) : (
                                    <div className="file-preview">
                                        <span className="file-icon">📹</span>
                                        <div className="file-info">
                                            <span className="file-name">{file.name}</span>
                                            <span className="file-size">{formatFileSize(file.size)}</span>
                                        </div>
                                        <button
                                            className="btn btn-secondary"
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                setFile(null)
                                            }}
                                        >
                                            변경
                                        </button>
                                    </div>
                                )}
                            </div>

                            {file && (
                                <motion.button
                                    className="btn btn-primary btn-lg upload-btn"
                                    onClick={handleUpload}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                >
                                    🚀 분석 시작
                                </motion.button>
                            )}
                        </motion.div>
                    )}

                    {(status === 'uploading' || status === 'analyzing') && (
                        <motion.div
                            key="progress"
                            className="glass-card progress-container"
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                        >
                            <div className="progress-header">
                                <span className="progress-icon animate-pulse">
                                    {status === 'uploading' ? '📤' : '🔬'}
                                </span>
                                <div>
                                    <h3>{status === 'uploading' ? '업로드 중...' : 'AI 분석 중...'}</h3>
                                    <p>{file?.name}</p>
                                </div>
                            </div>

                            <div className="progress-bar-container">
                                <div className="progress-bar">
                                    <motion.div
                                        className="progress-bar-fill"
                                        initial={{ width: 0 }}
                                        animate={{
                                            width: `${status === 'uploading' ? uploadProgress : analysisProgress}%`
                                        }}
                                    />
                                </div>
                                <span className="progress-percent">
                                    {status === 'uploading' ? uploadProgress : analysisProgress}%
                                </span>
                            </div>

                            {status === 'analyzing' && (
                                <div className="analysis-steps">
                                    <AnalysisStep
                                        label="프레임 추출"
                                        completed={analysisProgress >= 30}
                                        active={analysisProgress > 0 && analysisProgress < 30}
                                    />
                                    <AnalysisStep
                                        label="음성 인식 (STT)"
                                        completed={analysisProgress >= 50}
                                        active={analysisProgress >= 30 && analysisProgress < 50}
                                    />
                                    <AnalysisStep
                                        label="감정 분석"
                                        completed={analysisProgress >= 70}
                                        active={analysisProgress >= 50 && analysisProgress < 70}
                                    />
                                    <AnalysisStep
                                        label="7차원 평가"
                                        completed={analysisProgress >= 90}
                                        active={analysisProgress >= 70 && analysisProgress < 90}
                                    />
                                    <AnalysisStep
                                        label="리포트 생성"
                                        completed={analysisProgress >= 100}
                                        active={analysisProgress >= 90 && analysisProgress < 100}
                                    />
                                </div>
                            )}
                        </motion.div>
                    )}

                    {status === 'completed' && (
                        <motion.div
                            key="completed"
                            className="glass-card result-container"
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                        >
                            <span className="result-icon">✅</span>
                            <h2>분석 완료!</h2>
                            <p>AI 수업 분석이 완료되었습니다</p>

                            <div className="result-actions">
                                <button
                                    className="btn btn-primary btn-lg"
                                    onClick={handleViewResult}
                                >
                                    📊 결과 보기
                                </button>
                                <button
                                    className="btn btn-secondary"
                                    onClick={handleReset}
                                >
                                    새 분석 시작
                                </button>
                            </div>
                        </motion.div>
                    )}

                    {status === 'error' && (
                        <motion.div
                            key="error"
                            className="glass-card error-container"
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                        >
                            <span className="error-icon">❌</span>
                            <h2>오류 발생</h2>
                            <p>{error}</p>

                            <button
                                className="btn btn-primary"
                                onClick={handleReset}
                            >
                                다시 시도
                            </button>
                        </motion.div>
                    )}
                </AnimatePresence>

                {error && status === 'idle' && (
                    <motion.div
                        className="error-message"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        ⚠️ {error}
                    </motion.div>
                )}
            </div>

            {/* Features */}
            <section className="features-section">
                <h3>🔍 분석 항목</h3>
                <div className="features-grid">
                    <FeatureCard icon="👁️" title="비전 분석" desc="시선, 제스처, 자세 분석" />
                    <FeatureCard icon="🎤" title="음성 분석" desc="발화 속도, 억양, 습관어" />
                    <FeatureCard icon="😊" title="감정 분석" desc="표정 및 음성 감정 탐지" />
                    <FeatureCard icon="📊" title="7차원 평가" desc="임용 2차 기준 100점 평가" />
                </div>
            </section>
        </div>
    )
}

function AnalysisStep({ label, completed, active }) {
    return (
        <div className={`analysis-step ${completed ? 'completed' : ''} ${active ? 'active' : ''}`}>
            <span className="step-indicator">
                {completed ? '✓' : active ? <span className="animate-spin">◌</span> : '○'}
            </span>
            <span className="step-label">{label}</span>
        </div>
    )
}

function FeatureCard({ icon, title, desc }) {
    return (
        <motion.div
            className="glass-card feature-card"
            whileHover={{ scale: 1.02 }}
        >
            <span className="feature-icon">{icon}</span>
            <h4>{title}</h4>
            <p>{desc}</p>
        </motion.div>
    )
}
