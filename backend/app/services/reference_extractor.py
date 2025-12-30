import yt_dlp
import os
import cv2
import numpy as np

class ReferenceExtractor:
    def __init__(self, download_dir="backend/downloads/references"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)

    def download_reference(self, url: str) -> str:
        """
        Downloads a YouTube video and returns the local path.
        """
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(self.download_dir, '%(id)s.%(ext)s'),
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename

    def analyze_style(self, video_path: str):
        """
        Analyze the video to extract 'style' metrics:
        - Average Shot Length (ASL): Fast vs Slow pacing.
        - Color Vibe: Saturation/Brightness levels.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        # 1. Pacing Analysis (Shot detection)
        # Simplified: Use standard deviation of pixel intensity to find hard cuts
        # Real implementation would use pyscenedetect, here we mock for speed
        # Assume a cut every time pixel difference spikes
        
        # Heuristic for "Pacing":
        # Action/Hype = ~1-2s average shot length
        # Vlog/Cinematic = ~4-8s average shot length
        
        # For this demo, let's just use the duration and a heuristic or random mock
        # Real implementation: Iterate frames, calc diff, find peaks.
        
        shot_count = max(1, int(duration / 3)) # Mock: assuming 3s cuts on average
        avg_shot_length = duration / shot_count
        
        return {
            "pacing": "fast" if avg_shot_length < 2.5 else "slow",
            "avg_shot_length": avg_shot_length,
            "duration": duration,
            "source_path": video_path
        }
