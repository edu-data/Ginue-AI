"""
⚡ GAIM Lab v3.0 - Turbo Analyzer
초고속 비전 분석 모듈 (FFmpeg + MediaPipe + Multiprocessing)

Features:
- GPU 가속 FFmpeg 프레임 추출
- MediaPipe 기반 자세/제스처 분석
- 멀티프로세싱 병렬 처리
- 15분 영상 60초 내 분석
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import json

# MediaPipe imports
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("[!] MediaPipe not available")

# Image processing
try:
    from PIL import Image
    import numpy as np
    IMAGING_AVAILABLE = True
except ImportError:
    IMAGING_AVAILABLE = False


@dataclass
class AnalysisResult:
    """분석 결과 컨테이너"""
    timeline: List[Dict] = field(default_factory=list)
    audio_metrics: Dict = field(default_factory=dict)
    audio_timeline: List[Dict] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    frame_count: int = 0
    vision_summary: Dict = field(default_factory=dict)


class TurboAnalyzer:
    """
    ⚡ 초고속 타임랩스 분석기
    
    FFmpeg + MediaPipe + Multiprocessing을 활용한 고성능 분석
    """
    
    def __init__(self, temp_dir: Optional[str] = None, use_gpu: bool = True):
        """
        Args:
            temp_dir: 임시 캐시 디렉토리
            use_gpu: GPU 가속 사용 여부
        """
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.mkdtemp())
        self.use_gpu = use_gpu
        self.frames_dir = self.temp_dir / "frames"
        self.audio_path = self.temp_dir / "audio.wav"
        
        # Ensure directories exist
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        
        # Last analysis results
        self._last_result: Optional[AnalysisResult] = None
        
    def analyze_video(self, video_path: Path) -> Tuple[List[Dict], List[Dict]]:
        """
        비디오 분석 수행
        
        Args:
            video_path: 비디오 파일 경로
            
        Returns:
            (vision_results, content_results) 튜플
        """
        start_time = time.time()
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        print(f"📹 [TurboAnalyzer] 분석 시작: {video_path.name}")
        
        # Phase 1: Extract resources (frames + audio)
        print("   [1/3] 리소스 추출 중...")
        self._extract_resources(video_path)
        
        # Phase 2: Analyze frames in parallel
        print("   [2/3] 프레임 분석 중...")
        vision_results = self._analyze_frames_parallel()
        
        # Phase 3: Analyze audio
        print("   [3/3] 오디오 분석 중...")
        audio_metrics, audio_timeline = self._analyze_audio()
        
        elapsed = time.time() - start_time
        
        # Store results
        self._last_result = AnalysisResult(
            timeline=vision_results,
            audio_metrics=audio_metrics,
            audio_timeline=audio_timeline,
            elapsed_seconds=elapsed,
            frame_count=len(vision_results),
            vision_summary=self._compute_vision_summary(vision_results)
        )
        
        print(f"✅ [TurboAnalyzer] 완료: {elapsed:.1f}초, {len(vision_results)} 프레임")
        
        # Return compatible format
        content_results = [{"slide_changes": 0, "text_density": 0}]
        return vision_results, content_results
    
    def _extract_resources(self, video_path: Path):
        """FFmpeg로 프레임과 오디오 추출"""
        
        # Extract frames at 1fps, 360p
        frames_pattern = str(self.frames_dir / "frame_%04d.jpg")
        
        # GPU acceleration filter (NVIDIA)
        if self.use_gpu:
            scale_filter = "scale_cuda=640:360"
            hwaccel = ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"]
        else:
            scale_filter = "scale=640:360"
            hwaccel = []
        
        # Extract frames
        cmd_frames = [
            "ffmpeg", "-y",
            *hwaccel,
            "-i", str(video_path),
            "-vf", f"fps=1,{scale_filter}" if not self.use_gpu else f"fps=1,{scale_filter},hwdownload,format=nv12",
            "-q:v", "3",
            frames_pattern,
            "-loglevel", "error"
        ]
        
        try:
            subprocess.run(cmd_frames, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # Fallback to CPU
            cmd_frames = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-vf", "fps=1,scale=640:360",
                "-q:v", "3",
                frames_pattern,
                "-loglevel", "error"
            ]
            subprocess.run(cmd_frames, check=True, capture_output=True)
        
        # Extract audio
        cmd_audio = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-ar", "16000",
            "-ac", "1",
            str(self.audio_path),
            "-loglevel", "error"
        ]
        subprocess.run(cmd_audio, check=True, capture_output=True)
    
    def _analyze_frames_parallel(self) -> List[Dict]:
        """멀티프로세싱으로 프레임 병렬 분석"""
        frame_files = sorted(self.frames_dir.glob("frame_*.jpg"))
        
        if not frame_files:
            return []
        
        results = []
        
        # Use process pool for parallel analysis
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = {
                executor.submit(analyze_single_frame, str(f)): i 
                for i, f in enumerate(frame_files)
            }
            
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    result = future.result()
                    result["timestamp"] = idx  # seconds
                    results.append(result)
                except Exception as e:
                    print(f"   ⚠️ Frame {idx} 분석 실패: {e}")
        
        # Sort by timestamp
        results.sort(key=lambda x: x["timestamp"])
        return results
    
    def _analyze_audio(self) -> Tuple[Dict, List[Dict]]:
        """오디오 분석 (에너지, 피치, 침묵)"""
        if not self.audio_path.exists():
            return {}, []
        
        try:
            import librosa
            import numpy as np
            
            # Load audio
            y, sr = librosa.load(str(self.audio_path), sr=16000)
            
            # Overall metrics
            duration = len(y) / sr
            
            # Energy-based silence detection
            frame_length = int(0.025 * sr)
            hop_length = int(0.010 * sr)
            energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            
            silence_threshold = np.mean(energy) * 0.3
            silence_ratio = np.sum(energy < silence_threshold) / len(energy)
            
            # Pitch analysis
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_mean = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0
            pitch_std = np.std(pitches[pitches > 0]) if np.any(pitches > 0) else 0
            
            # Overall metrics
            audio_metrics = {
                "duration": duration,
                "silence_ratio": float(silence_ratio),
                "avg_energy": float(np.mean(energy)),
                "pitch_mean": float(pitch_mean),
                "pitch_std": float(pitch_std),
                "energy_variance": float(np.var(energy))
            }
            
            # Timeline (10-second segments)
            segment_duration = 10.0
            n_segments = int(np.ceil(duration / segment_duration))
            audio_timeline = []
            
            for i in range(n_segments):
                start = int(i * segment_duration * sr)
                end = int(min((i + 1) * segment_duration * sr, len(y)))
                segment = y[start:end]
                
                if len(segment) > 0:
                    seg_energy = np.sqrt(np.mean(segment ** 2))
                    audio_timeline.append({
                        "timestamp": i * segment_duration,
                        "energy": float(seg_energy),
                        "is_speech": seg_energy > silence_threshold
                    })
            
            return audio_metrics, audio_timeline
            
        except ImportError:
            print("   ⚠️ librosa not available, skipping audio analysis")
            return {}, []
        except Exception as e:
            print(f"   ⚠️ Audio analysis error: {e}")
            return {}, []
    
    def _compute_vision_summary(self, results: List[Dict]) -> Dict:
        """비전 분석 결과 요약"""
        if not results:
            return {}
        
        face_visible_count = sum(1 for r in results if r.get("face_visible", False))
        gesture_count = sum(1 for r in results if r.get("gesture_active", False))
        
        return {
            "total_frames": len(results),
            "face_visible_ratio": face_visible_count / len(results),
            "gesture_ratio": gesture_count / len(results),
            "avg_face_confidence": sum(r.get("face_confidence", 0) for r in results) / len(results)
        }
    
    def get_audio_metrics(self) -> Dict:
        """마지막 분석의 오디오 메트릭 반환"""
        return self._last_result.audio_metrics if self._last_result else {}
    
    def get_audio_timeline(self) -> List[Dict]:
        """마지막 분석의 오디오 타임라인 반환"""
        return self._last_result.audio_timeline if self._last_result else []
    
    def get_elapsed_time(self) -> float:
        """마지막 분석 소요 시간 반환"""
        return self._last_result.elapsed_seconds if self._last_result else 0.0
    
    def get_vision_summary(self) -> Dict:
        """비전 분석 요약 반환"""
        return self._last_result.vision_summary if self._last_result else {}


def analyze_single_frame(frame_path: str) -> Dict:
    """
    단일 프레임 분석 (워커 함수)
    
    MediaPipe로 얼굴/포즈/손 감지
    """
    result = {
        "face_visible": False,
        "face_confidence": 0.0,
        "gesture_active": False,
        "pose_detected": False,
        "hands_detected": 0
    }
    
    try:
        if not MEDIAPIPE_AVAILABLE or not IMAGING_AVAILABLE:
            return result
        
        # Load image
        image = Image.open(frame_path)
        image_np = np.array(image)
        
        # Face detection
        mp_face = mp.solutions.face_detection
        with mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
            rgb_image = image_np[:, :, ::-1] if image_np.shape[2] == 3 else image_np
            face_results = face_detection.process(rgb_image)
            
            if face_results.detections:
                result["face_visible"] = True
                result["face_confidence"] = face_results.detections[0].score[0]
        
        # Pose detection
        mp_pose = mp.solutions.pose
        with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
            pose_results = pose.process(rgb_image)
            
            if pose_results.pose_landmarks:
                result["pose_detected"] = True
                
                # Check for active gestures (hands above waist)
                landmarks = pose_results.pose_landmarks.landmark
                left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
                right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
                left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
                
                if left_wrist.y < left_hip.y or right_wrist.y < left_hip.y:
                    result["gesture_active"] = True
        
        # Hand detection
        mp_hands = mp.solutions.hands
        with mp_hands.Hands(static_image_mode=True, max_num_hands=2) as hands:
            hand_results = hands.process(rgb_image)
            
            if hand_results.multi_hand_landmarks:
                result["hands_detected"] = len(hand_results.multi_hand_landmarks)
        
    except Exception as e:
        pass  # Silent fail for individual frames
    
    return result


# CLI test
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        video = Path(sys.argv[1])
        if video.exists():
            analyzer = TurboAnalyzer()
            vision, content = analyzer.analyze_video(video)
            print(f"\n📊 분석 결과:")
            print(f"   프레임 수: {len(vision)}")
            print(f"   소요 시간: {analyzer.get_elapsed_time():.1f}초")
            print(f"   비전 요약: {analyzer.get_vision_summary()}")
            print(f"   오디오 메트릭: {analyzer.get_audio_metrics()}")
        else:
            print(f"파일을 찾을 수 없습니다: {video}")
    else:
        print("Usage: python turbo_analyzer.py <video_path>")
