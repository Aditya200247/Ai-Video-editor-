import json
import os
import google.generativeai as genai

class Director:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("✅ AI Director initialized with Gemini Pro")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini: {e}")
        else:
            print("⚠️ No GEMINI_API_KEY found. using fallback logic.")
            
        self.styles = self._load_styles()

    def _load_styles(self):
        try:
            with open("app/services/styles.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Try absolute path if relative fails (for testing)
            try:
                with open("backend/app/services/styles.json", "r") as f:
                    return json.load(f)
            except:
                return {}
        except Exception:
            return {}

    def _analyze_vibe(self, prompt: str) -> str:
        prompt = prompt.lower()
        if any(w in prompt for w in ['fast', 'hype', 'quick', 'energetic', 'gaming', 'montage']):
            return 'hype'
        if any(w in prompt for w in ['slow', 'cinematic', 'movie', 'film', 'sad', 'emotional', 'drama']):
            return 'cinematic'
        return 'vlog'

    def generate_edit_script(self, user_prompt: str, assets_metadata: list, reference_style: dict = None) -> dict:
        """
        Takes user intent and assets, returns an Edit Decision List (EDL).
        Uses Gemini LLM if available, otherwise falls back to vibe-based heuristics.
        """
        detected_vibe = self._analyze_vibe(user_prompt)
        print(f"🎬 Director detected vibe: {detected_vibe}")

        if self.model:
            try:
                return self._generate_with_llm(user_prompt, assets_metadata, detected_vibe, reference_style)
            except Exception as e:
                print(f"❌ LLM Generation failed: {e}. Falling back to heuristic.")
                
        return self._generate_heuristic(user_prompt, assets_metadata, detected_vibe)

    def _generate_with_llm(self, user_prompt: str, assets: list, vibe: str, style_ref: dict) -> dict:
        """Generate EDL using Gemini Pro"""
        
        style_config = self.styles.get("styles", {}).get(vibe, {})
        
        # Simplify assets for the prompt to save tokens/complexity
        simplified_assets = []
        for a in assets:
            simplified_assets.append({
                "id": a['file_id'],
                "type": a['type'], # video/image
                "duration": f"{a['metadata'].get('duration', 0):.1f}s",
                "filename": os.path.basename(a['path'])
            })

        system_prompt = f"""
        Act as a professional Video Editor Director. Your goal is to create an engaging video edit based on the user's request and the available assets.
        
        **Style:** {vibe.upper()}
        **Description:** {style_config.get('description', 'Standard edit')}
        **System Instructions:** {style_config.get('system_instruction', 'Create a balanced video.')}
        
        **Available Assets:**
        {json.dumps(simplified_assets, indent=2)}
        
        **User Request:** "{user_prompt}"
        
        **Task:**
        Create a JSON Edit Decision List (EDL) that selects the best parts of the clips.
        - For 'hype', use short, fast cuts (2-4s).
        - For 'cinematic', use longer, steady shots (5-8s).
        - Ensure the total duration matches the amount of content provided (don't make it too short if there are many clips).
        - You CAN re-use clips if it fits the style (like a montage).
        
        **Output Format (Strict JSON):**
        {{
            "timeline": [
                {{
                    "clip_id": "string (must match Asset ID)",
                    "start": float (start time in seconds),
                    "end": float (end time in seconds),
                    "description": "reason for selection",
                    "transition": "cut" | "cross_dissolve" | "fade_in" | "fade_out",
                    "speed": float (1.0 is normal),
                    "filter": "none" | "black_white" | "vibrant"
                }}
            ],
            "explanation": "Brief explanation of your creative choices."
        }}
        """
        
        response = self.model.generate_content(system_prompt)
        cleaned_json = self._clean_json_response(response.text)
        return cleaned_json

    def _clean_json_response(self, text: str) -> dict:
        """Extracts JSON from markdown code blocks if necessary"""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text.strip())
        except Exception as e:
            raise ValueError(f"Failed to parse LLM JSON: {e}")

    def _generate_heuristic(self, user_prompt: str, assets: list, vibe: str) -> dict:
        """Fallback logic if LLM is unavailable"""
        style_config = self.styles.get("styles", {}).get(vibe, {})
        target_clip_len = style_config.get('pacing', 3.0)
        timeline = []
        
        print(f"⚠️ Using Heuristic Director for {vibe} style")
        
        for asset in assets:
            duration = asset.get('metadata', {}).get('duration', 10)
            
            if vibe == 'hype':
                # Hype: Fast cuts
                if duration > target_clip_len:
                    timeline.append({
                        "clip_id": asset['file_id'],
                        "source_path": asset['path'],
                        "start": 0,
                        "end": target_clip_len,
                        "description": "Fast opener",
                        "speed": 1.2,
                        "transition": "cut"
                    })
            elif vibe == 'cinematic':
                # Cinematic: Slow middle cut
                mid = duration / 2
                half = target_clip_len / 2
                timeline.append({
                    "clip_id": asset['file_id'],
                    "source_path": asset['path'],
                    "start": max(0, mid - half),
                    "end": min(duration, mid + half),
                    "description": "Cinematic center frame",
                    "filter": "vibrant",
                    "transition": "cross_dissolve"
                })
            else:
                # Standard
                timeline.append({
                    "clip_id": asset['file_id'],
                    "source_path": asset['path'],
                    "start": 0,
                    "end": min(duration, target_clip_len),
                    "description": "Standard selection",
                    "transition": "cut"
                })
                
        return {
            "timeline": timeline,
            "explanation": f"Heuristic fallback: Generated {vibe} edit."
        }
