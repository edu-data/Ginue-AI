/**
 * 📊 Dashboard Page
 * Main overview with recent analyses and statistics
 */

import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
    BarChart, Bar, RadarChart, Radar, PolarGrid,
    PolarAngleAxis, XAxis, YAxis, Tooltip, ResponsiveContainer,
    PolarRadiusAxis
} from 'recharts'

// Demo data
const DEMO_STATS = {
    totalAnalyses: 18,
    averageScore: 77.1,
    bestScore: 84,
    completionRate: 100
}

const DEMO_RECENT = [
    { id: '1', name: '20251209_110545.mp4', score: 84, grade: 'A', date: '2025-12-09' },
    { id: '2', name: '20251209_143455.mp4', score: 81, grade: 'A', date: '2025-12-09' },
    { id: '3', name: '20251209_151833.mp4', score: 79, grade: 'B+', date: '2025-12-09' },
    { id: '4', name: '20251209_142648.mp4', score: 76, grade: 'B', date: '2025-12-09' },
]

const DEMO_DIMENSIONS = [
    { dimension: '수업 전문성', score: 16, maxScore: 20 },
    { dimension: '교수학습 방법', score: 15, maxScore: 20 },
    { dimension: '판서 및 언어', score: 12, maxScore: 15 },
    { dimension: '수업 태도', score: 11, maxScore: 15 },
    { dimension: '학생 참여', score: 10, maxScore: 15 },
    { dimension: '시간 배분', score: 7, maxScore: 10 },
    { dimension: '창의성', score: 3, maxScore: 5 },
]

const RADAR_DATA = DEMO_DIMENSIONS.map(d => ({
    subject: d.dimension.replace(' ', '\n'),
    value: (d.score / d.maxScore) * 100,
    fullMark: 100
}))

export default function Dashboard() {
    const [stats, setStats] = useState(DEMO_STATS)
    const [recentAnalyses, setRecentAnalyses] = useState(DEMO_RECENT)

    return (
        <div className="dashboard">
            <header className="page-header">
                <div>
                    <h1>📊 대시보드</h1>
                    <p>AI 수업 분석 현황을 한눈에 확인하세요</p>
                </div>
                <Link to="/upload" className="btn btn-primary btn-lg">
                    <span>🎬</span> 새 분석 시작
                </Link>
            </header>

            {/* Stats Cards */}
            <section className="stats-grid">
                <StatCard
                    icon="📈"
                    label="총 분석 수"
                    value={stats.totalAnalyses}
                    suffix="개"
                    color="var(--color-accent-primary)"
                />
                <StatCard
                    icon="⭐"
                    label="평균 점수"
                    value={stats.averageScore}
                    suffix="점"
                    color="var(--color-success)"
                />
                <StatCard
                    icon="🏆"
                    label="최고 점수"
                    value={stats.bestScore}
                    suffix="점"
                    color="var(--color-warning)"
                />
                <StatCard
                    icon="✅"
                    label="성공률"
                    value={stats.completionRate}
                    suffix="%"
                    color="var(--color-info)"
                />
            </section>

            {/* Charts Section */}
            <section className="charts-section">
                {/* Radar Chart */}
                <motion.div
                    className="glass-card chart-card"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 }}
                >
                    <h3>🎯 7차원 평균 역량</h3>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={300}>
                            <RadarChart data={RADAR_DATA}>
                                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                                <PolarAngleAxis
                                    dataKey="subject"
                                    tick={{ fill: 'var(--color-text-secondary)', fontSize: 11 }}
                                />
                                <PolarRadiusAxis
                                    angle={30}
                                    domain={[0, 100]}
                                    tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }}
                                />
                                <Radar
                                    name="점수"
                                    dataKey="value"
                                    stroke="var(--color-accent-primary)"
                                    fill="var(--color-accent-primary)"
                                    fillOpacity={0.3}
                                />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>

                {/* Bar Chart */}
                <motion.div
                    className="glass-card chart-card"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 }}
                >
                    <h3>📊 차원별 점수</h3>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={DEMO_DIMENSIONS} layout="vertical">
                                <XAxis type="number" domain={[0, 100]} tick={{ fill: 'var(--color-text-muted)' }} />
                                <YAxis
                                    type="category"
                                    dataKey="dimension"
                                    width={100}
                                    tick={{ fill: 'var(--color-text-secondary)', fontSize: 12 }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        background: 'var(--color-bg-secondary)',
                                        border: '1px solid var(--glass-border)',
                                        borderRadius: '8px'
                                    }}
                                    formatter={(value, name, props) => [
                                        `${props.payload.score}/${props.payload.maxScore}`,
                                        '점수'
                                    ]}
                                />
                                <Bar
                                    dataKey={(d) => (d.score / d.maxScore) * 100}
                                    fill="url(#barGradient)"
                                    radius={[0, 4, 4, 0]}
                                />
                                <defs>
                                    <linearGradient id="barGradient" x1="0" y1="0" x2="1" y2="0">
                                        <stop offset="0%" stopColor="var(--color-accent-primary)" />
                                        <stop offset="100%" stopColor="var(--color-accent-secondary)" />
                                    </linearGradient>
                                </defs>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>
            </section>

            {/* Recent Analyses */}
            <section className="recent-section">
                <motion.div
                    className="glass-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                >
                    <div className="section-header">
                        <h3>📁 최근 분석</h3>
                        <Link to="/portfolio" className="btn btn-secondary">
                            전체 보기 →
                        </Link>
                    </div>

                    <div className="analysis-list">
                        {recentAnalyses.map((analysis, index) => (
                            <motion.div
                                key={analysis.id}
                                className="analysis-item"
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.1 * index }}
                            >
                                <div className="analysis-info">
                                    <span className="analysis-name">{analysis.name}</span>
                                    <span className="analysis-date">{analysis.date}</span>
                                </div>
                                <div className="analysis-score">
                                    <span className={`grade grade-${analysis.grade.charAt(0)}`}>
                                        {analysis.grade}
                                    </span>
                                    <span className="score">{analysis.score}점</span>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </motion.div>
            </section>

            {/* Quick Actions */}
            <section className="quick-actions">
                <motion.div
                    className="glass-card action-card"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <Link to="/upload">
                        <span className="action-icon">📹</span>
                        <h4>영상 업로드</h4>
                        <p>새로운 수업 영상을 분석하세요</p>
                    </Link>
                </motion.div>

                <motion.div
                    className="glass-card action-card"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <Link to="/coach">
                        <span className="action-icon">🤖</span>
                        <h4>AI 코치</h4>
                        <p>맞춤형 수업 코칭을 받으세요</p>
                    </Link>
                </motion.div>

                <motion.div
                    className="glass-card action-card"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <Link to="/portfolio">
                        <span className="action-icon">📈</span>
                        <h4>포트폴리오</h4>
                        <p>성장 기록을 확인하세요</p>
                    </Link>
                </motion.div>
            </section>
        </div>
    )
}

// Stat Card Component
function StatCard({ icon, label, value, suffix, color }) {
    return (
        <motion.div
            className="glass-card stat-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.03 }}
        >
            <span className="stat-icon" style={{ color }}>{icon}</span>
            <div className="stat-content">
                <span className="stat-value">
                    {typeof value === 'number' ? value.toLocaleString() : value}
                    <small>{suffix}</small>
                </span>
                <span className="stat-label">{label}</span>
            </div>
        </motion.div>
    )
}
