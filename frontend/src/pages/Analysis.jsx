/**
 * 📊 Analysis Page
 * Detailed analysis result view
 */

import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
    RadarChart, Radar, PolarGrid, PolarAngleAxis,
    PolarRadiusAxis, ResponsiveContainer
} from 'recharts'

import './Analysis.css'

// Demo analysis result
const DEMO_RESULT = {
    id: 'demo123',
    video_name: '20251209_110545.mp4',
    created_at: '2025-12-09T11:05:45',
    evaluation: {
        total_score: 84,
        grade: 'A',
        dimensions: {
            teaching_expertise: { score: 17, max_score: 20, feedback: '학습 목표가 명확하게 제시되었습니다.' },
            teaching_method: { score: 16, max_score: 20, feedback: '다양한 교수법을 활용하고 있습니다.' },
            communication: { score: 13, max_score: 15, feedback: '습관어 3회 감지됨. 발화 명료성이 우수합니다.' },
            teaching_attitude: { score: 12, max_score: 15, feedback: '자신감 있는 수업 태도가 돋보입니다.' },
            student_engagement: { score: 11, max_score: 15, feedback: '학생과의 상호작용이 활발합니다.' },
            time_management: { score: 8, max_score: 10, feedback: '시간 배분이 적절합니다.' },
            creativity: { score: 4, max_score: 5, feedback: '창의적인 질문 기법을 사용했습니다.' }
        }
    },
    transcript: {
        text: '여러분 안녕하세요. 오늘은 분수의 덧셈에 대해 배워볼 거예요...',
        segments_count: 45,
        filler_words: { '음': 2, '어': 1 }
    },
    emotion: {
        positive_ratio: 0.72,
        neutral_ratio: 0.25,
        negative_ratio: 0.03,
        dominant_emotion: 'happy'
    },
    vision: {
        face_visible_ratio: 0.89,
        gesture_active_ratio: 0.45,
        avg_face_confidence: 0.92
    },
    audio: {
        avg_volume: -22.5,
        peak_volume: -12.3,
        silence_ratio: 0.12
    }
}

const DIMENSION_LABELS = {
    teaching_expertise: '수업 전문성',
    teaching_method: '교수학습 방법',
    communication: '판서 및 언어',
    teaching_attitude: '수업 태도',
    student_engagement: '학생 참여',
    time_management: '시간 배분',
    creativity: '창의성'
}

export default function Analysis() {
    const { id } = useParams()
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        loadAnalysis()
    }, [id])

    const loadAnalysis = async () => {
        try {
            const response = await fetch(`/api/v1/analysis/${id}`)

            if (!response.ok) {
                throw new Error('분석 결과를 찾을 수 없습니다')
            }

            const data = await response.json()
            setResult(data.result || DEMO_RESULT)
        } catch (err) {
            // Use demo data for now
            setResult(DEMO_RESULT)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="loading-container">
                <span className="animate-spin">🔄</span>
                <p>결과 로딩 중...</p>
            </div>
        )
    }

    if (error && !result) {
        return (
            <div className="error-container glass-card">
                <h2>오류</h2>
                <p>{error}</p>
                <Link to="/upload" className="btn btn-primary">새 분석 시작</Link>
            </div>
        )
    }

    const radarData = Object.entries(result.evaluation.dimensions).map(([key, value]) => ({
        dimension: DIMENSION_LABELS[key],
        score: (value.score / value.max_score) * 100,
        fullMark: 100
    }))

    return (
        <div className="analysis-page">
            <header className="page-header">
                <div>
                    <h1>📊 분석 결과</h1>
                    <p>{result.video_name}</p>
                </div>
                <div className="header-actions">
                    <Link to="/coach" className="btn btn-secondary">
                        🤖 AI 코치에게 질문
                    </Link>
                    <button className="btn btn-primary">
                        📄 PDF 다운로드
                    </button>
                </div>
            </header>

            {/* Score Overview */}
            <section className="score-overview">
                <motion.div
                    className="glass-card total-score-card"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                >
                    <div className="score-circle-large">
                        <svg viewBox="0 0 100 100">
                            <defs>
                                <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" stopColor="var(--color-accent-primary)" />
                                    <stop offset="100%" stopColor="var(--color-accent-secondary)" />
                                </linearGradient>
                            </defs>
                            <circle
                                cx="50"
                                cy="50"
                                r="42"
                                fill="none"
                                stroke="var(--glass-border)"
                                strokeWidth="6"
                            />
                            <motion.circle
                                cx="50"
                                cy="50"
                                r="42"
                                fill="none"
                                stroke="url(#scoreGradient)"
                                strokeWidth="6"
                                strokeLinecap="round"
                                strokeDasharray={`${result.evaluation.total_score * 2.64} 264`}
                                initial={{ strokeDasharray: '0 264' }}
                                animate={{ strokeDasharray: `${result.evaluation.total_score * 2.64} 264` }}
                                transition={{ duration: 1, ease: 'easeOut' }}
                                style={{ transformOrigin: 'center', transform: 'rotate(-90deg)' }}
                            />
                        </svg>
                        <div className="score-text">
                            <span className="score-value">{result.evaluation.total_score}</span>
                            <span className="score-label">점</span>
                        </div>
                    </div>
                    <div className="grade-badge">
                        <span className={`grade grade-${result.evaluation.grade.charAt(0)}`}>
                            {result.evaluation.grade}
                        </span>
                    </div>
                </motion.div>

                <motion.div
                    className="glass-card radar-card"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <h3>7차원 평가</h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <RadarChart data={radarData}>
                            <PolarGrid stroke="rgba(255,255,255,0.1)" />
                            <PolarAngleAxis
                                dataKey="dimension"
                                tick={{ fill: 'var(--color-text-secondary)', fontSize: 10 }}
                            />
                            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} />
                            <Radar
                                dataKey="score"
                                stroke="var(--color-accent-primary)"
                                fill="var(--color-accent-primary)"
                                fillOpacity={0.3}
                            />
                        </RadarChart>
                    </ResponsiveContainer>
                </motion.div>
            </section>

            {/* Dimension Details */}
            <section className="dimensions-section">
                <h2>📋 상세 평가</h2>
                <div className="dimensions-grid">
                    {Object.entries(result.evaluation.dimensions).map(([key, value], index) => (
                        <motion.div
                            key={key}
                            className="glass-card dimension-card"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 * index }}
                        >
                            <div className="dimension-header">
                                <span className="dimension-name">{DIMENSION_LABELS[key]}</span>
                                <span className="dimension-score">
                                    {value.score}/{value.max_score}
                                </span>
                            </div>
                            <div className="dimension-bar">
                                <motion.div
                                    className="dimension-bar-fill"
                                    initial={{ width: 0 }}
                                    animate={{ width: `${(value.score / value.max_score) * 100}%` }}
                                    transition={{ delay: 0.2 + 0.1 * index, duration: 0.5 }}
                                />
                            </div>
                            <p className="dimension-feedback">{value.feedback}</p>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* Analysis Insights */}
            <section className="insights-section">
                <div className="insights-grid">
                    {/* Transcript Summary */}
                    <motion.div
                        className="glass-card"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                    >
                        <h3>🎤 음성 분석</h3>
                        <div className="insight-content">
                            <div className="insight-stat">
                                <span className="stat-number">{result.transcript.segments_count}</span>
                                <span className="stat-label">발화 세그먼트</span>
                            </div>
                            <div className="insight-stat">
                                <span className="stat-number">
                                    {Object.values(result.transcript.filler_words).reduce((a, b) => a + b, 0)}
                                </span>
                                <span className="stat-label">습관어 감지</span>
                            </div>
                        </div>
                        <div className="filler-words">
                            {Object.entries(result.transcript.filler_words).map(([word, count]) => (
                                <span key={word} className="filler-tag">
                                    "{word}" × {count}
                                </span>
                            ))}
                        </div>
                    </motion.div>

                    {/* Emotion Summary */}
                    <motion.div
                        className="glass-card"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6 }}
                    >
                        <h3>😊 감정 분석</h3>
                        <div className="emotion-bars">
                            <div className="emotion-bar-item">
                                <span>긍정</span>
                                <div className="emotion-bar">
                                    <div
                                        className="emotion-bar-fill positive"
                                        style={{ width: `${result.emotion.positive_ratio * 100}%` }}
                                    />
                                </div>
                                <span>{Math.round(result.emotion.positive_ratio * 100)}%</span>
                            </div>
                            <div className="emotion-bar-item">
                                <span>중립</span>
                                <div className="emotion-bar">
                                    <div
                                        className="emotion-bar-fill neutral"
                                        style={{ width: `${result.emotion.neutral_ratio * 100}%` }}
                                    />
                                </div>
                                <span>{Math.round(result.emotion.neutral_ratio * 100)}%</span>
                            </div>
                            <div className="emotion-bar-item">
                                <span>부정</span>
                                <div className="emotion-bar">
                                    <div
                                        className="emotion-bar-fill negative"
                                        style={{ width: `${result.emotion.negative_ratio * 100}%` }}
                                    />
                                </div>
                                <span>{Math.round(result.emotion.negative_ratio * 100)}%</span>
                            </div>
                        </div>
                    </motion.div>

                    {/* Vision Summary */}
                    <motion.div
                        className="glass-card"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.7 }}
                    >
                        <h3>👁️ 비전 분석</h3>
                        <div className="insight-content">
                            <div className="insight-stat">
                                <span className="stat-number">
                                    {Math.round(result.vision.face_visible_ratio * 100)}%
                                </span>
                                <span className="stat-label">얼굴 노출</span>
                            </div>
                            <div className="insight-stat">
                                <span className="stat-number">
                                    {Math.round(result.vision.gesture_active_ratio * 100)}%
                                </span>
                                <span className="stat-label">제스처 활성</span>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* Actions */}
            <section className="actions-section">
                <Link to="/upload" className="btn btn-secondary btn-lg">
                    새 분석 시작
                </Link>
                <Link to={`/coach?analysis=${id}`} className="btn btn-primary btn-lg">
                    🤖 AI 코치와 상담
                </Link>
            </section>
        </div>
    )
}
