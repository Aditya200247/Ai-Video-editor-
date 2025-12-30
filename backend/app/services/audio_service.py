import os
import shutil
import uuid
from fastapi import UploadFile

class AudioService:
    def __init__(self, upload_dir="backend/uploads/music"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    def save_music(self, file: UploadFile) -> dict:
        """
        Save an uploaded music file.
        """
        file_id = str(uuid.uuid4())
        extension = os.path.splitext(file.filename)[1]
        if not extension:
            extension = ".mp3" # Default
            
        filename = f"{file_id}{extension}"
        file_path = os.path.join(self.upload_dir, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {
            "id": file_id,
            "filename": file.filename,
            "path": file_path,
            "url": f"/static/music/{filename}"
        }

    def list_music(self) -> list:
        """
        List available music tracks.
        """
        tracks = []
        if os.path.exists(self.upload_dir):
            for f in os.listdir(self.upload_dir):
                if f.endswith(('.mp3', '.wav', '.m4a')):
                    tracks.append({
                        "id": os.path.splitext(f)[0],
                        "filename": f,
                        "path": os.path.join(self.upload_dir, f),
                        "url": f"/static/music/{f}"
                    })
        return tracks
