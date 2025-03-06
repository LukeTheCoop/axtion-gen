"""
Audio Video Merger

This module provides functionality for merging audio and video files.
"""

import os
import logging
from typing import Optional

from app.core.ffmpeg.interfaces import AudioVideoMerger, FFmpegCommandExecutor

logger = logging.getLogger(__name__)

class AsyncAudioVideoMerger(AudioVideoMerger):
    """
    Asynchronous implementation of AudioVideoMerger.
    Merges audio and video files using FFmpeg.
    """
    
    def __init__(self, command_executor: FFmpegCommandExecutor):
        """
        Initialize the merger.
        
        Args:
            command_executor: Command executor for running FFmpeg
        """
        self.command_executor = command_executor
    
    async def process(self, audio_file: str, video_file: str, output_file: str) -> str:
        """
        Merge audio and video files.
        
        Args:
            audio_file: Path to the audio file
            video_file: Path to the video file
            output_file: Path to save the merged file
            
        Returns:
            str: Path to the merged file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        logger.info(f"Merging audio {audio_file} with video {video_file} to {output_file}")
        
        # Construct FFmpeg command
        # This replaces the original audio stream with the provided audio file
        cmd = f"ffmpeg -i {video_file} -i {audio_file} -map 0:v -map 1:a -c:v copy -shortest {output_file}"
        
        try:
            await self.command_executor.execute(cmd)
            logger.info(f"Successfully merged audio and video to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error merging audio and video: {e}")
            # If the merge fails, return the original video file
            return video_file
