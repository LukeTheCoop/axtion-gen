"""
Audio Processor Service

This module provides services for processing audio using ElevenLabs.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Set

from app.core.audio.audio_generator import AudioGenerator
from app.common.config import ConfigService

# Configure logging
logger = logging.getLogger(__name__)

class AudioProcessorService:
    """
    Service for processing audio using ElevenLabs.
    Handles audio generation for video captions.
    """
    
    def __init__(self, config_service: ConfigService):
        """
        Initialize the audio processor service.
        
        Args:
            config_service (ConfigService): Configuration service
        """
        self.config_service = config_service
        
        # Get audio configuration from config service
        audio_config = self.config_service.get("audio", {})
        
        # Initialize audio generator with config
        self._audio_generator = None
        self.audio_config = {
            "voice_id": audio_config.get("voice_id", "hKUnzqLzU3P9IVhYHREu"),
            "model_id": audio_config.get("model_id", "eleven_flash_v2"),
            "stability": audio_config.get("stability", 0.5),
            "similarity_boost": audio_config.get("similarity_boost", 0.75),
            "speed": audio_config.get("speed", 1.15),
            "use_speaker_boost": audio_config.get("use_speaker_boost", True),
            "output_format": audio_config.get("output_format", "mp3_44100_128"),
            "audio_output_dir": audio_config.get("output_directory", "data/current"),
            "max_workers": audio_config.get("max_concurrent_processes", 4),
            "max_retries": audio_config.get("max_retries", 3),
            "retry_delay": audio_config.get("retry_delay", 2),
            "max_retry_delay": audio_config.get("max_retry_delay", 10)
        }
    
    @property
    def audio_generator(self):
        """
        Get the audio generator, initializing it if needed.
        """
        if self._audio_generator is None:
            # Get API key from config or environment
            api_key = self.config_service.get("audio", {}).get("api_key") or os.getenv("EL")
            
            # Initialize audio generator
            self._audio_generator = AudioGenerator(api_key=api_key, config=self.audio_config)
            
        return self._audio_generator
    
    async def process_audio(self, video_list_path: str = None) -> List[str]:
        """
        Process audio generation from video_list.json.
        
        Args:
            video_list_path (str, optional): Path to video_list.json file
            
        Returns:
            List[str]: List of generated audio file paths
        """
        # Default video_list.json path
        if video_list_path is None:
            video_list_path = "data/current/video_list.json"
        
        # Check if video_list.json exists
        if not os.path.exists(video_list_path):
            logger.warning(f"Video list file not found: {video_list_path}")
            return []
        
        logger.info(f"Processing audio generation from {video_list_path}")
        
        # Ensure audio output directory exists
        audio_dir = self.audio_config["audio_output_dir"]
        os.makedirs(audio_dir, exist_ok=True)
        
        try:
            # Check and generate missing audio files
            generated_files = await self._ensure_audio_files(video_list_path)
            
            # Validate the generated files, log warnings for missing files
            all_audio_files = self._get_audio_files_from_video_list(video_list_path)
            missing_files = [f for f in all_audio_files if not os.path.exists(f)]
            
            if missing_files:
                logger.warning(f"Still missing {len(missing_files)} audio files after generation")
                for missing in missing_files:
                    logger.warning(f"Missing audio file: {missing}")
            else:
                logger.info("All required audio files are now available")
            
            # Return list of audio files generated/used
            return [f for f in all_audio_files if os.path.exists(f)]
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return []
    
    async def _ensure_audio_files(self, video_list_path: str) -> List[str]:
        """
        Ensure all required audio files exist, generating any missing ones.
        Prioritizes generation of earlier files in the sequence.
        
        Args:
            video_list_path (str): Path to video_list.json file
            
        Returns:
            List[str]: List of audio file paths
        """
        try:
            # Load video list
            with open(video_list_path, 'r') as f:
                video_list = json.load(f)
            
            # Check which audio files are missing
            audio_dir = self.audio_config["audio_output_dir"]
            missing_entries = {}
            existing_files = set()
            
            # First pass: identify existing and missing files
            for audio_file, data in video_list.items():
                # Get audio file path
                audio_path = os.path.join(audio_dir, audio_file)
                
                # Skip if audio file already exists
                if os.path.exists(audio_path):
                    logger.info(f"Audio file already exists: {audio_path}")
                    existing_files.add(audio_path)
                    continue
                
                # Get caption line
                line = data.get("line", "")
                if not line:
                    logger.warning(f"No caption line found for {audio_file}, skipping")
                    continue
                
                # Extract index for consistent naming
                if audio_file.startswith("audio_") and audio_file.endswith(".mp3"):
                    try:
                        index = int(audio_file.split("_")[1].split(".")[0])
                    except (IndexError, ValueError):
                        index = len(missing_entries) + 1
                else:
                    # Fall back to using file order if index can't be extracted
                    index = len(missing_entries) + 1
                
                # Add to missing entries
                missing_entries[index] = line
            
            # If there are missing entries, generate them
            if missing_entries:
                logger.info(f"Generating {len(missing_entries)} missing audio files")
                
                # Run in a background thread to avoid blocking the event loop
                import asyncio
                from concurrent.futures import ThreadPoolExecutor
                
                # Sort entries by index to prioritize earlier files
                sorted_entries = [{"index": idx, "text": text} for idx, text in 
                                  sorted(missing_entries.items(), key=lambda x: x[0])]
                
                with ThreadPoolExecutor() as executor:
                    # Run batch generation in a separate thread
                    result = await asyncio.get_event_loop().run_in_executor(
                        executor,
                        lambda: self.audio_generator.batch_generate(sorted_entries)
                    )
                
                logger.info(f"Generated {len(result)} audio files")
                return result
            else:
                logger.info("All audio files already exist")
                return list(existing_files)
                
        except Exception as e:
            logger.error(f"Error ensuring audio files: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _get_audio_files_from_video_list(self, video_list_path: str) -> List[str]:
        """
        Get a list of audio file paths from the video_list.json file.
        
        Args:
            video_list_path (str): Path to video_list.json file
            
        Returns:
            List[str]: List of audio file paths
        """
        try:
            # Load video list
            with open(video_list_path, 'r') as f:
                video_list = json.load(f)
            
            # Get audio file paths
            audio_dir = self.audio_config["audio_output_dir"]
            audio_files = []
            
            for audio_file in video_list.keys():
                audio_path = os.path.join(audio_dir, audio_file)
                audio_files.append(audio_path)
            
            return audio_files
            
        except Exception as e:
            logger.error(f"Error getting audio files from video list: {e}")
            return []
    
    def get_existing_audio_files(self, video_list_path: str = None) -> Set[str]:
        """
        Get a set of audio file paths that actually exist on disk
        from the video_list.json file.
        
        Args:
            video_list_path (str, optional): Path to video_list.json file
            
        Returns:
            Set[str]: Set of existing audio file paths
        """
        if video_list_path is None:
            video_list_path = "data/current/video_list.json"
            
        if not os.path.exists(video_list_path):
            return set()
            
        all_files = self._get_audio_files_from_video_list(video_list_path)
        return {f for f in all_files if os.path.exists(f)} 