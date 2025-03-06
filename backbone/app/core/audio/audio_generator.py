import os
import json
import logging
import time
import random
from typing import Dict, List, Union, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

from app.core.audio.abstract_audio_generator import AbstractAudioGenerator

# Configure logging
logger = logging.getLogger(__name__)

class AudioGenerator(AbstractAudioGenerator):
    """
    Generates audio files from text using ElevenLabs API.
    Implements the AbstractAudioGenerator interface.
    """
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict] = None):
        """
        Initialize the audio generator.
        
        Args:
            api_key: ElevenLabs API key (optional, will default to environment variable)
            config: Configuration options for audio generation
        """
        # Load environment variables if not already loaded
        load_dotenv()
        
        # Get API key from parameter, environment, or raise error
        self.api_key = api_key or os.getenv("EL")
        if not self.api_key:
            logger.warning("No ElevenLabs API key provided. Audio generation will not work.")
        
        # Default configuration
        self.config = {
            "voice_id": "hKUnzqLzU3P9IVhYHREu",  # Default voice
            "model_id": "eleven_flash_v2",       # Default model
            "stability": 0.5,
            "similarity_boost": 0.75,
            "speed": 1.15,
            "use_speaker_boost": True,
            "output_format": "mp3_44100_128",
            "audio_output_dir": "data/current",
            "max_workers": 4,                    # Reduced from 8 to 4 to prevent connection issues
            "max_retries": 3,                    # Number of retries for API calls
            "retry_delay": 2,                    # Initial delay between retries (in seconds)
            "max_retry_delay": 10,               # Maximum delay between retries (in seconds)
            "jitter": 0.5                        # Random jitter factor for retry delays
        }
        
        # Update default config with provided config
        if config:
            self.config.update(config)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.config["audio_output_dir"], exist_ok=True)
        
        # Lazy-load the ElevenLabs client when first needed
        self._client = None
    
    @property
    def client(self):
        """Get the ElevenLabs client, initializing it if needed."""
        if self._client is None and self.api_key:
            try:
                from elevenlabs.client import ElevenLabs
                self._client = ElevenLabs(api_key=self.api_key)
            except ImportError:
                logger.error("elevenlabs package is not installed. Please install it using: pip install elevenlabs")
                raise
        return self._client
    
    def _with_retry(self, func, *args, **kwargs):
        """
        Execute a function with retry logic for handling API connection issues.
        
        Args:
            func: Function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            The result of the function call
        """
        max_retries = self.config.get("max_retries", 3)
        base_delay = self.config.get("retry_delay", 2)
        max_delay = self.config.get("max_retry_delay", 10)
        jitter = self.config.get("jitter", 0.5)
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt}/{max_retries}...")
                
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    # Calculate exponential backoff with jitter
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    delay = delay * (1 + random.uniform(-jitter, jitter))
                    
                    # Log the error and retry information
                    logger.warning(f"Error during API call: {e}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {max_retries} retry attempts failed: {e}")
                    raise last_exception
    
    def generate_audio(self, text: str, output_path: Optional[str] = None) -> str:
        """
        Generate a single audio file from text.
        
        Args:
            text: Text to convert to audio
            output_path: Path to save the audio file (optional)
            
        Returns:
            str: Path to the generated audio file
        """
        # Check if client is available
        if not self.client:
            raise ValueError("ElevenLabs client is not initialized. Check API key.")
        
        # Check if output file already exists
        if output_path and os.path.exists(output_path):
            logger.info(f"Audio file already exists, skipping generation: {output_path}")
            return output_path
        
        try:
            logger.info(f"Generating audio for text: {text[:50]}{'...' if len(text) > 50 else ''}")
            
            # Set voice settings
            voice_settings = {
                "stability": self.config.get("stability", 0.5),
                "similarity_boost": self.config.get("similarity_boost", 0.75),
                "speed": self.config.get("speed", 1.15),
                "use_speaker_boost": self.config.get("use_speaker_boost", True)
            }
            
            # Convert text to speech with retry logic
            def _generate_audio():
                audio_generator = self.client.text_to_speech.convert(
                    text=text,
                    voice_id=self.config.get("voice_id"),
                    model_id=self.config.get("model_id"),
                    output_format=self.config.get("output_format"),
                    voice_settings=voice_settings
                )
                return b"".join(audio_generator)
            
            # Execute with retry
            audio_bytes = self._with_retry(_generate_audio)
            
            # Determine output path if not provided
            if not output_path:
                output_path = os.path.join(self.config["audio_output_dir"], f"audio_{os.urandom(4).hex()}.mp3")
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write audio bytes to file
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            
            logger.info(f"Generated audio file: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
    
    def batch_generate(self, entries: Union[Dict[str, str], List[Dict], List[tuple]]) -> List[str]:
        """
        Generate multiple audio files from a list of text entries.
        
        Args:
            entries: A dictionary with keys as file indexes and values as text,
                    or a list of dictionaries with 'index' and 'text' keys,
                    or a list of (index, text) tuples
                    
        Returns:
            List[str]: List of paths to generated audio files
        """
        # Standardize input format
        audio_entries = []
        
        if isinstance(entries, dict):
            # If entries is a dict mapping indexes to lines
            for idx, (key, text) in enumerate(entries.items(), 1):
                # Extract numeric index if possible, otherwise use current loop index
                if isinstance(key, str) and key.startswith('audio_') and key.endswith('.mp3'):
                    try:
                        index = int(key.split('_')[1].split('.')[0])
                    except (IndexError, ValueError):
                        index = idx
                else:
                    index = idx
                audio_entries.append({"index": index, "text": text})
        else:
            # If entries is a list
            for idx, entry in enumerate(entries, 1):
                if isinstance(entry, dict):
                    # Dict with text field
                    index = entry.get("index", idx)
                    text = entry.get("text") or entry.get("line")
                    if text:
                        audio_entries.append({"index": index, "text": text})
                elif isinstance(entry, tuple) and len(entry) >= 2:
                    # Tuple of (index, text)
                    audio_entries.append({"index": entry[0], "text": entry[1]})
        
        logger.info(f"Batch generating {len(audio_entries)} audio files")
        
        results = [None] * len(audio_entries)  # Pre-allocate results list
        failed_entries = []  # Track failed entries for retry
        
        # Use lower concurrency to prevent connection issues
        max_workers = min(self.config.get("max_workers", 4), 4)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {}
            
            for list_idx, entry in enumerate(audio_entries):
                index = entry["index"]
                text = entry["text"]
                output_path = os.path.join(self.config["audio_output_dir"], f"audio_{index}.mp3")
                
                # Skip if file already exists
                if os.path.exists(output_path):
                    logger.info(f"Audio file already exists, skipping: {output_path}")
                    results[list_idx] = output_path
                    continue
                
                # Submit task to thread pool
                future = executor.submit(self.generate_audio, text, output_path)
                future_to_idx[future] = list_idx
            
            # Collect results as they complete
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                entry = audio_entries[idx]
                try:
                    output_path = future.result()
                    results[idx] = output_path
                    logger.info(f"Successfully generated audio for index {entry['index']}")
                except Exception as e:
                    logger.error(f"Error in batch generation for index {entry['index']}: {e}")
                    failed_entries.append(entry)
        
        # Retry failed entries sequentially to avoid overwhelming the API
        if failed_entries:
            logger.info(f"Retrying {len(failed_entries)} failed entries sequentially...")
            for entry in failed_entries:
                index = entry["index"]
                text = entry["text"]
                output_path = os.path.join(self.config["audio_output_dir"], f"audio_{index}.mp3")
                
                try:
                    # Retry with longer timeout and exponential backoff
                    # Find the original index in audio_entries
                    for i, orig_entry in enumerate(audio_entries):
                        if orig_entry["index"] == index:
                            original_idx = i
                            break
                    else:
                        original_idx = -1
                    
                    # Try to generate again with more conservative settings
                    output_path = self.generate_audio(text, output_path)
                    if original_idx >= 0:
                        results[original_idx] = output_path
                except Exception as e:
                    logger.error(f"Final retry failed for index {index}: {e}")
        
        # Filter out None results
        valid_results = [r for r in results if r is not None]
        logger.info(f"Generated {len(valid_results)} audio files out of {len(audio_entries)} entries")
        
        return valid_results

    def generate_from_video_list(self, video_list_path: str) -> List[str]:
        """
        Generate audio files from a video_list.json file.
        
        Args:
            video_list_path: Path to the video_list.json file
            
        Returns:
            List[str]: List of paths to generated audio files
        """
        try:
            # Load the video list
            with open(video_list_path, 'r') as f:
                video_list = json.load(f)
            
            # Create a dictionary of entries to generate
            entries = {}
            for audio_file, data in video_list.items():
                # Extract index from audio filename (e.g., "audio_1.mp3" -> 1)
                if audio_file.startswith("audio_") and audio_file.endswith(".mp3"):
                    try:
                        index = int(audio_file.split("_")[1].split(".")[0])
                    except (IndexError, ValueError):
                        index = len(entries) + 1
                else:
                    index = len(entries) + 1
                    
                # Get the caption line from the data
                line = data.get("line", "")
                if not line:
                    logger.warning(f"No caption line found for {audio_file}, skipping")
                    continue
                
                entries[index] = line
            
            # Generate audio for all entries
            logger.info(f"Generating audio for {len(entries)} entries from video_list.json")
            
            # Convert dictionary to list of entries for batch_generate
            batch_entries = [{"index": idx, "text": text} for idx, text in entries.items()]
            
            # Generate audio files with reduced concurrency
            return self.batch_generate(batch_entries)
            
        except Exception as e:
            logger.error(f"Error generating audio from video_list: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return []
