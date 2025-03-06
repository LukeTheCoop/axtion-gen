"""
Video Processing Pipeline Implementation

This module implements the AsyncVideoProcessingPipeline class for processing videos.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional

from app.core.ffmpeg.interfaces import (
    FFmpegCommandExecutor,
    VideoMetadataService,
    AudioVideoMerger,
    SplitCaptionAdder,
    VideoConcatenator,
    VideoProcessingPipeline
)

logger = logging.getLogger(__name__)

class AsyncVideoProcessingPipeline:
    """
    Implementation of the VideoProcessingPipeline interface.
    Coordinates multiple video processing operations using async methods.
    """
    
    def __init__(
        self,
        command_executor: FFmpegCommandExecutor,
        metadata_service: VideoMetadataService,
        audio_video_merger: AudioVideoMerger,
        split_caption_adder: SplitCaptionAdder,
        concatenator: VideoConcatenator,
        max_concurrent_tasks: int = 4
    ):
        """
        Initialize the pipeline with the necessary components.
        
        Args:
            command_executor: Executor for FFmpeg commands
            metadata_service: Service for retrieving video metadata
            audio_video_merger: Component for merging audio and video
            split_caption_adder: Component for adding split captions
            concatenator: Component for concatenating videos
            max_concurrent_tasks: Maximum number of concurrent tasks
        """
        self.command_executor = command_executor
        self.metadata_service = metadata_service
        self.audio_video_merger = audio_video_merger
        self.split_caption_adder = split_caption_adder
        self.concatenator = concatenator
        self.max_concurrent_tasks = max_concurrent_tasks
        
        # Configuration for captions
        self.font_size = 24
        self.caption_position = "bottom"  # or "top"
        self.output_dir = "./output"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _ensure_valid_filename(self, filename: str, default_ext: str = ".mp4") -> str:
        """
        Ensure the filename has a valid extension and is a valid filename.
        
        Args:
            filename: The filename to validate
            default_ext: Default extension to add if missing
            
        Returns:
            str: Valid filename with extension
        """
        if not filename:
            return f"output{default_ext}"
            
        # Ensure filename has extension
        base, ext = os.path.splitext(filename)
        if not ext:
            filename = f"{base}{default_ext}"
            
        # Replace invalid characters in filename
        filename = os.path.basename(filename)
        
        return filename
    
    async def process_videos(self, video_data: Dict[str, Dict[str, Any]], input_video: str = None) -> List[str]:
        """
        Process multiple videos in parallel.
        
        Args:
            video_data: Dictionary mapping audio files to their processing data
                        {audio_file: {"line": caption_text, "source_video": video_path, "clip": clip_name}}
            input_video: Optional reference video for formatting
            
        Returns:
            List[str]: List of processed video file paths
        """
        logger.info(f"Starting processing of {len(video_data)} videos with max {self.max_concurrent_tasks} concurrent tasks")
        
        # Create output directory if not exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create tasks in batches to limit concurrent processing
        semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        tasks = []
        processed_videos = []
        
        async def process_single_video(audio_file, data):
            async with semaphore:
                try:
                    # Extract data
                    line = data.get("line", "")
                    source_video = data.get("source_video", input_video)
                    
                    # Determine output filename (using clip name if available)
                    clip_name = data.get("clip", None)
                    audio_basename = os.path.basename(audio_file).split('.')[0]
                    
                    if clip_name:
                        # Use the clip name from video_list.json
                        # Ensure clip name is valid and has an extension
                        clip_name = self._ensure_valid_filename(clip_name)
                        
                        merged_output = os.path.join(self.output_dir, f"merged_{clip_name}")
                        final_output = os.path.join(self.output_dir, clip_name)
                    else:
                        # Fall back to using the audio filename
                        merged_output = os.path.join(self.output_dir, f"merged_{audio_basename}.mp4")
                        final_output = os.path.join(self.output_dir, f"final_{audio_basename}.mp4")
                    
                    # Step 1: Merge audio and video
                    logger.info(f"Merging audio {audio_file} with video {source_video}")
                    merged = await self.audio_video_merger.process(
                        audio_file=audio_file,
                        video_file=source_video,
                        output_file=merged_output
                    )
                    
                    # Step 2: Add captions
                    logger.info(f"Adding captions to {merged}")
                    captioned = await self.split_caption_adder.process(
                        input_file=merged,
                        captions=line,
                        output_file=final_output,
                        position=self.caption_position,
                        font_size=self.font_size
                    )
                    
                    # Return final video path
                    return captioned
                except Exception as e:
                    logger.error(f"Error processing video with audio {audio_file}: {e}")
                    return None
        
        # Create tasks for each video
        for audio_file, data in video_data.items():
            tasks.append(process_single_video(audio_file, data))
        
        # Run all tasks and collect results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        for result in results:
            if result and not isinstance(result, Exception) and os.path.exists(result):
                processed_videos.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Task failed with exception: {result}")
        
        logger.info(f"Completed processing {len(processed_videos)} videos successfully")
        return processed_videos
    
    async def concatenate_videos(self, video_files: List[str], output_file: str, project_id: str = None) -> str:
        """
        Concatenate multiple videos into a single video.
        
        Args:
            video_files: List of video files to concatenate
            output_file: Path where the concatenated video will be saved
            project_id: Optional project ID for organizing output
            
        Returns:
            str: Path to the concatenated video
        """
        if not video_files:
            logger.warning("No videos to concatenate")
            return None
        
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Ensure output file has extension
            output_file = self._ensure_valid_filename(output_file)
            
            # Add full path if not already present
            if not os.path.dirname(output_file):
                output_file = os.path.join(self.output_dir, output_file)
            
            # Concatenate videos
            logger.info(f"Concatenating {len(video_files)} videos into {output_file}")
            result = await self.concatenator.process(video_files, output_file, project_id)
            
            return result
        except Exception as e:
            logger.error(f"Error concatenating videos: {e}")
            return None 