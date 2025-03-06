"""
FFmpeg Factory Module

This module provides factory classes for creating FFmpeg components.
"""

import logging
from typing import Dict, Any

from app.infrastructure.ffmpeg.ffmpeg_utils import AsyncFFmpegCommandExecutor
from app.infrastructure.ffmpeg.video_metadata import AsyncVideoMetadataService
from app.infrastructure.ffmpeg.merge_audio_video import AsyncAudioVideoMerger
from app.infrastructure.ffmpeg.add_split_caption import AsyncSplitCaptionAdder
from app.infrastructure.ffmpeg.video_concatenator import AsyncVideoConcatenator

logger = logging.getLogger(__name__)

class FFmpegFactory:
    """
    Factory for creating FFmpeg components.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the factory with configuration.
        
        Args:
            config: Configuration for the factory
        """
        self.config = config or {}
        self.max_concurrent_processes = self.config.get("max_concurrent_processes", 4)
    
    def create_command_executor(self):
        """
        Create a command executor.
        
        Returns:
            AsyncFFmpegCommandExecutor: A command executor
        """
        return AsyncFFmpegCommandExecutor(max_processes=self.max_concurrent_processes)
    
    def create_metadata_service(self):
        """
        Create a video metadata service.
        
        Returns:
            AsyncVideoMetadataService: A video metadata service
        """
        return AsyncVideoMetadataService(
            command_executor=self.create_command_executor()
        )
    
    def create_audio_video_merger(self):
        """
        Create an audio video merger.
        
        Returns:
            AsyncAudioVideoMerger: An audio video merger
        """
        return AsyncAudioVideoMerger(
            command_executor=self.create_command_executor()
        )
    
    def create_split_caption_adder(self):
        """
        Create a split caption adder.
        
        Returns:
            AsyncSplitCaptionAdder: A split caption adder
        """
        return AsyncSplitCaptionAdder(
            command_executor=self.create_command_executor()
        )
    
    def create_video_concatenator(self):
        """
        Create a video concatenator.
        
        Returns:
            AsyncVideoConcatenator: A video concatenator
        """
        return AsyncVideoConcatenator(
            command_executor=self.create_command_executor()
        )

def create_ffmpeg_factory(config: Dict[str, Any] = None) -> FFmpegFactory:
    """
    Create an FFmpeg factory with the given configuration.
    
    Args:
        config: Configuration for the factory
        
    Returns:
        FFmpegFactory: A factory for creating FFmpeg components
    """
    return FFmpegFactory(config) 

def create_command_executor(config: Dict[str, Any] = None):
    """
    Create a command executor directly (utility function).
    
    Args:
        config: Configuration for the factory
        
    Returns:
        AsyncFFmpegCommandExecutor: A command executor
    """
    factory = create_ffmpeg_factory(config)
    return factory.create_command_executor()

def create_metadata_service(config: Dict[str, Any] = None):
    """
    Create a metadata service directly (utility function).
    
    Args:
        config: Configuration for the factory
        
    Returns:
        AsyncVideoMetadataService: A metadata service
    """
    factory = create_ffmpeg_factory(config)
    return factory.create_metadata_service()

def create_video_processing_pipeline(config: Dict[str, Any] = None):
    """
    Create a video processing pipeline directly (utility function).
    This is a convenience function that calls create_pipeline in __init__.py.
    
    Args:
        config: Configuration for the pipeline
        
    Returns:
        AsyncVideoProcessingPipeline: A video processing pipeline
    """
    from app.infrastructure.ffmpeg import create_pipeline
    return create_pipeline(config)

def create_youtube_audio_merger(command_executor=None):
    """
    Create a YouTube audio merger.
    
    Args:
        command_executor: Command executor for running FFmpeg (optional)
        
    Returns:
        AsyncYouTubeAudioMerger: A YouTube audio merger
    """
    from app.infrastructure.ffmpeg.youtube_audio_merger import AsyncYouTubeAudioMerger
    
    # Create command executor if not provided
    if command_executor is None:
        command_executor = create_command_executor()
        
    return AsyncYouTubeAudioMerger(command_executor) 