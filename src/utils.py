"""
Utility functions for the audio pipeline
"""

import os
import yaml
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

def load_config(config_path="config/config.yaml"):
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing config file: {e}")

def load_env_variables():
    """Load environment variables from .env file"""
    load_dotenv()
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    if not api_key:
        raise ValueError(
            "ELEVENLABS_API_KEY not found in environment variables. "
            "Please create a .env file with your API key."
        )
    
    return api_key

def setup_directories(config):
    """Create necessary directories if they don't exist"""
    directories = [
        config['paths']['raw_audio'],
        config['paths']['refined_audio'],
        config['paths']['logs']
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    logging.info(f"Directories verified: {', '.join(directories)}")

def setup_logging(config):
    """Configure logging based on config settings"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_format = log_config.get('format', '%(asctime)s - %(levelname)s - %(message)s')
    
    # Console handler
    handlers = [logging.StreamHandler()]
    
    # File handler if enabled
    if log_config.get('file_enabled', True):
        log_dir = config['paths']['logs']
        log_file = os.path.join(log_dir, f"audio_pipeline_{datetime.now().strftime('%Y%m%d')}.log")
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)

def generate_filename(prefix, extension, timestamp=True):
    """Generate a unique filename with optional timestamp"""
    if timestamp:
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{prefix}_{timestamp_str}.{extension}"
    return f"{prefix}.{extension}"

def get_file_size(file_path):
    """Get file size in MB"""
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)
    return 0

def validate_text_input(text, min_length=1, max_length=5000):
    """Validate text input for TTS"""
    if not text or not isinstance(text, str):
        raise ValueError("Text must be a non-empty string")
    
    text = text.strip()
    
    if len(text) < min_length:
        raise ValueError(f"Text too short. Minimum {min_length} characters required")
    
    if len(text) > max_length:
        raise ValueError(f"Text too long. Maximum {max_length} characters allowed")
    
    return text

def format_duration(seconds):
    """Format duration in seconds to human-readable format"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.2f}s"