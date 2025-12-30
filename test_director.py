import os
import unittest
from unittest.mock import MagicMock, patch
from backend.app.services.director import Director

class TestDirector(unittest.TestCase):
    def setUp(self):
        # Ensure no API key interferes with default tests
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
            
    def test_vibe_detection(self):
        d = Director()
        print("\nTesting Vibe Detection...")
        prompts = {
            "Make a fast hype reel for gaming": "hype",
            "Create a slow emotional movie scene": "cinematic",
            "Just a daily vlog edit": "vlog"
        }
        for p, expected in prompts.items():
            vibe = d._analyze_vibe(p)
            print(f"Prompt: '{p}' -> Vibe: {vibe}")
            self.assertEqual(vibe, expected)

    def test_heuristic_fallback(self):
        """Test the logic when no API key is present"""
        print("\nTesting Heuristic Fallback...")
        d = Director()
        assets = [{"file_id": "1", "path": "vid.mp4", "metadata": {"duration": 10.0}, "type": "video"}]
        
        # Test Hype
        edl = d.generate_edit_script("make it hype", assets)
        self.assertIn("Heuristic fallback", edl['explanation'])
        self.assertIn("hype", edl['explanation'])
        
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_llm_generation(self, mock_config, mock_model_class):
        """Test the LLM path by mocking the API"""
        print("\nTesting LLM Path (Mocked)...")
        
        # Setup Mock
        mock_instance = mock_model_class.return_value
        mock_response = MagicMock()
        mock_response.text = '```json\n{"timeline": [], "explanation": "AI Generated"}\n```'
        mock_instance.generate_content.return_value = mock_response
        
        # Inject Fake Key
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
            d = Director() # Should initialize model now
            
            assets = [{"file_id": "1", "path": "vid.mp4", "metadata": {"duration": 10.0}, "type": "video"}]
            edl = d.generate_edit_script("make it cinematic", assets)
            
            print("LLM EDL Explanation:", edl['explanation'])
            self.assertEqual(edl['explanation'], "AI Generated")
            mock_instance.generate_content.assert_called_once()

if __name__ == "__main__":
    unittest.main()
