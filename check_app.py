import sys
import os

print("Checking imports...")
try:
    from backend.app.services.analyzer import AssetAnalyzer
    print("Analyzer imported.")
    from backend.app.services.director import Director
    print("Director imported.")
    from backend.app.services.video_processor import VideoProcessor
    print("VideoProcessor imported.")
    from backend.app.services.reference_extractor import ReferenceExtractor
    print("ReferenceExtractor imported.")
    from backend.main import app
    print("FastAPI App imported.")
    print("ALL SYSTEMS GO.")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
