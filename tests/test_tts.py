"""
Test script for TTS and audio refinement pipeline
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import generate_refined_audio, quick_generate

def test_basic_generation():
    """Test 1: Basic audio generation"""
    print("\n" + "="*60)
    print("TEST 1: Basic Audio Generation")
    print("="*60)
    
    text = "Hello world, this is a test of the audio generation system."
    
    result = quick_generate(text)
    
    if result['success']:
        print("\n✅ Test PASSED!")
        print(f"Raw audio: {result['raw_audio']}")
        print(f"Refined audio: {result['refined_audio']}")
        print(f"Duration: {result['metadata']['duration']}s")
        print(f"Total time: {result['metadata']['total_time']}s")
    else:
        print(f"\n❌ Test FAILED: {result['error']}")
    
    return result['success']

def test_ad_script():
    """Test 2: Realistic ad script"""
    print("\n" + "="*60)
    print("TEST 2: Ad Script Generation")
    print("="*60)
    
    text = """
    Discover the future of fitness with FitAI! 
    Our revolutionary app uses artificial intelligence to create personalized workout plans 
    that adapt to your progress in real-time. 
    Join thousands of users who've already transformed their lives. 
    Download FitAI today and get your first month free!
    """
    
    result = generate_refined_audio(
        text=text,
        output_name="test_ad_script"
    )
    
    if result['success']:
        print("\n✅ Test PASSED!")
        print(f"Raw audio: {result['raw_audio']}")
        print(f"Refined audio: {result['refined_audio']}")
        print(f"Duration: {result['metadata']['duration']}s")
        print(f"Processing breakdown:")
        print(f"  - TTS: {result['metadata']['generation_time']}s")
        print(f"  - Refinement: {result['metadata']['refinement_time']}s")
        print(f"  - Total: {result['metadata']['total_time']}s")
    else:
        print(f"\n❌ Test FAILED: {result['error']}")
    
    return result['success']

def test_different_voice():
    """Test 3: Different voice"""
    print("\n" + "="*60)
    print("TEST 3: Different Voice (Adam)")
    print("="*60)
    
    text = "This is Adam's voice speaking. Testing different voice characteristics."
    
    # Adam voice ID
    adam_voice = "pNInz6obpgDQGcFmaJgB"
    
    result = generate_refined_audio(
        text=text,
        voice_id=adam_voice,
        output_name="test_adam_voice"
    )
    
    if result['success']:
        print("\n✅ Test PASSED!")
        print(f"Voice used: {result['metadata']['voice_id']}")
        print(f"Refined audio: {result['refined_audio']}")
    else:
        print(f"\n❌ Test FAILED: {result['error']}")
    
    return result['success']

def test_error_handling():
    """Test 4: Error handling"""
    print("\n" + "="*60)
    print("TEST 4: Error Handling")
    print("="*60)
    
    # Test with empty text
    print("\nTesting empty text...")
    result = quick_generate("")
    
    if not result['success']:
        print("✅ Empty text correctly rejected")
    else:
        print("❌ Empty text should have been rejected")
        return False
    
    # Test with very long text
    print("\nTesting very long text (>5000 chars)...")
    long_text = "A" * 6000
    result = quick_generate(long_text)
    
    if not result['success']:
        print("✅ Long text correctly rejected")
    else:
        print("❌ Long text should have been rejected")
        return False
    
    print("\n✅ Error handling test PASSED!")
    return True

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("AUDIO PIPELINE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Basic Generation", test_basic_generation),
        ("Ad Script", test_ad_script),
        ("Different Voice", test_different_voice),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ {test_name} CRASHED: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️ SOME TESTS FAILED")

if __name__ == "__main__":
    run_all_tests()