"""
Video Processor Service

This module provides services for processing videos using the async FFmpeg infrastructure.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional

from app.infrastructure.ffmpeg import create_pipeline, configure_ffmpeg, create_youtube_audio_merger
from app.common.config import ConfigService
from app.api.services.audio_processor import AudioProcessorService

# Configure logging
logger = logging.getLogger(__name__)

class VideoProcessorService:
    """
    Service for processing videos using FFmpeg.
    Handles video and audio merging, adding captions, and other video operations.
    """
    
    def __init__(self, config_service: ConfigService):
        """
        Initialize the video processor service.
        
        Args:
            config_service (ConfigService): Configuration service
        """
        self.config_service = config_service
        
        # Get FFmpeg configuration from config service
        ffmpeg_config = self.config_service.get("ffmpeg", {})
        self.max_concurrent_processes = ffmpeg_config.get("max_concurrent_processes", 4)
        
        # Configure FFmpeg with our settings
        configure_ffmpeg(max_concurrent_processes=self.max_concurrent_processes)
        
        # Create video processing pipeline
        self._pipeline = None
        
        # Create audio processor service
        self._audio_processor = None
    
    @property
    def pipeline(self):
        """
        Get the video processing pipeline.
        Lazy initialization to ensure it's created when needed.
        """
        if self._pipeline is None:
            ffmpeg_config = {
                "max_concurrent_processes": self.max_concurrent_processes,
                "font_size": self.config_service.get("ffmpeg", {}).get("font_size", 24),
                "position": self.config_service.get("ffmpeg", {}).get("position", "bottom")
            }
            self._pipeline = create_pipeline(ffmpeg_config)
        return self._pipeline
    
    @property
    def audio_processor(self):
        """
        Get the audio processor service.
        Lazy initialization to ensure it's created when needed.
        """
        if self._audio_processor is None:
            self._audio_processor = AudioProcessorService(self.config_service)
        return self._audio_processor
    
    def _get_youtube_audio_merger(self):
        """
        Get a YouTube audio merger instance.
        
        Returns:
            YouTubeAudioMerger: A YouTube audio merger
        """
        return create_youtube_audio_merger()
    
    async def process_videos(self, prompts_data: Dict[str, str] = None, genre: Optional[str] = None, project_id: str = None, options: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Process videos by merging with audio and adding captions.
        Uses video_list.json if available, otherwise falls back to dynamic pairing.
        
        Args:
            prompts_data (Dict[str, str], optional): Dictionary mapping prompt IDs to prompt text
            genre (str, optional): Genre for selecting videos. If None, uses default from config.
            project_id (str, optional): Project ID for organizing output files
            options (Dict[str, Any], optional): Additional processing options
            
        Returns:
            List[str]: List of processed video file paths
        """
        # Determine genre - use default if not provided
        if genre is None:
            genre = self.config_service.get("default_genre", "military")
        
        # If project_id is not provided, create one using genre and timestamp
        if project_id is None and genre:
            import time
            project_id = f"{genre}_{int(time.time())}"
        
        logger.info("========== STARTING VIDEO PROCESSING PIPELINE ==========")
        logger.info(f"Genre: {genre}, Project ID: {project_id}")
        
        # Extract YouTube audio options 
        youtube_audio = None
        
        # First check if it was provided in options
        if options and "youtube_audio" in options:
            youtube_audio = options.get("youtube_audio")
            logger.info(f"YouTube audio options provided in request: {youtube_audio}")
        # If not provided in options, check youtube_audio config
        else:
            config_youtube_audio = self.config_service.get_youtube_audio_config()
            if config_youtube_audio and "url" in config_youtube_audio:
                youtube_audio = config_youtube_audio
                logger.info(f"YouTube audio options found in config: {youtube_audio}")
            # If no youtube_audio config, check music config for track_id
            else:
                music_config = self.config_service.get_music_config()
                if music_config and "track_id" in music_config:
                    track_id = music_config.get("track_id")
                    if track_id:
                        # Convert music config to youtube_audio format
                        youtube_audio = {
                            "url": f"https://www.youtube.com/watch?v={track_id}",
                            "volume": music_config.get("volume", 0.5)
                        }
                        
                        # Handle start_time conversion from "M:SS" to seconds if needed
                        start_time = music_config.get("start_time", "0:00")
                        if isinstance(start_time, str) and ":" in start_time:
                            try:
                                minutes, seconds = start_time.split(":")
                                start_time_seconds = float(minutes) * 60 + float(seconds)
                                youtube_audio["start_time"] = start_time_seconds
                            except Exception as e:
                                logger.error(f"Error converting music start_time '{start_time}' to seconds: {e}")
                                youtube_audio["start_time"] = 0.0
                        else:
                            youtube_audio["start_time"] = float(start_time) if start_time else 0.0
                        
                        # Add trim_audio parameter from music config
                        if "trim_audio" in music_config:
                            youtube_audio["trim_audio"] = float(music_config.get("trim_audio"))
                            
                        logger.info(f"Using music track_id '{track_id}' as YouTube audio: {youtube_audio}")
        
        logger.info("====== PROCESS STEP 1: PREPARE AUDIO FILES ======")
        # Construct paths
        audio_dir = "data/current"
        videos_dir = f"data/media/videos/{genre}"
        video_list_path = os.path.join(audio_dir, "video_list.json")
        
        # Step 1: Generate audio files from video_list.json if it exists
        available_audio_files = set()
        if os.path.exists(video_list_path):
            logger.info(f"Found video_list.json at {video_list_path}, generating audio files")
            try:
                # Generate any missing audio files
                generated_files = await self.audio_processor.process_audio(video_list_path)
                available_audio_files = set(generated_files)
                
                if not available_audio_files:
                    logger.warning("No audio files were successfully generated")
                else:
                    logger.info(f"Audio generation complete, {len(available_audio_files)} files available")
            except Exception as e:
                logger.error(f"Error generating audio files: {e}")
                import traceback
                logger.debug(f"Traceback: {traceback.format_exc()}")
                # Continue with processing even if audio generation fails
                
                # Get any existing audio files
                available_audio_files = self.audio_processor.get_existing_audio_files(video_list_path)
                logger.info(f"Found {len(available_audio_files)} existing audio files to use")
        
        logger.info("====== PROCESS STEP 2: CREATE INDIVIDUAL VIDEOS WITH CAPTIONS ======")
        # Step 2: Process videos
        processed_videos = []
        if os.path.exists(video_list_path):
            # Use video_list.json for processing, but only process videos with available audio
            logger.info(f"Using video_list.json for video processing")
            processed_videos = await self._process_from_video_list(
                video_list_path, 
                audio_dir, 
                videos_dir, 
                available_audio_files
            )
        else:
            # Fall back to dynamic pairing
            logger.info("No video_list.json found, falling back to dynamic pairing")
            processed_videos = await self._process_dynamic_pairing(prompts_data, audio_dir, videos_dir)
        
        logger.info("====== PROCESS STEP 3: CONCATENATE VIDEOS AND ADD YOUTUBE AUDIO ======")
        # Step 3: Concatenate all videos into a single final video
        if processed_videos and len(processed_videos) > 0:
            logger.info(f"All videos processed. Creating final concatenated video with project_id: {project_id}")
            
            # Define output path for the final video
            output_dir = f"./data/media/output/{project_id}"
            output_file = f"final_{genre}_video.mp4"
            final_output_path = os.path.join(output_dir, output_file)
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            try:
                # Concatenate all processed videos and apply YouTube audio if provided
                final_video = await self.concatenate_videos(
                    processed_videos, 
                    final_output_path, 
                    project_id,
                    youtube_audio
                )
                logger.info(f"Successfully created final concatenated video: {final_video}")
                
                # Add the final video to the processed videos list
                if final_video and final_video not in processed_videos:
                    processed_videos.append(final_video)
            except Exception as e:
                logger.error(f"Failed to create final concatenated video: {e}")
                import traceback
                logger.debug(f"Traceback: {traceback.format_exc()}")
        else:
            logger.warning("No videos were processed, cannot create final concatenated video")
        
        logger.info("========== VIDEO PROCESSING PIPELINE COMPLETE ==========")
        return processed_videos
    
    async def _process_from_video_list(
        self, 
        video_list_path: str, 
        audio_dir: str, 
        videos_dir: str,
        available_audio_files: Optional[set] = None
    ) -> List[str]:
        """
        Process videos using the mapping in video_list.json
        
        Args:
            video_list_path: Path to video_list.json
            audio_dir: Directory containing audio files
            videos_dir: Directory containing source videos
            available_audio_files: Set of available audio file paths
            
        Returns:
            List[str]: List of processed video file paths
        """
        # Load the video_list.json file
        try:
            with open(video_list_path, 'r') as f:
                video_list = json.load(f)
        except Exception as e:
            logger.error(f"Error loading video_list.json: {e}")
            raise
        
        # If available_audio_files is not provided, get all existing files
        if available_audio_files is None:
            available_audio_files = set()
            for audio_file in video_list.keys():
                audio_path = os.path.join(audio_dir, audio_file)
                if os.path.exists(audio_path):
                    available_audio_files.add(audio_path)
        
        # Prepare data for processing
        video_data = {}
        for audio_file, data in video_list.items():
            # Get full paths
            audio_path = os.path.join(audio_dir, audio_file)
            video_path = os.path.join(videos_dir, data["source_video"])
            
            # Skip if audio file doesn't exist
            if audio_path not in available_audio_files:
                logger.warning(f"Audio file not found or not valid: {audio_path}")
                continue
                
            # Skip if video file doesn't exist
            if not os.path.exists(video_path):
                logger.warning(f"Video file not found: {video_path}")
                continue
                
            # Add to processing data
            video_data[audio_path] = {
                "line": data["line"],
                "source_video": video_path,
                "clip": data.get("clip", None)  # Include clip name if available
            }
        
        if not video_data:
            logger.warning("No valid audio-video pairs found in video_list.json")
            return []
            
        logger.info(f"Preparing to process {len(video_data)} videos from video_list.json")
        
        # Process each video
        return await self._process_video_data(video_data)
    
    async def _process_dynamic_pairing(self, prompts_data: Dict[str, str], audio_dir: str, videos_dir: str) -> List[str]:
        """
        Process videos by dynamically pairing audio files with videos.
        
        Args:
            prompts_data: Dictionary of prompts (creative, polish, etc.)
            audio_dir: Directory containing audio files
            videos_dir: Directory containing source videos
            
        Returns:
            List[str]: List of processed video file paths
        """
        # Check if we have prompts data
        if not prompts_data:
            logger.warning("No prompts data provided for dynamic pairing")
            return []
            
        # Check if videos directory exists
        if not os.path.exists(videos_dir):
            logger.warning(f"Videos directory not found: {videos_dir}")
            return []
            
        # Get all videos in the directory
        video_files = [
            os.path.join(videos_dir, f) 
            for f in os.listdir(videos_dir) 
            if f.endswith(('.mp4', '.mov', '.avi'))
        ]
        
        if not video_files:
            logger.warning(f"No video files found in {videos_dir}")
            return []
            
        # Get all audio files
        audio_files = []
        if os.path.exists(audio_dir):
            audio_files = [
                os.path.join(audio_dir, f)
                for f in os.listdir(audio_dir)
                if f.endswith('.mp3') and os.path.exists(os.path.join(audio_dir, f))
            ]
        
        # Prepare dynamic pairing of audio and video
        video_data = {}
        
        if audio_files:
            # If we have audio files, pair each with a video
            for i, audio_file in enumerate(audio_files):
                # Select a video file (cycling through available videos)
                video_index = i % len(video_files)
                video_file = video_files[video_index]
                
                # Add to processing data
                video_data[audio_file] = {
                    "line": f"Caption {i+1}",  # Default caption
                    "source_video": video_file
                }
        else:
            # If no audio files, create text captions from prompts
            caption_text = ""
            if "creative" in prompts_data:
                caption_text = prompts_data["creative"]
            elif "polish" in prompts_data:
                caption_text = prompts_data["polish"]
                
            # Split caption text into sentences
            import re
            sentences = re.split(r'(?<=[.!?])\s+', caption_text)
            
            # Pair each sentence with a video
            for i, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue
                    
                # Select a video file (cycling through available videos)
                video_index = i % len(video_files)
                video_file = video_files[video_index]
                
                # Add to processing data
                pseudo_audio_file = f"caption_{i+1}"  # No real audio file
                video_data[pseudo_audio_file] = {
                    "line": sentence.strip(),
                    "source_video": video_file,
                    "no_audio": True  # Flag to indicate no audio merging
                }
        
        logger.info(f"Dynamically paired {len(video_data)} videos for processing")
        
        # Process each video
        return await self._process_video_data(video_data)
    
    async def _process_video_data(self, video_data: Dict[str, Dict]) -> List[str]:
        """
        Process videos based on the provided data.
        
        Args:
            video_data: Dictionary mapping audio files to video data
            
        Returns:
            List[str]: List of processed video file paths
        """
        # Process videos using the pipeline
        processed_videos = []
        
        try:
            # Start the video processing pipeline
            processed_videos = await self.pipeline.process_videos(video_data)
            logger.info(f"Successfully processed {len(processed_videos)} videos")
        except Exception as e:
            logger.error(f"Error processing videos: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
        
        return processed_videos
    
    async def apply_youtube_audio(self, video_path: str, youtube_url: str, output_path: str = None, 
                                 start_time: float = 0.0, trim_audio: float = 0.0, volume: float = 1.0) -> str:
        """
        Apply YouTube audio to a video.
        
        Args:
            video_path: Path to the input video
            youtube_url: YouTube URL to download audio from
            output_path: Path to save the output video (optional)
            start_time: Start time in seconds to begin the audio in the video
            trim_audio: Trim the beginning of the YouTube audio by this many seconds
            volume: Volume of the YouTube audio (0.0-1.0)
            
        Returns:
            str: Path to the processed video
        """
        logger.info(f"===== YOUTUBE AUDIO PROCESSING =====")
        logger.info(f"STEP 1: PREPARING TO DOWNLOAD AUDIO from {youtube_url}")
        logger.info(f"  - Input video: {video_path}")
        logger.info(f"  - Audio settings: start_time={start_time}s, trim_audio={trim_audio}s, volume={volume}")
        
        if not os.path.exists(video_path):
            logger.error(f"ERROR: Video file does not exist: {video_path}")
            return None
            
        # Create YouTube audio merger
        youtube_merger = self._get_youtube_audio_merger()
        
        # If output path is not provided, create one
        if output_path is None:
            video_dir = os.path.dirname(video_path)
            video_name = os.path.basename(video_path)
            output_path = os.path.join(video_dir, f"youtube_audio_{video_name}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        logger.info(f"STEP 2: OUTPUT WILL BE SAVED TO {output_path}")
        
        # Process the video with YouTube audio
        try:
            logger.info(f"STEP 3: DOWNLOADING AND MERGING YOUTUBE AUDIO")
            result = await youtube_merger.process(
                video_file=video_path,
                youtube_url=youtube_url,
                output_file=output_path,
                start_time=start_time,
                trim_audio=trim_audio,
                volume=volume
            )
            logger.info(f"STEP 4: SUCCESSFULLY COMPLETED YOUTUBE AUDIO PROCESSING")
            logger.info(f"  - Final output: {result}")
            return result
        except Exception as e:
            logger.error(f"ERROR DURING YOUTUBE AUDIO PROCESSING: {e}")
            logger.warning(f"Falling back to original video: {video_path}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return video_path
            
    async def concatenate_videos(self, video_files: List[str], output_path: str, project_id: str = None, 
                               youtube_audio: Optional[Dict[str, Any]] = None) -> str:
        """
        Concatenate multiple videos into a single file.
        Optionally apply YouTube audio to the final video.
        
        Args:
            video_files: List of video file paths to concatenate
            output_path: Path for the final concatenated video
            project_id: Optional project ID for organizing output
            youtube_audio: Optional YouTube audio configuration:
                           {
                               "url": "YouTube URL",
                               "start_time": 0.0,
                               "trim_audio": 0.0,
                               "volume": 1.0
                           }
            
        Returns:
            str: Path to the concatenated video
        """
        if not video_files:
            logger.warning("No video files provided for concatenation")
            return None
            
        try:
            # Define output directory for project
            output_dir = os.path.dirname(output_path)
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # STEP 1: CONCATENATION
            logger.info(f"STEP 1: CONCATENATING {len(video_files)} videos into {output_path}")
            
            # Use the pipeline to concatenate videos
            final_video_path = await self.pipeline.concatenate_videos(
                video_files, 
                output_path,
                project_id=project_id
            )
            
            # STEP 2: PREPARE YOUTUBE AUDIO CONFIGURATION
            logger.info("STEP 2: PREPARING YOUTUBE AUDIO")
            
            # If YouTube audio wasn't provided in parameters, check config
            if not youtube_audio:
                config_youtube_audio = self.config_service.get_youtube_audio_config()
                if config_youtube_audio and "url" in config_youtube_audio:
                    youtube_audio = config_youtube_audio
                    logger.info(f"Using YouTube audio from config: {youtube_audio}")
                # If no youtube_audio config, check music config for track_id
                else:
                    music_config = self.config_service.get_music_config()
                    if music_config and "track_id" in music_config:
                        track_id = music_config.get("track_id")
                        if track_id:
                            # Convert music config to youtube_audio format
                            youtube_audio = {
                                "url": f"https://www.youtube.com/watch?v={track_id}",
                                "volume": music_config.get("volume", 0.5)
                            }
                            
                            # Handle start_time conversion from "M:SS" to seconds if needed
                            start_time = music_config.get("start_time", "0:00")
                            if isinstance(start_time, str) and ":" in start_time:
                                try:
                                    minutes, seconds = start_time.split(":")
                                    start_time_seconds = float(minutes) * 60 + float(seconds)
                                    youtube_audio["start_time"] = start_time_seconds
                                except Exception as e:
                                    logger.error(f"Error converting music start_time '{start_time}' to seconds: {e}")
                                    youtube_audio["start_time"] = 0.0
                            else:
                                youtube_audio["start_time"] = float(start_time) if start_time else 0.0
                                
                            # Add trim_audio parameter from music config
                            if "trim_audio" in music_config:
                                youtube_audio["trim_audio"] = float(music_config.get("trim_audio"))
                            
                            logger.info(f"Using music track_id '{track_id}' as YouTube audio: {youtube_audio}")
            
            # STEP 3: APPLY YOUTUBE AUDIO AND CREATE FINAL OUTPUT
            if youtube_audio and final_video_path:
                youtube_url = youtube_audio.get("url")
                if youtube_url:
                    logger.info(f"STEP 3: APPLYING YOUTUBE AUDIO from {youtube_url} to concatenated video")
                    # Create a temporary path for the intermediate version
                    temp_path = final_video_path.replace(".mp4", "_temp.mp4")
                    
                    # Rename the final video to a temporary name
                    os.rename(final_video_path, temp_path)
                    
                    # Apply YouTube audio
                    final_video_path = await self.apply_youtube_audio(
                        video_path=temp_path,
                        youtube_url=youtube_url,
                        output_path=final_video_path,
                        start_time=youtube_audio.get("start_time", 0.0),
                        trim_audio=youtube_audio.get("trim_audio", 0.0),
                        volume=youtube_audio.get("volume", 1.0)
                    )
                    
                    # Clean up temporary file
                    if os.path.exists(temp_path) and final_video_path != temp_path:
                        try:
                            os.remove(temp_path)
                            logger.info("Temporary concatenated file removed after adding YouTube audio")
                        except Exception as e:
                            logger.warning(f"Failed to clean up temporary file: {e}")
                    
                    logger.info(f"STEP 4: FINAL OUTPUT CREATED at {final_video_path}")
            else:
                logger.info(f"STEP 3: NO YOUTUBE AUDIO APPLIED. FINAL OUTPUT at {final_video_path}")
            
            return final_video_path
            
        except Exception as e:
            logger.error(f"Error concatenating videos: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return None 