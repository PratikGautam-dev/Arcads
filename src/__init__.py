"""
Main Audio Pipeline - Complete orchestration of TTS and refinement
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path

from .utils import (
    load_config, 
    load_env_variables, 
    setup_directories, 
    setup_logging,
    validate_text_input,
    generate_filename
)
from .tts_service import ElevenLabsTTS
from .audio_refiner import AudioRefiner

# Initialize logger
logger = logging.getLogger(__name__)

def generate_refined_audio(
    text,
    voice_id=None,
    output_name=None,
    config_path="config/config.yaml"
):
    """
    Complete pipeline: Text -> Raw Audio -> Refined Audio
    
    Args:
        text (str): Text to convert to speech
        voice_id (str, optional): ElevenLabs voice ID
        output_name (str, optional): Custom output filename (without extension)
        config_path (str): Path to config file
    
    Returns:
        dict: Complete result with both raw and refined audio paths
    """
    pipeline_start = time.time()
    
    try:
        # Load configuration
        config = load_config(config_path)
        
        # Setup logging
        setup_logging(config)
        
        # Setup directories
        setup_directories(config)
        
        # Load API key
        api_key = load_env_variables()
        
        # Validate text input
        text = validate_text_input(text)
        
        logger.info("="*60)
        logger.info("Starting Audio Generation Pipeline")
        logger.info(f"Text length: {len(text)} characters")
        logger.info("="*60)
        
        # Generate filenames
        if output_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_name = f"audio_{timestamp}"
        
        raw_audio_path = os.path.join(
            config['paths']['raw_audio'],
            f"{output_name}.mp3"
        )
        
        refined_audio_path = os.path.join(
            config['paths']['refined_audio'],
            f"{output_name}.wav"
        )
        
        # Step 1: Generate audio with ElevenLabs
        logger.info("Step 1: Generating audio with ElevenLabs...")
        tts = ElevenLabsTTS(api_key, config)
        
        # Validate API key
        if not tts.validate_api_key():
            raise ValueError("Invalid ElevenLabs API key")
        
        # Generate and save raw audio
        tts_result = tts.generate_and_save(
            text=text,
            output_path=raw_audio_path,
            voice_id=voice_id
        )
        
        if not tts_result['success']:
            raise Exception(f"TTS generation failed: {tts_result['error']}")
        
        logger.info(f"✓ Raw audio generated: {raw_audio_path}")
        
        # Step 2: Refine audio
        logger.info("Step 2: Refining audio quality...")
        refiner = AudioRefiner(config)
        
        refine_result = refiner.process_pipeline(
            input_path=raw_audio_path,
            output_path=refined_audio_path
        )
        
        if not refine_result['success']:
            raise Exception(f"Audio refinement failed: {refine_result['error']}")
        
        logger.info(f"✓ Refined audio saved: {refined_audio_path}")
        
        # Calculate total time
        total_time = time.time() - pipeline_start
        
        logger.info("="*60)
        logger.info("Pipeline Completed Successfully!")
        logger.info(f"Total time: {total_time:.2f}s")
        logger.info("="*60)
        
        # Return complete result
        return {
            'success': True,
            'raw_audio': raw_audio_path,
            'refined_audio': refined_audio_path,
            'metadata': {
                'text': text,
                'text_length': len(text),
                'voice_id': tts_result['metadata']['voice_id'],
                'generation_time': tts_result['metadata']['generation_time'],
                'refinement_time': refine_result['metadata']['processing_time'],
                'total_time': round(total_time, 2),
                'raw_size_mb': round(tts_result['metadata']['file_size'] / (1024*1024), 2),
                'refined_size_mb': round(refine_result['metadata']['file_size'] / (1024*1024), 2),
                'duration': refine_result['metadata']['output_duration'],
                'sample_rate': refine_result['metadata']['sample_rate']
            },
            'error': None
        }
        
    except Exception as e:
        error_msg = f"Pipeline failed: {str(e)}"
        logger.error(error_msg)
        
        return {
            'success': False,
            'raw_audio': None,
            'refined_audio': None,
            'metadata': None,
            'error': error_msg
        }

def quick_generate(text, voice_id=None):
    """
    Quick generation with default settings
    
    Args:
        text (str): Text to convert
        voice_id (str, optional): Voice ID
    
    Returns:
        dict: Result with file paths
    """
    return generate_refined_audio(text, voice_id)


# Export main functions
__all__ = [
    'generate_refined_audio',
    'quick_generate',
    'ElevenLabsTTS',
    'AudioRefiner'
]