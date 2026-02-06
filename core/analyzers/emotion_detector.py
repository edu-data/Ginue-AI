"""
😊 GAIM Lab v3.0 - Emotion Detector
교사/학생 표정 및 음성 감정 분석 모듈

Features:
- DeepFace 기반 표정 인식 (7가지 감정)
- 음성 감정 인식 (SER)
- 타임라인 기반 감정 추적
- 교실 분위기 종합 분석
"""

import os
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import Counter
import time

# Image processing
try:
    from PIL import Image
    import cv2
    IMAGING_AVAILABLE = True
except ImportError:
    IMAGING_AVAILABLE = False

# DeepFace for facial emotion
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False

# Audio processing
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False


@dataclass
class EmotionFrame:
    """단일 프레임/세그먼트 감정 데이터"""
    timestamp: float
    dominant_emotion: str
    emotion_scores: Dict[str, float]
    confidence: float = 0.0
    source: str = "face"  # "face" or "voice"


@dataclass
class EmotionTimeline:
    """감정 타임라인 분석 결과"""
    frames: List[EmotionFrame]
    summary: Dict[str, float]  # 감정별 비율
    positive_ratio: float
    negative_ratio: float
    neutral_ratio: float
    dominant_emotion: str
    mood_transitions: List[Dict]  # 분위기 변화 지점


# 감정 카테고리 분류
POSITIVE_EMOTIONS = ["happy", "surprise"]
NEGATIVE_EMOTIONS = ["sad", "angry", "fear", "disgust"]
NEUTRAL_EMOTIONS = ["neutral"]


class EmotionDetector:
    """
    😊 감정 분석기
    
    표정과 음성에서 감정을 추출하여 수업 분위기를 분석
    """
    
    # 감정 라벨 (한글)
    EMOTION_LABELS_KO = {
        "happy": "행복 😊",
        "sad": "슬픔 😢",
        "angry": "분노 😠",
        "fear": "공포 😨",
        "surprise": "놀람 😲",
        "disgust": "혐오 🤢",
        "neutral": "무표정 😐"
    }
    
    def __init__(
        self,
        face_detector: str = "opencv",
        analyze_voice: bool = True,
        segment_duration: float = 10.0
    ):
        """
        Args:
            face_detector: 얼굴 감지 백엔드 ("opencv", "retinaface", "mtcnn")
            analyze_voice: 음성 감정 분석 여부
            segment_duration: 타임라인 세그먼트 길이 (초)
        """
        self.face_detector = face_detector
        self.analyze_voice = analyze_voice
        self.segment_duration = segment_duration
        
        self._check_dependencies()
        
        print(f"😊 [EmotionDetector] 초기화: face_detector={face_detector}")
    
    def _check_dependencies(self):
        """의존성 확인"""
        if not IMAGING_AVAILABLE:
            print("   ⚠️ PIL/OpenCV not available")
        if not DEEPFACE_AVAILABLE:
            print("   ⚠️ DeepFace not available - facial emotion disabled")
        if not LIBROSA_AVAILABLE:
            print("   ⚠️ librosa not available - voice emotion disabled")
    
    def analyze_frame(self, image_path: str) -> Optional[EmotionFrame]:
        """
        단일 이미지에서 표정 분석
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            EmotionFrame 또는 None (얼굴 미감지 시)
        """
        if not DEEPFACE_AVAILABLE:
            return None
        
        try:
            # Analyze with DeepFace
            result = DeepFace.analyze(
                img_path=image_path,
                actions=["emotion"],
                detector_backend=self.face_detector,
                enforce_detection=False,
                silent=True
            )
            
            if isinstance(result, list):
                result = result[0]
            
            emotion_scores = result.get("emotion", {})
            dominant = result.get("dominant_emotion", "neutral")
            
            # Normalize scores to 0-1
            total = sum(emotion_scores.values())
            if total > 0:
                emotion_scores = {k: v / total for k, v in emotion_scores.items()}
            
            return EmotionFrame(
                timestamp=0.0,  # Will be set by caller
                dominant_emotion=dominant,
                emotion_scores=emotion_scores,
                confidence=emotion_scores.get(dominant, 0),
                source="face"
            )
            
        except Exception as e:
            return None
    
    def analyze_frames_batch(
        self, 
        frame_paths: List[str],
        timestamps: Optional[List[float]] = None
    ) -> List[EmotionFrame]:
        """
        여러 프레임 배치 분석
        
        Args:
            frame_paths: 프레임 이미지 경로 리스트
            timestamps: 각 프레임의 타임스탬프 (없으면 인덱스 사용)
            
        Returns:
            EmotionFrame 리스트
        """
        results = []
        
        for i, path in enumerate(frame_paths):
            frame = self.analyze_frame(path)
            
            if frame:
                frame.timestamp = timestamps[i] if timestamps else float(i)
                results.append(frame)
        
        return results
    
    def analyze_audio_emotion(
        self,
        audio_path: str,
        segment_duration: float = None
    ) -> List[EmotionFrame]:
        """
        오디오에서 음성 감정 분석
        
        간단한 특성 기반 감정 추론 (ML 모델 없이)
        - 에너지 높음 + 피치 높음 → happy/surprise
        - 에너지 낮음 → sad/neutral
        - 에너지 변동 큼 → angry
        
        Args:
            audio_path: 오디오 파일 경로
            segment_duration: 세그먼트 길이
            
        Returns:
            EmotionFrame 리스트
        """
        if not LIBROSA_AVAILABLE:
            return []
        
        segment_duration = segment_duration or self.segment_duration
        
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=16000)
            duration = len(y) / sr
            
            results = []
            n_segments = int(np.ceil(duration / segment_duration))
            
            for i in range(n_segments):
                start = int(i * segment_duration * sr)
                end = int(min((i + 1) * segment_duration * sr, len(y)))
                segment = y[start:end]
                
                if len(segment) < sr * 0.5:  # Skip very short segments
                    continue
                
                # Extract features
                energy = np.sqrt(np.mean(segment ** 2))
                energy_var = np.var(np.abs(segment))
                
                # Zero crossing rate (긴박함 지표)
                zcr = np.mean(librosa.feature.zero_crossing_rate(segment))
                
                # Spectral centroid (밝기)
                cent = np.mean(librosa.feature.spectral_centroid(y=segment, sr=sr))
                
                # Infer emotion from features
                emotion = self._infer_emotion_from_features(energy, energy_var, zcr, cent)
                
                results.append(EmotionFrame(
                    timestamp=i * segment_duration,
                    dominant_emotion=emotion["dominant"],
                    emotion_scores=emotion["scores"],
                    confidence=emotion["confidence"],
                    source="voice"
                ))
            
            return results
            
        except Exception as e:
            print(f"   ⚠️ Audio emotion analysis error: {e}")
            return []
    
    def _infer_emotion_from_features(
        self,
        energy: float,
        energy_var: float,
        zcr: float,
        centroid: float
    ) -> Dict:
        """특성 기반 감정 추론"""
        
        # Normalize features to 0-1 range (approximate)
        energy_norm = min(energy * 10, 1.0)
        var_norm = min(energy_var * 100, 1.0)
        zcr_norm = min(zcr * 5, 1.0)
        cent_norm = min(centroid / 4000, 1.0)
        
        # Simple rule-based inference
        scores = {
            "happy": 0.0,
            "sad": 0.0,
            "angry": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "disgust": 0.0,
            "neutral": 0.3
        }
        
        # High energy + high pitch → happy/excited
        if energy_norm > 0.6 and cent_norm > 0.5:
            scores["happy"] = 0.5 + energy_norm * 0.3
            scores["surprise"] = 0.3
        
        # Low energy → sad
        elif energy_norm < 0.3:
            scores["sad"] = 0.4 + (1 - energy_norm) * 0.3
            scores["neutral"] = 0.3
        
        # High variance → angry/excited
        elif var_norm > 0.5:
            scores["angry"] = 0.4 + var_norm * 0.3
        
        # High ZCR → nervous
        elif zcr_norm > 0.6:
            scores["fear"] = 0.3
            scores["surprise"] = 0.3
        
        else:
            scores["neutral"] = 0.6
        
        # Normalize
        total = sum(scores.values())
        scores = {k: v / total for k, v in scores.items()}
        
        dominant = max(scores, key=scores.get)
        
        return {
            "dominant": dominant,
            "scores": scores,
            "confidence": scores[dominant]
        }
    
    def build_timeline(
        self,
        face_frames: List[EmotionFrame],
        voice_frames: Optional[List[EmotionFrame]] = None
    ) -> EmotionTimeline:
        """
        감정 타임라인 구축
        
        Args:
            face_frames: 표정 기반 감정
            voice_frames: 음성 기반 감정 (선택)
            
        Returns:
            EmotionTimeline 객체
        """
        all_frames = list(face_frames)
        if voice_frames:
            all_frames.extend(voice_frames)
        
        # Sort by timestamp
        all_frames.sort(key=lambda x: x.timestamp)
        
        if not all_frames:
            return EmotionTimeline(
                frames=[],
                summary={},
                positive_ratio=0.0,
                negative_ratio=0.0,
                neutral_ratio=0.0,
                dominant_emotion="neutral",
                mood_transitions=[]
            )
        
        # Calculate emotion distribution
        emotions = [f.dominant_emotion for f in all_frames]
        emotion_counts = Counter(emotions)
        total = len(emotions)
        
        summary = {k: v / total for k, v in emotion_counts.items()}
        
        # Calculate sentiment ratios
        positive_ratio = sum(summary.get(e, 0) for e in POSITIVE_EMOTIONS)
        negative_ratio = sum(summary.get(e, 0) for e in NEGATIVE_EMOTIONS)
        neutral_ratio = sum(summary.get(e, 0) for e in NEUTRAL_EMOTIONS)
        
        # Find dominant
        dominant = emotion_counts.most_common(1)[0][0]
        
        # Detect mood transitions
        transitions = self._detect_transitions(all_frames)
        
        return EmotionTimeline(
            frames=all_frames,
            summary=summary,
            positive_ratio=positive_ratio,
            negative_ratio=negative_ratio,
            neutral_ratio=neutral_ratio,
            dominant_emotion=dominant,
            mood_transitions=transitions
        )
    
    def _detect_transitions(
        self,
        frames: List[EmotionFrame],
        min_duration: float = 5.0
    ) -> List[Dict]:
        """분위기 변화 지점 감지"""
        transitions = []
        
        if len(frames) < 2:
            return transitions
        
        prev_emotion = frames[0].dominant_emotion
        prev_category = self._get_category(prev_emotion)
        segment_start = frames[0].timestamp
        
        for frame in frames[1:]:
            curr_category = self._get_category(frame.dominant_emotion)
            
            if curr_category != prev_category:
                duration = frame.timestamp - segment_start
                if duration >= min_duration:
                    transitions.append({
                        "timestamp": frame.timestamp,
                        "from_mood": prev_category,
                        "to_mood": curr_category,
                        "from_emotion": prev_emotion,
                        "to_emotion": frame.dominant_emotion
                    })
                
                prev_category = curr_category
                prev_emotion = frame.dominant_emotion
                segment_start = frame.timestamp
        
        return transitions
    
    def _get_category(self, emotion: str) -> str:
        """감정 카테고리 반환"""
        if emotion in POSITIVE_EMOTIONS:
            return "positive"
        elif emotion in NEGATIVE_EMOTIONS:
            return "negative"
        return "neutral"
    
    def analyze_classroom_mood(
        self,
        frame_dir: str,
        audio_path: Optional[str] = None
    ) -> Dict:
        """
        교실 전체 분위기 종합 분석
        
        Args:
            frame_dir: 프레임 이미지 디렉토리
            audio_path: 오디오 파일 경로 (선택)
            
        Returns:
            종합 분석 결과 딕셔너리
        """
        frame_dir = Path(frame_dir)
        
        # Get all frames
        frame_paths = sorted(frame_dir.glob("*.jpg")) + sorted(frame_dir.glob("*.png"))
        timestamps = [float(i) for i in range(len(frame_paths))]
        
        print(f"😊 [EmotionDetector] 분석 시작: {len(frame_paths)} 프레임")
        
        # Analyze faces
        start_time = time.time()
        face_frames = self.analyze_frames_batch(
            [str(p) for p in frame_paths],
            timestamps
        )
        
        # Analyze voice if available
        voice_frames = []
        if audio_path and self.analyze_voice:
            voice_frames = self.analyze_audio_emotion(audio_path)
        
        # Build timeline
        timeline = self.build_timeline(face_frames, voice_frames)
        
        elapsed = time.time() - start_time
        
        result = {
            "timeline": timeline,
            "summary": {
                "dominant_emotion": timeline.dominant_emotion,
                "dominant_emotion_ko": self.EMOTION_LABELS_KO.get(
                    timeline.dominant_emotion, timeline.dominant_emotion
                ),
                "positive_ratio": timeline.positive_ratio,
                "negative_ratio": timeline.negative_ratio,
                "neutral_ratio": timeline.neutral_ratio,
                "emotion_distribution": timeline.summary,
                "mood_transitions_count": len(timeline.mood_transitions),
                "frames_analyzed": len(face_frames),
                "processing_time": elapsed
            },
            "recommendations": self._generate_recommendations(timeline)
        }
        
        print(f"   ✅ 분석 완료: 주요 감정={timeline.dominant_emotion}, "
              f"긍정={timeline.positive_ratio:.1%}, "
              f"부정={timeline.negative_ratio:.1%}")
        
        return result
    
    def _generate_recommendations(self, timeline: EmotionTimeline) -> List[str]:
        """감정 분석 기반 개선 권장사항 생성"""
        recommendations = []
        
        if timeline.negative_ratio > 0.3:
            recommendations.append(
                "😟 부정적 감정 비율이 높습니다. 더 밝고 활기찬 표현을 연습해 보세요."
            )
        
        if timeline.neutral_ratio > 0.6:
            recommendations.append(
                "😐 무표정이 많습니다. 학생들과의 상호작용에서 더 다양한 감정을 표현해 보세요."
            )
        
        if timeline.positive_ratio > 0.5:
            recommendations.append(
                "😊 긍정적인 분위기가 잘 유지되고 있습니다. 훌륭합니다!"
            )
        
        if len(timeline.mood_transitions) > 5:
            recommendations.append(
                "🎭 감정 변화가 빈번합니다. 일관된 분위기 유지를 연습해 보세요."
            )
        
        return recommendations


# CLI test
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        
        detector = EmotionDetector()
        
        if path.is_dir():
            result = detector.analyze_classroom_mood(str(path))
            print(f"\n📊 분석 결과:")
            print(f"   주요 감정: {result['summary']['dominant_emotion_ko']}")
            print(f"   긍정: {result['summary']['positive_ratio']:.1%}")
            print(f"   부정: {result['summary']['negative_ratio']:.1%}")
            print(f"   중립: {result['summary']['neutral_ratio']:.1%}")
            print(f"\n💡 권장사항:")
            for rec in result['recommendations']:
                print(f"   {rec}")
        else:
            frame = detector.analyze_frame(str(path))
            if frame:
                print(f"감정: {frame.dominant_emotion}")
                print(f"점수: {frame.emotion_scores}")
    else:
        print("Usage: python emotion_detector.py <frame_dir_or_image>")
