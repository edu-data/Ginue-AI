/**
 * 🚀 GAIM Lab v3.0 - Main App Component
 */

import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'

// Pages
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import Analysis from './pages/Analysis'
import AICoach from './pages/AICoach'
import Portfolio from './pages/Portfolio'

import './App.css'

function App() {
    return (
        <BrowserRouter>
            <div className="app">
                {/* Navigation */}
                <nav className="nav">
                    <NavLink to="/" className="nav-brand">
                        <span className="nav-logo">🎓</span>
                        <span>GAIM Lab</span>
                        <span className="nav-version">v3.0</span>
                    </NavLink>

                    <ul className="nav-links">
                        <li>
                            <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                                대시보드
                            </NavLink>
                        </li>
                        <li>
                            <NavLink to="/upload" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                                영상 업로드
                            </NavLink>
                        </li>
                        <li>
                            <NavLink to="/coach" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                                AI 코치
                            </NavLink>
                        </li>
                        <li>
                            <NavLink to="/portfolio" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                                포트폴리오
                            </NavLink>
                        </li>
                    </ul>
                </nav>

                {/* Main Content */}
                <main className="main-content">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4 }}
                    >
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/upload" element={<Upload />} />
                            <Route path="/analysis/:id" element={<Analysis />} />
                            <Route path="/coach" element={<AICoach />} />
                            <Route path="/portfolio" element={<Portfolio />} />
                        </Routes>
                    </motion.div>
                </main>

                {/* Footer */}
                <footer className="footer">
                    <div className="footer-content">
                        <span>© 2026 경인교육대학교 GAIM Lab</span>
                        <span className="footer-divider">|</span>
                        <span>AI 기반 수업 분석 플랫폼</span>
                    </div>
                </footer>
            </div>
        </BrowserRouter>
    )
}

export default App
