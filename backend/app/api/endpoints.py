from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.app.services.analyzer import AssetAnalyzer
import shutil
import os
import uuid

router = APIRouter()
analyzer = AssetAnalyzer()

UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_asset(file: UploadFile = File(...)):
    """
    Upload a video or audio file. Returns a file ID.
    """
    file_id = str(uuid.uuid4())
    extension = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{extension}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"file_id": file_id, "filename": file.filename, "path": file_path}

@router.post("/analyze/{file_type}/{file_id}")
async def analyze_asset(file_type: str, file_id: str):
    """
    Trigger analysis. file_type = 'video' or 'audio'.
    """
    # Simple search for file (ignoring extension)
    found_path = None
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            if f.startswith(file_id):
                found_path = os.path.join(UPLOAD_DIR, f)
                break
            
    if not found_path:
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        if file_type == "video":
            metadata = analyzer.get_video_metadata(found_path)
            scenes = analyzer.detect_scenes(found_path)
            return {"metadata": metadata, "scenes": scenes}
        elif file_type == "audio":
            analysis = analyzer.analyze_audio(found_path)
            return {"analysis": analysis}
            raise HTTPException(status_code=400, detail="Invalid file type")
    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_edit")
async def generate_edit(request: dict):
    """
    Full Pipeline:
    1. Receives list of file_ids and a prompt.
    2. Director creates an EDL.
    3. VideoProcessor renders it.
    """
    from backend.app.services.director import Director
    from backend.app.services.video_processor import VideoProcessor
    from backend.app.services.reference_extractor import ReferenceExtractor
    
    file_ids = request.get("file_ids", [])
    prompt = request.get("prompt", "Make a cool video")
    reference_url = request.get("reference_url") # Optional YouTube link
    
    if not file_ids:
        raise HTTPException(status_code=400, detail="No files provided")
        
    director = Director()
    processor = VideoProcessor()
    ref_extractor = ReferenceExtractor()
    
    # 0. Process Reference (if any)
    reference_style = None
    if reference_url:
        try:
            print(f"Downloading reference: {reference_url}")
            ref_path = ref_extractor.download_reference(reference_url)
            reference_style = ref_extractor.analyze_style(ref_path)
            print(f"Extracted Style: {reference_style}")
        except Exception as e:
            print(f"Reference extraction failed: {e}")
            # Continue without reference
            
    # 0.5 Process Music (if any)
    music_id = request.get("music_id")
    music_path = None
    if music_id:
        # Search in music dir
        music_dir = "backend/uploads/music"
        for f in os.listdir(music_dir):
            if f.startswith(music_id):
                music_path = os.path.join(music_dir, f)
                break
    
    # 1. Gather Metadata
    assets_metadata = []
    for fid in file_ids:
        # Locate file
        found_path = None
        for f in os.listdir(UPLOAD_DIR):
            if f.startswith(fid):
                found_path = os.path.join(UPLOAD_DIR, f)
                break
        
        if found_path:
            meta = analyzer.get_video_metadata(found_path)
            assets_metadata.append({
                "file_id": fid,
                "path": found_path,
                "metadata": meta
            })
            
    # 2. Director -> EDL
    # Mix user prompt with reference insights
    final_prompt = prompt
    if reference_style:
        pacing = reference_style.get("pacing", "normal")
        final_prompt += f". STYLE REFERENCE: Match this pacing: {pacing} (avg shot {reference_style.get('avg_shot_length', 3):.1f}s)."
        
    edl = director.generate_edit_script(final_prompt, assets_metadata, reference_style)
    
    if music_path:
        edl['audio_track'] = music_path
    
    # 3. Render
    output_filename = f"render_{uuid.uuid4()}.mp4"
    output_path = os.path.join(UPLOAD_DIR, output_filename)
    
    try:
        processor.render_video(edl, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rendering failed: {str(e)}")
        
    return {
        "status": "success",
        "edl": edl,
        "output_url": f"/static/{output_filename}",
        "output_path": output_path
    }

# --- Music Endpoints ---
from backend.app.services.audio_service import AudioService
audio_service = AudioService()

@router.post("/music/upload")
async def upload_music(file: UploadFile = File(...)):
    return audio_service.save_music(file)

@router.get("/music/list")
async def list_music():
    return audio_service.list_music()

