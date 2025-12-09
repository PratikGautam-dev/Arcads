"""
Audio Refinement Pipeline
Processes raw audio to improve quality for lip sync
"""

import os
import time
import logging
import numpy as np
import soundfile as sf
import noisereduce as nr
from pydub import AudioSegment
from pathlib import Path

logger = logging.getLogger(__name__)

class AudioRefiner:
    """Audio refinement and processing pipeline"""
    
    def __init__(self, config):
        """
        Initialize audio refiner with configuration
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.refinement_config = config['audio_refinement']
        self.output_config = self.refinement_config['output']
        
        self._configure_ffmpeg()
        logger.info("Audio refiner initialized")

    def _configure_ffmpeg(self):
        """Configure ffmpeg path for pydub"""
        import shutil
        
        # 1. Check config file first
        if 'paths' in self.config and self.config['paths'].get('ffmpeg'):
            ffmpeg_path = self.config['paths']['ffmpeg']
            if os.path.exists(ffmpeg_path):
                AudioSegment.converter = ffmpeg_path
                os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
                logger.info(f"Using ffmpeg from config: {ffmpeg_path}")
                return
            else:
                logger.warning(f"Configured ffmpeg path not found: {ffmpeg_path}")

        # 2. Check if ffmpeg is already in path
        if shutil.which("ffmpeg"):
            logger.info(f"ffmpeg found in PATH: {shutil.which('ffmpeg')}")
            return

        # Common Windows install locations to check
        possible_paths = [
            r"C:\ffmpeg\bin",
            r"C:\Program Files\ffmpeg\bin",
            os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.0.2-full_build\bin"), # Common winget path
             os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Links"), # Winget links
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                # Add to PATH environment variable for pydub/subprocess
                os.environ["PATH"] += os.pathsep + path
                logger.info(f"Added ffmpeg to PATH: {path}")
                return
                
        logger.warning("ffmpeg not found in common locations. Ensure it is installed and in PATH.")
    
    def load_audio(self, file_path):
        """
        Load audio file (supports MP3, WAV, etc.)
        
        Args:
            file_path (str): Path to audio file
        
        Returns:
            tuple: (audio_data as numpy array, sample_rate)
        """
        try:
            # Load using pydub (handles MP3, WAV, etc.)
            audio = AudioSegment.from_file(file_path)
            
            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Get sample rate
            sample_rate = audio.frame_rate
            
            # Convert to numpy array
            audio_array = np.array(audio.get_array_of_samples(), dtype=np.float32)
            
            # Normalize to -1 to 1 range
            audio_array = audio_array / np.iinfo(audio.array_type).max
            
            logger.info(f"Loaded audio: {file_path} (duration: {len(audio_array)/sample_rate:.2f}s, SR: {sample_rate}Hz)")
            
            return audio_array, sample_rate
            
        except Exception as e:
            logger.error(f"Error loading audio: {str(e)}")
            raise
    
    def reduce_noise(self, audio_data, sample_rate):
        """
        Apply noise reduction to audio
        
        Args:
            audio_data (np.array): Audio data
            sample_rate (int): Sample rate
        
        Returns:
            np.array: Noise-reduced audio
        """
        if not self.refinement_config['noise_reduction']['enabled']:
            logger.info("Noise reduction disabled")
            return audio_data
        
        try:
            strength = self.refinement_config['noise_reduction']['strength']
            
            logger.info(f"Applying noise reduction (strength: {strength})")
            
            # Apply noise reduction
            reduced_noise = nr.reduce_noise(
                y=audio_data,
                sr=sample_rate,
                prop_decrease=strength,
                stationary=True
            )
            
            logger.info("Noise reduction completed")
            return reduced_noise
            
        except Exception as e:
            logger.warning(f"Noise reduction failed: {str(e)}, using original audio")
            return audio_data
    
    def normalize_volume(self, audio_data, target_db=-18.0):
        """
        Normalize audio volume to target dB level
        
        Args:
            audio_data (np.array): Audio data
            target_db (float): Target dB level
        
        Returns:
            np.array: Normalized audio
        """
        if not self.refinement_config['normalization']['enabled']:
            logger.info("Volume normalization disabled")
            return audio_data
        
        try:
            target_db = self.refinement_config['normalization']['target_db']
            
            logger.info(f"Normalizing volume to {target_db} dB")
            
            # Calculate current RMS
            rms = np.sqrt(np.mean(audio_data**2))
            
            if rms == 0:
                logger.warning("Audio RMS is 0, skipping normalization")
                return audio_data
            
            # Calculate current dB
            current_db = 20 * np.log10(rms)
            
            # Calculate gain needed
            gain_db = target_db - current_db
            gain_linear = 10 ** (gain_db / 20)
            
            # Apply gain
            normalized = audio_data * gain_linear
            
            # Prevent clipping
            max_val = np.max(np.abs(normalized))
            if max_val > 0.95:
                normalized = normalized * (0.95 / max_val)
            
            logger.info(f"Volume normalized (gain: {gain_db:.2f} dB)")
            return normalized
            
        except Exception as e:
            logger.warning(f"Normalization failed: {str(e)}, using original audio")
            return audio_data
    
    def enhance_voice(self, audio_data, sample_rate):
        """
        Apply voice enhancement (optional compression and EQ)
        
        Args:
            audio_data (np.array): Audio data
            sample_rate (int): Sample rate
        
        Returns:
            np.array: Enhanced audio
        """
        enhancement_config = self.refinement_config['enhancement']
        
        if not (enhancement_config['compression'] or enhancement_config['eq_boost']):
            logger.info("Voice enhancement disabled")
            return audio_data
        
        try:
            enhanced = audio_data.copy()
            
            # Simple compression (reduce dynamic range)
            if enhancement_config['compression']:
                logger.info("Applying gentle compression")
                threshold = 0.3
                ratio = 3.0
                
                # Apply compression above threshold
                mask = np.abs(enhanced) > threshold
                enhanced[mask] = np.sign(enhanced[mask]) * (
                    threshold + (np.abs(enhanced[mask]) - threshold) / ratio
                )
            
            # Simple EQ boost for voice frequencies (not implemented - would need scipy)
            # This is a placeholder for future enhancement
            if enhancement_config['eq_boost']:
                logger.info("EQ boost enabled (placeholder)")
            
            logger.info("Voice enhancement completed")
            return enhanced
            
        except Exception as e:
            logger.warning(f"Enhancement failed: {str(e)}, using original audio")
            return audio_data
    
    def save_refined(self, audio_data, sample_rate, output_path):
        """
        Save refined audio as WAV file
        
        Args:
            audio_data (np.array): Audio data
            sample_rate (int): Sample rate
            output_path (str): Output file path
        
        Returns:
            dict: Save result with file info
        """
        try:
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Get output settings
            target_sr = self.output_config['sample_rate']
            bit_depth = self.output_config['bit_depth']
            
            # Resample if needed
            if sample_rate != target_sr:
                logger.info(f"Resampling from {sample_rate}Hz to {target_sr}Hz")
                # Simple resampling (for better quality, use librosa.resample)
                from scipy import signal
                num_samples = int(len(audio_data) * target_sr / sample_rate)
                audio_data = signal.resample(audio_data, num_samples)
                sample_rate = target_sr
            
            # Convert to appropriate bit depth
            if bit_depth == 16:
                subtype = 'PCM_16'
            elif bit_depth == 24:
                subtype = 'PCM_24'
            else:
                subtype = 'PCM_32'
            
            # Save as WAV
            sf.write(
                output_path,
                audio_data,
                sample_rate,
                subtype=subtype
            )
            
            file_size = os.path.getsize(output_path)
            duration = len(audio_data) / sample_rate
            
            logger.info(f"Refined audio saved: {output_path} ({file_size/(1024*1024):.2f} MB, {duration:.2f}s)")
            
            return {
                'success': True,
                'file_path': output_path,
                'file_size': file_size,
                'duration': duration,
                'sample_rate': sample_rate,
                'error': None
            }
            
        except Exception as e:
            error_msg = f"Error saving refined audio: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'file_path': None,
                'file_size': 0,
                'duration': 0,
                'error': error_msg
            }
    
    def process_pipeline(self, input_path, output_path):
        """
        Complete audio refinement pipeline
        
        Args:
            input_path (str): Input audio file path
            output_path (str): Output audio file path
        
        Returns:
            dict: Processing result with metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting refinement pipeline: {input_path} -> {output_path}")
            
            # Step 1: Load audio
            audio_data, sample_rate = self.load_audio(input_path)
            input_duration = len(audio_data) / sample_rate
            
            # Step 2: Reduce noise
            audio_data = self.reduce_noise(audio_data, sample_rate)
            
            # Step 3: Normalize volume
            audio_data = self.normalize_volume(audio_data, self.refinement_config['normalization']['target_db'])
            
            # Step 4: Enhance voice
            audio_data = self.enhance_voice(audio_data, sample_rate)
            
            # Step 5: Save refined audio
            save_result = self.save_refined(audio_data, sample_rate, output_path)
            
            if not save_result['success']:
                return save_result
            
            processing_time = time.time() - start_time
            
            logger.info(f"Refinement pipeline completed in {processing_time:.2f}s")
            
            return {
                'success': True,
                'refined_audio_path': save_result['file_path'],
                'metadata': {
                    'input_duration': round(input_duration, 2),
                    'output_duration': round(save_result['duration'], 2),
                    'sample_rate': save_result['sample_rate'],
                    'processing_time': round(processing_time, 2),
                    'file_size': save_result['file_size']
                },
                'error': None
            }
            
        except Exception as e:
            error_msg = f"Refinement pipeline failed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'refined_audio_path': None,
                'metadata': None,
                'error': error_msg
            }