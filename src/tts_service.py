"""
ElevenLabs Text-to-Speech Service
Handles audio generation from text using ElevenLabs API
"""

import os
import time
import logging
import requests
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

logger = logging.getLogger(__name__)

class ElevenLabsTTS:
    """ElevenLabs TTS service wrapper"""
    
    def __init__(self, api_key, config):
        """
        Initialize ElevenLabs TTS service
        
        Args:
            api_key (str): ElevenLabs API key
            config (dict): Configuration dictionary
        """
        self.api_key = api_key
        self.config = config
        self.client = ElevenLabs(api_key=api_key)
        
        # Get settings from config
        self.model = config['elevenlabs']['model']
        self.default_voice_id = config['elevenlabs']['default_voice_id']
        self.voice_settings = config['elevenlabs']['settings']
        
        logger.info(f"ElevenLabs TTS initialized with model: {self.model}")
    
    def validate_api_key(self):
        """
        Validate that the API key is working
        
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Try to get voices to test API key
            voices = self.client.voices.get_all()
            logger.info(f"API key validated successfully. {len(voices.voices)} voices available")
            return True
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            return False
    
    def get_available_voices(self):
        """
        Get list of available voices
        
        Returns:
            list: List of voice dictionaries with id, name, and category
        """
        try:
            voices_response = self.client.voices.get_all()
            voices = []
            
            for voice in voices_response.voices:
                voices.append({
                    'id': voice.voice_id,
                    'name': voice.name,
                    'category': voice.category if hasattr(voice, 'category') else 'general'
                })
            
            logger.info(f"Retrieved {len(voices)} available voices")
            return voices
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
            return []
    
    def generate_audio(self, text, voice_id=None, settings=None):
        """
        Generate audio from text using ElevenLabs
        
        Args:
            text (str): Text to convert to speech
            voice_id (str, optional): Voice ID to use. Defaults to config default
            settings (dict, optional): Custom voice settings. Defaults to config settings
        
        Returns:
            dict: Result containing success status, audio data, and metadata
        """
        start_time = time.time()
        
        # Use defaults if not provided
        if voice_id is None:
            voice_id = self.default_voice_id
        
        if settings is None:
            settings = self.voice_settings
        
        try:
            logger.info(f"Generating audio for text (length: {len(text)} chars) with voice: {voice_id}")
            
            # Create voice settings object
            voice_settings_obj = VoiceSettings(
                stability=settings.get('stability', 0.6),
                similarity_boost=settings.get('similarity_boost', 0.8),
                style=settings.get('style', 0.4),
                use_speaker_boost=settings.get('use_speaker_boost', True)
            )
            
            # Generate audio
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id=self.model,
                voice_settings=voice_settings_obj
            )
            
            # Collect audio bytes
            audio_data = b''.join(audio_generator)
            
            generation_time = time.time() - start_time
            
            logger.info(f"Audio generated successfully in {generation_time:.2f}s")
            
            return {
                'success': True,
                'audio_data': audio_data,
                'metadata': {
                    'voice_id': voice_id,
                    'text_length': len(text),
                    'generation_time': round(generation_time, 2),
                    'audio_size': len(audio_data)
                },
                'error': None
            }
            
        except Exception as e:
            error_msg = f"Error generating audio: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'audio_data': None,
                'metadata': None,
                'error': error_msg
            }
    
    def save_audio(self, audio_data, output_path):
        """
        Save audio data to file
        
        Args:
            audio_data (bytes): Audio data to save
            output_path (str): Path where to save the audio file
        
        Returns:
            dict: Result containing success status and file info
        """
        try:
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write audio data
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            file_size = os.path.getsize(output_path)
            file_size_mb = file_size / (1024 * 1024)
            
            logger.info(f"Audio saved to: {output_path} ({file_size_mb:.2f} MB)")
            
            return {
                'success': True,
                'file_path': output_path,
                'file_size': file_size,
                'error': None
            }
            
        except Exception as e:
            error_msg = f"Error saving audio: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'file_path': None,
                'file_size': 0,
                'error': error_msg
            }
    
    def generate_and_save(self, text, output_path, voice_id=None, settings=None):
        """
        Generate audio and save to file in one step
        
        Args:
            text (str): Text to convert to speech
            output_path (str): Where to save the audio
            voice_id (str, optional): Voice ID to use
            settings (dict, optional): Custom voice settings
        
        Returns:
            dict: Combined result with generation and save info
        """
        # Generate audio
        gen_result = self.generate_audio(text, voice_id, settings)
        
        if not gen_result['success']:
            return gen_result
        
        # Save audio
        save_result = self.save_audio(gen_result['audio_data'], output_path)
        
        if not save_result['success']:
            return save_result
        
        # Combine results
        return {
            'success': True,
            'file_path': save_result['file_path'],
            'metadata': {
                **gen_result['metadata'],
                'file_size': save_result['file_size'],
                'output_path': output_path
            },
            'error': None
        }