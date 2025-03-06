"""
FFmpeg Core Interfaces

This module defines the interfaces for FFmpeg processing operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class FFmpegCommandExecutor(ABC):
    """Interface for executing FFmpeg commands."""
    
    @abstractmethod
    async def execute(self, command: str) -> str:
        """
        Execute an FFmpeg command.
        
        Args:
            command: The FFmpeg command to execute
            
        Returns:
            The command output
        """
        pass

class VideoMetadataService(ABC):
    """Interface for retrieving video metadata."""
    
    @abstractmethod
    async def get_duration(self, video_file: str) -> float:
        """
        Get the duration of a video in seconds.
        
        Args:
            video_file: Path to the video file
            
        Returns:
            The duration in seconds
        """
        pass
    
    @abstractmethod
    async def get_resolution(self, video_file: str) -> tuple:
        """
        Get the resolution of a video.
        
        Args:
            video_file: Path to the video file
            
        Returns:
            Tuple of (width, height)
        """
        pass
    
    @abstractmethod
    async def get_codec(self, video_file: str) -> str:
        """
        Get the codec of a video.
        
        Args:
            video_file: Path to the video file
            
        Returns:
            The codec name
        """
        pass

class VideoOperation(ABC):
    """Base interface for video operations."""
    
    @abstractmethod
    async def process(self, *args, **kwargs) -> str:
        """
        Process a video operation.
        
        Returns:
            Path to the output file
        """
        pass

class AudioVideoMerger(VideoOperation):
    """Interface for merging audio and video files."""
    
    @abstractmethod
    async def process(self, audio_file: str, video_file: str, output_file: str) -> str:
        """
        Merge audio and video files.
        
        Args:
            audio_file: Path to the audio file
            video_file: Path to the video file
            output_file: Path to save the merged file
            
        Returns:
            Path to the merged file
        """
        pass

class CaptionAdder(VideoOperation):
    """Interface for adding captions to videos."""
    
    @abstractmethod
    async def process(
        self, 
        input_file: str, 
        captions: str, 
        output_file: str, 
        position: str = "bottom",
        font_size: int = 24
    ) -> str:
        """
        Add captions to a video.
        
        Args:
            input_file: Path to the input video
            captions: Caption text
            output_file: Path to save the captioned video
            position: Position of the caption (top, bottom)
            font_size: Font size for the caption
            
        Returns:
            Path to the captioned video
        """
        pass

class SplitCaptionAdder(VideoOperation):
    """Interface for adding split captions to videos."""
    
    @abstractmethod
    async def process(
        self, 
        input_file: str, 
        captions: str, 
        output_file: str, 
        position: str = "bottom",
        font_size: int = 24,
        max_chars_per_line: int = 40
    ) -> str:
        """
        Add split captions to a video.
        
        Args:
            input_file: Path to the input video
            captions: Caption text
            output_file: Path to save the captioned video
            position: Position of the caption (top, bottom)
            font_size: Font size for the caption
            max_chars_per_line: Maximum characters per line
            
        Returns:
            Path to the captioned video
        """
        pass

class VideoConcatenator(VideoOperation):
    """Interface for concatenating videos."""
    
    @abstractmethod
    async def process(self, video_files: List[str], output_file: str, project_id: str = None) -> str:
        """
        Concatenate multiple videos.
        
        Args:
            video_files: List of video files to concatenate
            output_file: Path to save the concatenated video
            project_id: Optional project ID for organizing output
            
        Returns:
            Path to the concatenated video
        """
        pass

class VideoProcessingPipeline(ABC):
    """Interface for a video processing pipeline."""
    
    @abstractmethod
    async def process_videos(self, video_data: Dict[str, Dict[str, Any]], input_video: str = None) -> List[str]:
        """
        Process multiple videos in parallel.
        
        Args:
            video_data: Dictionary mapping audio files to their processing data
                        {audio_file: {"line": caption_text, "source_video": video_path}}
            input_video: Optional reference video for formatting
            
        Returns:
            List of processed video file paths
        """
        pass
    
    @abstractmethod
    async def concatenate_videos(self, video_files: List[str], output_file: str) -> str:
        """
        Concatenate multiple videos into a single video.
        
        Args:
            video_files: List of video files to concatenate
            output_file: Path where the concatenated video will be saved
            
        Returns:
            Path to the concatenated video
        """
        pass

class YouTubeAudioMerger(VideoOperation):
    """Interface for downloading and merging YouTube audio with videos."""
    
    @abstractmethod
    async def process(self, 
                     video_file: str, 
                     youtube_url: str, 
                     output_file: str, 
                     start_time: float = 0.0, 
                     trim_audio: float = 0.0, 
                     volume: float = 1.0) -> str:
        """
        Download audio from YouTube and merge it with a video.
        
        Args:
            video_file: Path to the input video
            youtube_url: YouTube URL to download audio from
            output_file: Path to save the merged file
            start_time: Start time in seconds to begin the audio in the video
            trim_audio: Trim the beginning of the YouTube audio by this many seconds
            volume: Volume of the YouTube audio (0.0-1.0)
            
        Returns:
            Path to the merged file
        """
        pass 