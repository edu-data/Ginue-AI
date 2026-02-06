/**
 * 📈 Portfolio Page
 * Student portfolio with growth tracking and badges
 */

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
    LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
    RadarChart, Radar, PolarGrid, PolarAngleAxis
} from 'recharts'

import './Portfolio.css'

// Demo data
const DEMO_SESSIONS = [
    { id: 1, date: '2025-12-09', video: '20251209_110545.mp4', score: 84, grade: 'A' },
    { id: 2, date: '2025-12-09', video: '20251209_143455.mp4', score: 81, grade: 'A' },
    { id: 3, date: '2025-12-09', video: '20251209_151833.mp4', score: 79, grade: 'B+' },
    { id: 4, date: '2025-12-09', video: '20251209_142648.mp4', score: 76, grade: 'B' },
    { id: 5, date: '2025-12-09', video: '20251209_104016.mp4', score: 75, grade: 'B' },
    { id: 6, date: '2025-12-09', video: '20251209_102400.mp4', score: 73, grade: 'B' },
]

const DEMO_BADGES = [
    { id: 1, icon: '🌟', name: '첫 분석', desc: '첫 수업 분석 완료', earned: true, date: '2025-12-09' },
    { id: 2, icon: '🎯', name: '목표 달성', desc: '80점 이상 달성', earned: true, date: '2025-12-09' },
    { id: 3, icon: '📈', name: '성장중', desc: '3회 이상 분석 완료', earned: true, date: '2025-12-09' },
    { id: 4, icon: '🏆', name: 'A+ 등급', desc: '90점 이상 달성', earned: false },
    { id: 5, icon: '🔥', name: '연속 향상', desc: '3회 연속 점수 상승', earned: false },
    { id: 6, icon: '💎', name: '마스터', desc: '10회 분석 완료', earned: false },
]

const GROWTH_DATA = [
    { session: '1', score: 73 },
    { session: '2', score: 75 },
    { session: '3', score: 76 },
    { session: '4', score: 79 },
    { session: '5', score: 81 },
    { session: '6', score: 84 },
]

const DIMENSION_COMPARE = [
    { dimension: '수업\n전문성', first: 70, latest: 85 },
    { dimension: '교수학습\n방법', first: 65, latest: 80 },
    { dimension: '판서 및\n언어', first: 75, latest: 87 },
    { dimension: '수업\n태도', first: 72, latest: 80 },
    { dimension: '학생\n참여', first: 60, latest: 73 },
    { dimension: '시간\n배분', first: 68, latest: 80 },
    { dimension: '창의성', first: 50, latest: 80 },
]

export default function Portfolio() {
    const [selectedTab, setSelectedTab] = useState('overview')

    const avgScore = Math.round(
        DEMO_SESSIONS.reduce((sum, s) => sum + s.score, 0) / DEMO_SESSIONS.length
    )

    const earnedBadges = DEMO_BADGES.filter(b => b.earned).length
    const totalBadges = DEMO_BADGES.length

    return (
        <div className="portfolio-page">
            <header className="page-header">
                <div>
                    <h1>📈 포트폴리오</h1>
                    <p>나의 수업 역량 성장 기록</p>
                </div>
            </header>

            {/* Stats Overview */}
            <section className="portfolio-stats">
                <motion.div
                    className="glass-card stat-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <span className="stat-icon">📊</span>
                    <div className="stat-content">
                        <span className="stat-value">{DEMO_SESSIONS.length}</span>
                        <span className="stat-label">총 분석 수</span>
                    </div>
                </motion.div>

                <motion.div
                    className="glass-card stat-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <span className="stat-icon">⭐</span>
                    <div className="stat-content">
                        <span className="stat-value">{avgScore}<small>점</small></span>
                        <span className="stat-label">평균 점수</span>
                    </div>
                </motion.div>

                <motion.div
                    className="glass-card stat-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <span className="stat-icon">🏆</span>
                    <div className="stat-content">
                        <span className="stat-value">{DEMO_SESSIONS[0]?.score}<small>점</small></span>
                        <span className="stat-label">최고 점수</span>
                    </div>
                </motion.div>

                <motion.div
                    className="glass-card stat-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                >
                    <span className="stat-icon">🎖️</span>
                    <div className="stat-content">
                        <span className="stat-value">{earnedBadges}/{totalBadges}</span>
                        <span className="stat-label">획득 배지</span>
                    </div>
                </motion.div>
            </section>

            {/* Tabs */}
            <div className="tabs">
                <button
                    className={`tab ${selectedTab === 'overview' ? 'active' : ''}`}
                    onClick={() => setSelectedTab('overview')}
                >
                    성장 추이
                </button>
                <button
                    className={`tab ${selectedTab === 'sessions' ? 'active' : ''}`}
                    onClick={() => setSelectedTab('sessions')}
                >
                    분석 기록
                </button>
                <button
                    className={`tab ${selectedTab === 'badges' ? 'active' : ''}`}
                    onClick={() => setSelectedTab('badges')}
                >
                    배지
                </button>
            </div>

            {/* Tab Content */}
            {selectedTab === 'overview' && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="tab-content"
                >
                    {/* Growth Chart */}
                    <div className="charts-grid">
                        <motion.div
                            className="glass-card"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <h3>📈 점수 성장 추이</h3>
                            <ResponsiveContainer width="100%" height={250}>
                                <LineChart data={GROWTH_DATA}>
                                    <XAxis
                                        dataKey="session"
                                        tick={{ fill: 'var(--color-text-muted)', fontSize: 12 }}
                                        tickFormatter={(v) => `#${v}`}
                                    />
                                    <YAxis
                                        domain={[50, 100]}
                                        tick={{ fill: 'var(--color-text-muted)', fontSize: 12 }}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            background: 'var(--color-bg-secondary)',
                                            border: '1px solid var(--glass-border)',
                                            borderRadius: '8px'
                                        }}
                                        formatter={(value) => [`${value}점`, '점수']}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="score"
                                        stroke="var(--color-accent-primary)"
                                        strokeWidth={3}
                                        dot={{ fill: 'var(--color-accent-primary)', strokeWidth: 2, r: 5 }}
                                        activeDot={{ r: 7, fill: 'var(--color-accent-secondary)' }}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </motion.div>

                        {/* Dimension Comparison */}
                        <motion.div
                            className="glass-card"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                        >
                            <h3>🎯 역량 비교 (첫 회 vs 최근)</h3>
                            <ResponsiveContainer width="100%" height={250}>
                                <RadarChart data={DIMENSION_COMPARE}>
                                    <PolarGrid stroke="rgba(255,255,255,0.1)" />
                                    <PolarAngleAxis
                                        dataKey="dimension"
                                        tick={{ fill: 'var(--color-text-secondary)', fontSize: 10 }}
                                    />
                                    <Radar
                                        name="첫 분석"
                                        dataKey="first"
                                        stroke="var(--color-warning)"
                                        fill="var(--color-warning)"
                                        fillOpacity={0.2}
                                    />
                                    <Radar
                                        name="최근"
                                        dataKey="latest"
                                        stroke="var(--color-success)"
                                        fill="var(--color-success)"
                                        fillOpacity={0.3}
                                    />
                                </RadarChart>
                            </ResponsiveContainer>
                            <div className="chart-legend">
                                <span className="legend-item">
                                    <span className="legend-dot" style={{ background: 'var(--color-warning)' }}></span>
                                    첫 분석
                                </span>
                                <span className="legend-item">
                                    <span className="legend-dot" style={{ background: 'var(--color-success)' }}></span>
                                    최근
                                </span>
                            </div>
                        </motion.div>
                    </div>
                </motion.div>
            )}

            {selectedTab === 'sessions' && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="tab-content"
                >
                    <div className="glass-card sessions-list">
                        <h3>📁 분석 기록</h3>
                        <div className="sessions-table">
                            <div className="table-header">
                                <span>날짜</span>
                                <span>영상</span>
                                <span>점수</span>
                                <span>등급</span>
                            </div>
                            {DEMO_SESSIONS.map((session, index) => (
                                <motion.div
                                    key={session.id}
                                    className="table-row"
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: 0.05 * index }}
                                >
                                    <span>{session.date}</span>
                                    <span className="video-name">{session.video}</span>
                                    <span className="score-cell">{session.score}점</span>
                                    <span className={`grade grade-${session.grade.charAt(0)}`}>
                                        {session.grade}
                                    </span>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </motion.div>
            )}

            {selectedTab === 'badges' && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="tab-content"
                >
                    <div className="badges-grid">
                        {DEMO_BADGES.map((badge, index) => (
                            <motion.div
                                key={badge.id}
                                className={`glass-card badge-card ${!badge.earned ? 'locked' : ''}`}
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: 0.05 * index }}
                                whileHover={{ scale: badge.earned ? 1.03 : 1 }}
                            >
                                <span className="badge-icon">{badge.icon}</span>
                                <h4>{badge.name}</h4>
                                <p>{badge.desc}</p>
                                {badge.earned && badge.date && (
                                    <span className="badge-date">획득: {badge.date}</span>
                                )}
                                {!badge.earned && (
                                    <span className="badge-locked">🔒 미획득</span>
                                )}
                            </motion.div>
                        ))}
                    </div>
                </motion.div>
            )}
        </div>
    )
}
