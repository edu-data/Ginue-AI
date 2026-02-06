# 🎓 GAIM Lab v3.0 - AI 기반 수업 분석 플랫폼

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Ginue AI** - 경인교육대학교의 혁신적인 AI 기반 마이크로티칭 분석 시스템

![GAIM Lab v3.0](https://img.shields.io/badge/GAIM_Lab-v3.0-purple?style=for-the-badge)

---

## 📋 목차

- [프로젝트 소개](#-프로젝트-소개)
- [주요 기능](#-주요-기능)
- [시스템 아키텍처](#-시스템-아키텍처)
- [7차원 평가 프레임워크](#-7차원-평가-프레임워크)
- [설치 방법](#-설치-방법)
- [사용 방법](#-사용-방법)
- [성능 벤치마크](#-성능-벤치마크)
- [라이선스](#-라이선스)

---

## 🎯 프로젝트 소개

**GAIM Lab v3.0**은 예비 교사의 수업 역량을 AI로 분석하고 개선하는 혁신적인 플랫폼입니다.
초등교사 임용고시 2차 수업 실연 평가 기준에 맞춘 **7차원 100점 평가 프레임워크**를 제공합니다.

### 핵심 가치

| 🎬 | 📊 | 🤖 | 📈 |
|:-:|:-:|:-:|:-:|
| **비전 분석** | **7차원 평가** | **AI 코칭** | **성장 추적** |
| 시선, 제스처, 자세 | 전문성 기반 점수 | 맞춤형 피드백 | 포트폴리오 관리 |

---

## ✨ 주요 기능

### 1. 🎥 비디오 분석

- **비전 분석**: 시선 추적, 제스처 인식, 자세 분석
- **음성 분석**: STT 기반 발화 분석, 속도/억양/습관어 탐지
- **감정 분석**: 표정 및 음성 감정 탐지

### 2. 📊 7차원 평가 시스템

- 초등교사 임용고시 2차 기준 적용
- 100점 만점 체계
- 강점/개선점 자동 분석

### 3. 🤖 AI 수업 코치

- Google Gemini 기반 대화형 코칭
- 개인화된 수업 개선 피드백
- 실전 수업 팁 제공

### 4. 📈 성장 포트폴리오

- 수업 역량 성장 추이 시각화
- 디지털 배지 시스템
- 분석 기록 관리

---

## 🏗️ 시스템 아키텍처

```
GAIM Lab v3.0
├── frontend/          # React 18 + Vite
│   ├── src/
│   │   ├── components/    # 재사용 컴포넌트
│   │   ├── pages/         # 페이지 컴포넌트
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Upload.jsx
│   │   │   ├── Analysis.jsx
│   │   │   ├── AICoach.jsx
│   │   │   └── Portfolio.jsx
│   │   └── index.css      # 글래스모피즘 디자인
│   └── package.json
├── backend/           # FastAPI
│   └── app/
│       ├── main.py
│       ├── api/v1/
│       │   ├── analysis.py
│       │   ├── chat.py
│       │   └── websocket.py
│       └── core/config.py
├── core/              # 분석 엔진
│   ├── analyzers/
│   │   ├── turbo_analyzer.py
│   │   ├── faster_whisper_stt.py
│   │   └── emotion_detector.py
│   └── config.py
├── scripts/           # 분석 스크립트
│   ├── batch_analysis.py
│   ├── demo_analysis.py
│   ├── enhanced_demo_analysis.py
│   └── benchmark.py
└── output/            # 분석 결과
```

### 기술 스택

| 구분 | 기술 |
|------|------|
| **Frontend** | React 18, Vite, Chart.js, Framer Motion |
| **Backend** | FastAPI, Python 3.10+, Uvicorn |
| **AI/ML** | Google Gemini API, FFmpeg |
| **Design** | Glassmorphism, CSS Variables |

---

## 📐 7차원 평가 프레임워크

초등교사 임용고시 2차 수업 시연 평가 기준 기반:

| 차원 | 평가 항목 | 배점 |
|:----:|:---------|:----:|
| 1️⃣ | **수업 전문성** - 교과 내용 이해, 정확한 설명 | 15점 |
| 2️⃣ | **교수학습 방법** - 다양한 교수 전략 활용 | 15점 |
| 3️⃣ | **판서 및 언어** - 명확한 발음, 적절한 속도 | 15점 |
| 4️⃣ | **수업 태도** - 자신감, 열정, 눈맞춤 | 15점 |
| 5️⃣ | **학생 참여 유도** - 질문, 상호작용, 피드백 | 15점 |
| 6️⃣ | **시간 배분** - 도입-전개-정리 균형 | 10점 |
| 7️⃣ | **창의성** - 독창적 교수법, 시각자료 활용 | 15점 |

---

## 🚀 설치 방법

### 사전 요구사항

- Python 3.10+
- Node.js 18+
- FFmpeg

### 1. 저장소 클론

```bash
git clone https://github.com/edu-data/Ginue-AI.git
cd Ginue-AI
```

### 2. 백엔드 설정

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# .env 파일에 GEMINI_API_KEY 설정
```

### 3. 프론트엔드 설정

```bash
cd frontend
npm install
```

### 4. 서버 실행

```bash
# 백엔드 (터미널 1)
cd backend
uvicorn app.main:app --reload --port 8000

# 프론트엔드 (터미널 2)
cd frontend
npm run dev
```

### 5. 접속

- **프론트엔드**: <http://localhost:5173>
- **API 문서**: <http://localhost:8000/docs>

---

## 📖 사용 방법

### 1. 영상 업로드

1. 대시보드에서 "새 분석 시작" 클릭
2. 수업 영상 파일 드래그앤드롭
3. 분석 시작

### 2. 분석 결과 확인

- 7차원 점수 및 등급 확인
- 강점/개선점 상세 피드백 확인
- 차원별 세부 분석 리뷰

### 3. AI 코치 활용

- 자유롭게 수업 관련 질문
- 빠른 액션 버튼 활용
- 맞춤형 피드백 받기

### 4. 포트폴리오 관리

- 성장 추이 그래프 확인
- 분석 기록 열람
- 획득 배지 확인

---

## ⚡ 성능 벤치마크

### 분석 성능

| 항목 | 결과 |
|------|------|
| **분석 속도** | 19.9x 실시간 |
| **15분 영상** | ~45초 분석 |
| **프레임 처리** | 9.96 fps |

### API 성능

| 항목 | 결과 |
|------|------|
| **API 응답** | ~2,060ms |
| **페이지 로딩** | 23ms 평균 |
| **동시 처리량** | 4.73 req/s |
| **성공률** | 100% |

---

## 📁 프로젝트 구조

```
d:\Ginue_AI
├── backend/           FastAPI 백엔드 서버
├── frontend/          React 프론트엔드
├── core/              분석 엔진 (TurboAnalyzer, STT, Emotion)
├── scripts/           배치 분석, 벤치마크 스크립트
├── output/            분석 결과 저장
├── .env.example       환경변수 템플릿
├── .gitignore         Git 제외 규칙
└── README.md          이 파일
```

---

## 📜 라이선스

MIT License © 2026 경인교육대학교 GAIM Lab

---

## 👥 개발팀

- **경인교육대학교 교육학과**
- AI 기반 교육 혁신 연구팀

---

<p align="center">
  <strong>🎓 GAIM Lab v3.0 - AI로 더 나은 수업을 만들어갑니다</strong>
</p>
