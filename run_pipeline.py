"""
Simple script to run the audio pipeline
Usage: python run_pipeline.py
"""

from src import quick_generate

def main():
    """Run the audio generation pipeline"""
    
    print("\n" + "="*60)
    print("AI VIDEO ADS - AUDIO GENERATOR")
    print("="*60)
    
    # Your ad script here
    text = """
    Transform your fitness journey with FitAI! 
    Our revolutionary app uses artificial intelligence to create personalized workout plans 
    that adapt to your progress in real-time. 
    Join thousands of users who've already transformed their lives. 
    Download FitAI today and get your first month free!
    """
    
    print(f"\nGenerating audio for text ({len(text)} characters)...")
    print("\nProcessing...\n")
    
    # Generate audio
    result = quick_generate(text)
    
    # Display results
    if result['success']:
        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print(f"\n📁 Files generated:")
        print(f"   Raw MP3:      {result['raw_audio']}")
        print(f"   Refined WAV:  {result['refined_audio']}")
        
        print(f"\n📊 Metadata:")
        print(f"   Duration:     {result['metadata']['duration']}s")
        print(f"   Sample Rate:  {result['metadata']['sample_rate']} Hz")
        print(f"   Voice:        {result['metadata']['voice_id']}")
        
        print(f"\n⏱️  Processing time:")
        print(f"   TTS:          {result['metadata']['generation_time']}s")
        print(f"   Refinement:   {result['metadata']['refinement_time']}s")
        print(f"   Total:        {result['metadata']['total_time']}s")
        
        print(f"\n💾 File sizes:")
        print(f"   Raw MP3:      {result['metadata']['raw_size_mb']} MB")
        print(f"   Refined WAV:  {result['metadata']['refined_size_mb']} MB")
        
        print("\n✨ The refined WAV is ready for MuseTalk!")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("❌ FAILED!")
        print("="*60)
        print(f"\nError: {result['error']}")
        print("\nCheck logs/ directory for details.")
        print("="*60 + "\n")

if __name__ == "__main__":
    main()