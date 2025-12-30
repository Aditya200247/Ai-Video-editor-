import json
import os

class Director:
    def __init__(self):
        # In a real app, initialize Gemini or OpenAI client here
        # self.client = genai.GenerativeModel('gemini-pro')
        self.styles = self._load_styles()

    def _load_styles(self):
        try:
            with open("backend/app/services/styles.json", "r") as f:
                return json.load(f)
        except:
            return {}

    def _analyze_vibe(self, prompt: str) -> str:
        """
        Simple keyword matching to guess the vibe.
        In a real LLM app, this would be a separate prompt.
        """
        prompt = prompt.lower()
        if any(w in prompt for w in ['fast', 'hype', 'quick', 'energetic', 'gaming']):
            return 'hype'
        if any(w in prompt for w in ['slow', 'cinematic', 'movie', 'film', 'sad', 'emotional']):
            return 'cinematic'
        return 'vlog' # Default

    def generate_edit_script(self, user_prompt: str, assets_metadata: list, reference_style: dict = None) -> dict:
        """
        The 'Brain'. Takes user intent and assets, returns an Edit Decision List (EDL).
        """
        
        # 1. Determine Vibe / Style
        detected_vibe = self._analyze_vibe(user_prompt)
        style_config = self.styles.get("styles", {}).get(detected_vibe, {})
        
        print(f"Director detected vibe: {detected_vibe}")
        
        # 2. Construct the System Prompt with Few-Shot Examples (Training)
        system_prompt = f"""
        You are a professional video editor specializing in {detected_vibe} style.
        Style Description: {style_config.get('description', 'Standard video editing')}
        Instructions: {style_config.get('system_instruction', 'Create a balanced video.')}
        
        Your job is to take a set of video clips and a user request and create a JSON Edit Decision List (EDL).
        
        The Output must strictly follow this JSON schema:
        {{
            "timeline": [
                {{
                    "clip_id": "string",
                    "start": float,
                    "end": float,
                    "description": "string",
                    "transition": "cut" | "fade_in" | "fade_out",
                    "speed": float,
                    "saturation": float,
                    "filter": "black_white"
                }}
            ],
            "audio_track": "string (optional)",
            "explanation": "string"
        }}
        """
        
        # Inject Examples
        examples = style_config.get('examples', [])
        if examples:
            system_prompt += "\n\nEXAMPLES OF GOOD EDITS:\n"
            for ex in examples:
                system_prompt += f"User: {ex['user_request']}\nEDL Snippet: {json.dumps(ex['edl_snippet'])}\n\n"

        # 3. Construct User Context
        context = {
            "user_request": user_prompt,
            "assets_summary": [
                 f"ID: {a['file_id']}, Dur: {a['metadata'].get('duration',0)}s" for a in assets_metadata
            ],
            "assets": assets_metadata, # Full metadata provided to logic
            "reference_style": reference_style
        }
        
        # 4. Call LLM (Mocked for now with smarter heuristics based on vibe)
        print(f"Director received prompt: {user_prompt}")
        
        # --- MOCK INTELLIGENCE ---
        # Instead of random 2s clips, we adjust based on Vibe
        
        target_clip_len = style_config.get('pacing', 3.0)
        timeline = []
        
        for asset in assets_metadata:
            duration = asset.get('metadata', {}).get('duration', 10)
            
            # Divide clip into chunks based on pacing
            current_pos = 0.0
            
            # For HYPE, we might take multiple fast cuts from same clip
            # For CINEMATIC, we take one long stable shot
            
            if detected_vibe == 'hype':
                # Take 2-3 short bursts
                num_cuts = 2
                for i in range(num_cuts):
                    if current_pos + target_clip_len > duration: break
                    
                    timeline.append({
                        "clip_id": asset['file_id'],
                        "source_path": asset['path'],
                        "start": current_pos,
                        "end": current_pos + target_clip_len,
                        "description": f"Hype cut {i+1}",
                        "effect": "zoom_in" if i % 2 == 0 else "cut",
                        "speed": 1.5 # Fast!
                    })
                    current_pos += (target_clip_len + 2.0) # Skip ahead
            
            elif detected_vibe == 'cinematic':
                # Take one long middle section
                mid = duration / 2
                half_len = target_clip_len / 2
                start = max(0, mid - half_len)
                end = min(duration, mid + half_len)
                
                timeline.append({
                    "clip_id": asset['file_id'],
                    "source_path": asset['path'],
                    "start": start,
                    "end": end,
                    "description": "Cinematic stable shot",
                    "saturation": 1.2, # Good color
                    "transition": "cross_dissolve"
                })
                
            else:
                # Default logic
                start = 0
                end = min(duration, target_clip_len)
                timeline.append({
                    "clip_id": asset['file_id'],
                    "source_path": asset['path'],
                    "start": start,
                    "end": end,
                    "description": "Standard cut",
                    "effect": "cut"
                })
            
        return {
            "timeline": timeline,
            "explanation": f"Generated a {detected_vibe} edit based on your request and provided examples."
        }
