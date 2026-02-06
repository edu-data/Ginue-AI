/**
 * 🤖 AI Coach Page
 * Interactive chat with AI teaching coach
 */

import { useState, useRef, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

import './AICoach.css'

const SUGGESTION_QUESTIONS = [
    '이번 수업에서 어떤 점을 개선할 수 있을까요?',
    '효과적인 발문 기법을 알려주세요',
    '학생 참여를 높이는 방법은?',
    '시간 배분을 어떻게 개선할 수 있나요?',
    '습관어를 줄이는 방법을 알려주세요',
]

export default function AICoach() {
    const [searchParams] = useSearchParams()
    const analysisId = searchParams.get('analysis')

    const [messages, setMessages] = useState([
        {
            id: '1',
            role: 'assistant',
            content: '안녕하세요! 저는 GAIM Lab의 AI 수업 코치입니다. 🎓\n\n수업 분석 결과에 대한 질문이나, 수업 역량 향상을 위한 조언이 필요하시면 언제든 물어보세요!\n\n어떤 도움이 필요하신가요?',
            timestamp: new Date().toISOString()
        }
    ])
    const [inputValue, setInputValue] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [sessionId, setSessionId] = useState(null)
    const [suggestions, setSuggestions] = useState(SUGGESTION_QUESTIONS.slice(0, 3))

    const messagesEndRef = useRef(null)
    const inputRef = useRef(null)

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    const sendMessage = async (messageText) => {
        if (!messageText.trim() || isLoading) return

        const userMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: messageText,
            timestamp: new Date().toISOString()
        }

        setMessages(prev => [...prev, userMessage])
        setInputValue('')
        setIsLoading(true)
        setSuggestions([])

        try {
            const response = await fetch('/api/v1/chat/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    message: messageText,
                    analysis_id: analysisId
                })
            })

            if (!response.ok) {
                throw new Error('응답 생성 실패')
            }

            const data = await response.json()

            setSessionId(data.session_id)

            const assistantMessage = {
                id: Date.now().toString() + '-assistant',
                role: 'assistant',
                content: data.message.content,
                timestamp: data.message.timestamp
            }

            setMessages(prev => [...prev, assistantMessage])
            setSuggestions(data.suggestions || [])

        } catch (err) {
            // Fallback response
            const fallbackMessage = {
                id: Date.now().toString() + '-assistant',
                role: 'assistant',
                content: generateFallbackResponse(messageText),
                timestamp: new Date().toISOString()
            }

            setMessages(prev => [...prev, fallbackMessage])
            setSuggestions(SUGGESTION_QUESTIONS.slice(0, 3))
        } finally {
            setIsLoading(false)
        }
    }

    const generateFallbackResponse = (question) => {
        const responses = {
            '발문': '효과적인 발문 기법으로는:\n\n1. **개방형 질문 활용**: "왜 그렇게 생각하나요?" 같은 질문으로 사고를 확장시키세요.\n2. **대기 시간 확보**: 질문 후 3-5초 기다려 학생들이 생각할 시간을 주세요.\n3. **연쇄 질문**: 학생 답변에 이어지는 후속 질문으로 심화 학습을 유도하세요.',
            '참여': '학생 참여를 높이려면:\n\n1. **짝토의/모둠활동**: 모든 학생이 발언 기회를 갖도록 합니다.\n2. **Think-Pair-Share**: 개별 사고 → 짝 토의 → 전체 공유\n3. **실시간 피드백**: 학생 반응에 즉각적으로 반응해 주세요.',
            '시간': '시간 배분 개선 방법:\n\n1. **도입 5분, 전개 30분, 정리 10분** 기본 틀을 유지하세요.\n2. **타이머 활용**: 각 활동에 시간을 할당하세요.\n3. **우선순위 설정**: 핵심 내용에 집중하고 부가 내용은 유연하게 조절하세요.',
            '습관어': '습관어를 줄이려면:\n\n1. **녹화 분석**: 자신의 수업을 녹화해서 습관어를 파악하세요.\n2. **의도적 멈춤**: 습관어 대신 잠시 멈추는 연습을 하세요.\n3. **연습, 연습**: 발표 연습을 통해 의식적으로 개선하세요.',
            'default': '좋은 질문입니다! 수업 역량 향상을 위해 몇 가지 팁을 드릴게요:\n\n1. **자기 분석**: 정기적으로 수업을 녹화하고 분석해 보세요.\n2. **동료 피드백**: 동료 교사의 수업을 참관하고 피드백을 나누세요.\n3. **교육 이론 학습**: 최신 교수법을 지속적으로 학습하세요.\n\n더 구체적인 질문이 있으시면 말씀해 주세요!'
        }

        for (const [keyword, response] of Object.entries(responses)) {
            if (question.includes(keyword)) {
                return response
            }
        }

        return responses.default
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage(inputValue)
        }
    }

    const handleSuggestionClick = (suggestion) => {
        sendMessage(suggestion)
    }

    return (
        <div className="coach-page">
            <header className="coach-header glass-card">
                <div className="coach-info">
                    <span className="coach-avatar">🤖</span>
                    <div>
                        <h1>AI 수업 코치</h1>
                        <p>맞춤형 수업 코칭 & 피드백</p>
                    </div>
                </div>
                {analysisId && (
                    <span className="analysis-badge">
                        📊 분석 #{analysisId} 연결됨
                    </span>
                )}
            </header>

            <div className="chat-container glass-card">
                <div className="messages-container">
                    <AnimatePresence>
                        {messages.map((message) => (
                            <motion.div
                                key={message.id}
                                className={`message ${message.role}`}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                            >
                                {message.role === 'assistant' && (
                                    <span className="message-avatar">🤖</span>
                                )}
                                <div className="message-content">
                                    <div className="message-text">
                                        {message.content.split('\n').map((line, i) => (
                                            <p key={i}>{line}</p>
                                        ))}
                                    </div>
                                    <span className="message-time">
                                        {new Date(message.timestamp).toLocaleTimeString('ko-KR', {
                                            hour: '2-digit',
                                            minute: '2-digit'
                                        })}
                                    </span>
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {isLoading && (
                        <motion.div
                            className="message assistant"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                        >
                            <span className="message-avatar">🤖</span>
                            <div className="message-content">
                                <div className="typing-indicator">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Suggestions */}
                {suggestions.length > 0 && !isLoading && (
                    <div className="suggestions">
                        {suggestions.map((suggestion, index) => (
                            <motion.button
                                key={index}
                                className="suggestion-chip"
                                onClick={() => handleSuggestionClick(suggestion)}
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: 0.1 * index }}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                            >
                                {suggestion}
                            </motion.button>
                        ))}
                    </div>
                )}

                {/* Input */}
                <div className="input-container">
                    <textarea
                        ref={inputRef}
                        className="chat-input"
                        placeholder="질문을 입력하세요..."
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        rows={1}
                        disabled={isLoading}
                    />
                    <button
                        className="send-button btn btn-primary"
                        onClick={() => sendMessage(inputValue)}
                        disabled={!inputValue.trim() || isLoading}
                    >
                        <span>전송</span>
                        <span>➤</span>
                    </button>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="quick-actions">
                <motion.button
                    className="glass-card quick-action"
                    onClick={() => handleSuggestionClick('이번 수업의 강점은 무엇인가요?')}
                    whileHover={{ scale: 1.02 }}
                >
                    <span>💪</span>
                    <span>강점 분석</span>
                </motion.button>
                <motion.button
                    className="glass-card quick-action"
                    onClick={() => handleSuggestionClick('개선이 필요한 부분을 알려주세요')}
                    whileHover={{ scale: 1.02 }}
                >
                    <span>📈</span>
                    <span>개선점 분석</span>
                </motion.button>
                <motion.button
                    className="glass-card quick-action"
                    onClick={() => handleSuggestionClick('다음 수업에서 바로 적용할 수 있는 팁을 주세요')}
                    whileHover={{ scale: 1.02 }}
                >
                    <span>💡</span>
                    <span>실전 팁</span>
                </motion.button>
            </div>
        </div>
    )
}
