"""
Video Metadata Service

This module provides services for retrieving video metadata.
"""

import json
import logging
from typing import Dict, Any, Optional, Tuple

from app.core.ffmpeg.interfaces import VideoMetadataService, FFmpegCommandExecutor

logger = logging.getLogger(__name__)

class AsyncVideoMetadataService(VideoMetadataService):
    """
    Asynchronous implementation of VideoMetadataService.
    Uses FFprobe to retrieve metadata about video files.
    """
    
    def __init__(self, command_executor: FFmpegCommandExecutor):
        """
        Initialize the service.
        
        Args:
            command_executor: Command executor for running FFprobe
        """
        self.command_executor = command_executor
    
    async def get_duration(self, video_file: str) -> float:
        """
        Get the duration of a video in seconds.
        
        Args:
            video_file: Path to the video file
            
        Returns:
            float: Duration in seconds
        """
        cmd = f"ffprobe -v error -show_entries format=duration -of json {video_file}"
        output = await self.command_executor.execute(cmd)
        
        try:
            data = json.loads(output)
            return float(data['format']['duration'])
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error getting video duration: {e}")
            # Return a default duration if we can't determine it
            return 10.0
    
    async def get_resolution(self, video_file: str) -> tuple:
        """
        Get the resolution of a video.
        
        Args:
            video_file: Path to the video file
            
        Returns:
            tuple: (width, height)
        """
        cmd = f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of json {video_file}"
        output = await self.command_executor.execute(cmd)
        
        try:
            data = json.loads(output)
            stream = data['streams'][0]
            return (int(stream['width']), int(stream['height']))
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Error getting video resolution: {e}")
            # Return a default resolution if we can't determine it
            return (1920, 1080)
    
    async def get_codec(self, video_file: str) -> str:
        """
        Get the codec of a video.
        
        Args:
            video_file: Path to the video file
            
        Returns:
            str: The codec name
        """
        cmd = f"ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of json {video_file}"
        output = await self.command_executor.execute(cmd)
        
        try:
            data = json.loads(output)
            return data['streams'][0]['codec_name']
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Error getting video codec: {e}")
            return "unknown"
    
    async def get_full_info(self, video_file: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a video file.
        
        Args:
            video_file: Path to the video file
            
        Returns:
            Dict[str, Any]: Comprehensive video information
        """
        cmd = f"ffprobe -v error -show_format -show_streams -of json {video_file}"
        output = await self.command_executor.execute(cmd)
        
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing video information: {e}")
            return {} 