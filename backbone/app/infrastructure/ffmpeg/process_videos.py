"""
Video Processing Pipeline

This module provides functionality for processing multiple videos concurrently.
"""

import asyncio
from typing import Dict, List, Tuple, Any
import json
from .ffmpeg_utils import check_ffmpeg, run_ffmpeg_command

from app.core.ffmpeg.interfaces import (
    VideoProcessingPipeline,
    AudioVideoMerger,
    SplitCaptionAdder
)

async def run_ffmpeg_command(cmd: List[str], task_description: str) -> str:
    """
    Run an FFmpeg command asynchronously.
    
    Args:
        cmd (List[str]): Command to run
        task_description (str): Description of the task for logging
        
    Returns:
        str: Output of the command
        
    Raises:
        RuntimeError: If the command fails
    """
    # Use ThreadPoolExecutor since subprocess calls are blocking
    loop = asyncio.get_event_loop()
    
    logger.info(f"Starting: {task_description}")
    
    try:
        # Run subprocess in a thread pool to avoid blocking the event loop
        process = await loop.run_in_executor(
            None,
            lambda: subprocess.run(cmd, check=True, capture_output=True, text=True)
        )
        logger.info(f"Completed: {task_description}")
        return process.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error in {task_description}: {e}")
        logger.error(f"FFmpeg stderr: {e.stderr}")
        raise RuntimeError(f"Failed in {task_description}: {e}")


async def get_video_info(video_path: str) -> Dict:
    """
    Get detailed information about a video file using FFprobe asynchronously.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        Dict: A dictionary containing video metadata
    """
    check_ffmpeg()
    
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path
    ]
    
    result = await run_ffmpeg_command(cmd, f"Getting video info: {video_path}")
    return json.loads(result)


async def get_video_duration(video_path: str) -> float:
    """
    Get the duration of a video file in seconds asynchronously.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        float: Duration of the video in seconds
    """
    info = await get_video_info(video_path)
    return float(info['format']['duration'])


class AsyncVideoProcessingPipeline(VideoProcessingPipeline):
    """
    Asynchronous implementation of VideoProcessingPipeline.
    Processes multiple videos concurrently using asyncio.
    """
    
    def __init__(self, audio_video_merger: AudioVideoMerger, caption_adder: SplitCaptionAdder):
        """
        Initialize the pipeline with necessary operations.
        
        Args:
            audio_video_merger (AudioVideoMerger): For merging audio and video
            caption_adder (SplitCaptionAdder): For adding captions to video
        """
        self.audio_video_merger = audio_video_merger
        self.caption_adder = caption_adder
    
    async def process_video(self, video_data: Dict[str, Any], input_video: str) -> str:
        """
        Process a single video through the pipeline.
        
        Args:
            video_data (Dict): Data for processing the video, includes audio and caption
            input_video (str): Path to the input video template
            
        Returns:
            str: Path to the processed video
        """
        # Extract data
        audio_file = video_data.get("audio_file", "")
        line = video_data.get("line", "")
        
        # Determine output file names
        video_name = f'{audio_file.split("_")[1].split(".")[0]}.mp4'
        final_video_name = f'final_{video_name}'
        
        # Step 1: Merge audio and video
        await self.audio_video_merger.process(input_video, audio_file, video_name)
        
        # Step 2: Add split caption
        await self.caption_adder.process(video_name, line, final_video_name)
        
        return final_video_name
    
    async def process_videos(self, video_list: Dict[str, Dict[str, Any]], input_video: str) -> List[str]:
        """
        Process multiple videos concurrently using asyncio.
        
        Args:
            video_list (Dict): Dictionary mapping audio files to data
            input_video (str): Path to the input video template
            
        Returns:
            List[str]: List of processed video file paths
        """
        tasks = []
        
        # Create a task for each video to process
        for audio_file, data in video_list.items():
            # Make sure the data has the audio_file field
            data["audio_file"] = audio_file
            
            task = asyncio.create_task(self.process_video(data, input_video))
            tasks.append(task)
        
        # Wait for all tasks to complete
        processed_videos = await asyncio.gather(*tasks)
        
        return processed_videos
