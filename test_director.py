from backend.app.services.director import Director

def test_director_logic():
    d = Director()
    
    # Test 1: Vibe Detection
    print("Testing Vibe Detection...")
    prompts = {
        "Make a fast hype reel for gaming": "hype",
        "Create a slow emotional movie scene": "cinematic",
        "Just a daily vlog edit": "vlog"
    }
    
    for p, expected in prompts.items():
        vibe = d._analyze_vibe(p)
        print(f"Prompt: '{p}' -> Vibe: {vibe} (Expected: {expected})")
        assert vibe == expected
        
    # Test 2: EDL Generation (Mock Assets)
    print("\nTesting EDL Generation...")
    assets = [{
        "file_id": "test_1",
        "path": "test.mp4",
        "metadata": {"duration": 10.0}
    }]
    
    # Test Hype
    edl_hype = d.generate_edit_script("make it hype", assets)
    # Expect multiple cuts or speed up
    print("Hype EDL explanation:", edl_hype['explanation'])
    assert "hype" in edl_hype['explanation']
    
    # Test Cinematic
    edl_cine = d.generate_edit_script("make it cinematic", assets)
    print("Cinematic EDL explanation:", edl_cine['explanation'])
    assert "cinematic" in edl_cine['explanation']
    
    print("\nALL TESTS PASSED")

if __name__ == "__main__":
    test_director_logic()
