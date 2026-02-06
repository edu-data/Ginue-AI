"""
⚡ GAIM Lab v3.0 - Faster-Whisper STT
Whisper 대비 3배 빠른 음성 인식 엔진

Features:
- CUDA 가속 지원
- 실시간 스트리밍 모드
- 한국어 최적화
- 세그먼트별 타임스탬프
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import time

# Try faster-whisper first, fallback to whisper
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


@dataclass
class TranscriptSegment:
    """음성 인식 세그먼트"""
    start: float
    end: float
    text: str
    confidence: float = 1.0
    words: List[Dict] = field(default_factory=list)


@dataclass
class TranscriptionResult:
    """전사 결과"""
    text: str
    segments: List[TranscriptSegment]
    language: str
    duration: float
    processing_time: float
    filler_words: Dict[str, int] = field(default_factory=dict)


class FasterWhisperSTT:
    """
    ⚡ 초고속 음성 인식 엔진
    
    Faster-Whisper를 사용하여 Whisper 대비 3배 빠른 STT 수행
    """
    
    # Korean filler words to detect
    FILLER_WORDS_KO = [
        "음", "어", "그", "이제", "뭐", "그래서", "아", "에", 
        "그러니까", "일단", "막", "좀", "근데", "저기"
    ]
    
    def __init__(
        self,
        model_size: str = "small",
        language: str = "ko",
        compute_type: str = "float16",
        device: str = "auto"
    ):
        """
        Args:
            model_size: 모델 크기 ("tiny", "base", "small", "medium", "large")
            language: 언어 코드 ("ko", "en" 등)
            compute_type: 연산 타입 ("float16", "int8", "float32")
            device: 장치 ("cuda", "cpu", "auto")
        """
        self.model_size = model_size
        self.language = language
        self.compute_type = compute_type
        self.device = self._detect_device() if device == "auto" else device
        
        self._model = None
        self._fallback_model = None
        
        print(f"🎤 [FasterWhisperSTT] 초기화: model={model_size}, lang={language}, device={self.device}")
    
    def _detect_device(self) -> str:
        """CUDA 사용 가능 여부 확인"""
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"
    
    def _load_model(self):
        """모델 로드 (지연 로딩)"""
        if self._model is not None:
            return
        
        if FASTER_WHISPER_AVAILABLE:
            print(f"   📦 Faster-Whisper 모델 로딩: {self.model_size}")
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
        elif WHISPER_AVAILABLE:
            print(f"   📦 OpenAI Whisper 모델 로딩 (fallback): {self.model_size}")
            self._fallback_model = whisper.load_model(self.model_size)
        else:
            raise ImportError("faster-whisper 또는 whisper 중 하나가 필요합니다")
    
    def transcribe_audio(self, audio_path: str) -> TranscriptionResult:
        """
        오디오 파일 전사
        
        Args:
            audio_path: 오디오 파일 경로 (WAV 권장)
            
        Returns:
            TranscriptionResult 객체
        """
        start_time = time.time()
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        self._load_model()
        
        if FASTER_WHISPER_AVAILABLE and self._model:
            result = self._transcribe_faster(audio_path)
        else:
            result = self._transcribe_whisper(audio_path)
        
        result.processing_time = time.time() - start_time
        result.filler_words = self._detect_filler_words(result.text)
        
        print(f"   ✅ STT 완료: {len(result.text)}자, {len(result.segments)}개 세그먼트, {result.processing_time:.1f}초")
        
        return result
    
    def _transcribe_faster(self, audio_path: Path) -> TranscriptionResult:
        """Faster-Whisper로 전사"""
        segments_iter, info = self._model.transcribe(
            str(audio_path),
            language=self.language,
            word_timestamps=True,
            vad_filter=True,  # Voice activity detection
            vad_parameters=dict(
                min_silence_duration_ms=500,
                speech_pad_ms=200
            )
        )
        
        segments = []
        full_text = []
        
        for seg in segments_iter:
            segment = TranscriptSegment(
                start=seg.start,
                end=seg.end,
                text=seg.text.strip(),
                confidence=seg.avg_logprob if hasattr(seg, 'avg_logprob') else 1.0
            )
            
            # Extract word-level timestamps if available
            if hasattr(seg, 'words') and seg.words:
                segment.words = [
                    {"word": w.word, "start": w.start, "end": w.end}
                    for w in seg.words
                ]
            
            segments.append(segment)
            full_text.append(seg.text.strip())
        
        return TranscriptionResult(
            text=" ".join(full_text),
            segments=segments,
            language=info.language,
            duration=info.duration,
            processing_time=0.0  # Will be set later
        )
    
    def _transcribe_whisper(self, audio_path: Path) -> TranscriptionResult:
        """OpenAI Whisper로 전사 (폴백)"""
        result = self._fallback_model.transcribe(
            str(audio_path),
            language=self.language
        )
        
        segments = []
        for seg in result.get("segments", []):
            segments.append(TranscriptSegment(
                start=seg["start"],
                end=seg["end"],
                text=seg["text"].strip()
            ))
        
        # Calculate duration from last segment
        duration = segments[-1].end if segments else 0.0
        
        return TranscriptionResult(
            text=result.get("text", ""),
            segments=segments,
            language=self.language,
            duration=duration,
            processing_time=0.0
        )
    
    def _detect_filler_words(self, text: str) -> Dict[str, int]:
        """습관어(군더더기 말) 감지"""
        filler_counts = {}
        
        # Simple word-based detection
        words = text.split()
        
        for filler in self.FILLER_WORDS_KO:
            count = sum(1 for w in words if filler in w)
            if count > 0:
                filler_counts[filler] = count
        
        return filler_counts
    
    def transcribe_video(self, video_path: str) -> TranscriptionResult:
        """
        비디오 파일에서 오디오 추출 후 전사
        
        Args:
            video_path: 비디오 파일 경로
            
        Returns:
            TranscriptionResult 객체
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Extract audio to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio_path = temp_audio.name
        
        try:
            print(f"   🎬 영상에서 오디오 추출 중...")
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-ar", "16000",
                "-ac", "1",
                "-acodec", "pcm_s16le",
                temp_audio_path,
                "-loglevel", "error"
            ]
            subprocess.run(cmd, check=True)
            
            return self.transcribe_audio(temp_audio_path)
            
        finally:
            # Cleanup temp file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
    
    def get_speech_segments_with_timestamps(
        self, 
        audio_path: str
    ) -> List[Dict]:
        """
        발화 구간과 타임스탬프 반환 (타임라인 마커용)
        
        Returns:
            [{"start": 0.0, "end": 5.2, "text": "...", "type": "speech"}, ...]
        """
        result = self.transcribe_audio(audio_path)
        
        markers = []
        for seg in result.segments:
            markers.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text,
                "type": "speech",
                "confidence": seg.confidence
            })
            
            # Mark filler words
            for filler in self.FILLER_WORDS_KO:
                if filler in seg.text:
                    markers.append({
                        "start": seg.start,
                        "end": seg.end,
                        "text": f"습관어 감지: '{filler}'",
                        "type": "filler_word"
                    })
        
        return markers


# CLI test
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        audio_or_video = Path(sys.argv[1])
        
        stt = FasterWhisperSTT(model_size="small", language="ko")
        
        if audio_or_video.suffix.lower() in [".mp4", ".avi", ".mov", ".mkv"]:
            result = stt.transcribe_video(str(audio_or_video))
        else:
            result = stt.transcribe_audio(str(audio_or_video))
        
        print(f"\n📝 전사 결과:")
        print(f"   텍스트 길이: {len(result.text)}자")
        print(f"   세그먼트 수: {len(result.segments)}")
        print(f"   처리 시간: {result.processing_time:.1f}초")
        print(f"   습관어: {result.filler_words}")
        print(f"\n--- 처음 500자 ---")
        print(result.text[:500])
    else:
        print("Usage: python faster_whisper_stt.py <audio_or_video_path>")
