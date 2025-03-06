"""
FFmpeg Infrastructure Package

This package provides the implementations of the FFmpeg interfaces for video processing.
"""

from app.infrastructure.ffmpeg.factories import (
    create_ffmpeg_factory,
    create_command_executor,
    create_metadata_service,
    create_video_processing_pipeline,
    create_youtube_audio_merger
)

# For direct access to component implementations
from app.infrastructure.ffmpeg.ffmpeg_utils import (
    AsyncFFmpegCommandExecutor,
    configure_ffmpeg,
    check_ffmpeg
)
from app.infrastructure.ffmpeg.video_metadata import AsyncVideoMetadataService
from app.infrastructure.ffmpeg.merge_audio_video import AsyncAudioVideoMerger
from app.infrastructure.ffmpeg.caption_adder import AsyncCaptionAdder
from app.infrastructure.ffmpeg.add_split_caption import AsyncSplitCaptionAdder
from app.infrastructure.ffmpeg.video_concatenator import AsyncVideoConcatenator
from app.infrastructure.ffmpeg.youtube_audio_merger import AsyncYouTubeAudioMerger
from app.infrastructure.ffmpeg.pipeline import AsyncVideoProcessingPipeline

# Main function to create a configured pipeline
def create_pipeline(config=None):
    """
    Create and configure a video processing pipeline.
    
    Args:
        config (dict, optional): Configuration for the pipeline
        
    Returns:
        AsyncVideoProcessingPipeline: Configured pipeline instance
    """
    # Get a factory
    factory = create_ffmpeg_factory()
    
    # Create a pipeline
    pipeline = AsyncVideoProcessingPipeline(
        command_executor=factory.create_command_executor(),
        metadata_service=factory.create_metadata_service(),
        audio_video_merger=factory.create_audio_video_merger(),
        split_caption_adder=factory.create_split_caption_adder(),
        concatenator=factory.create_video_concatenator()
    )
    
    # Configure if needed
    if config:
        if "max_concurrent_processes" in config:
            configure_ffmpeg(max_concurrent_processes=config["max_concurrent_processes"])
        if "font_size" in config:
            pipeline.font_size = config["font_size"]
        if "position" in config:
            pipeline.caption_position = config["position"]
    
    return pipeline

__all__ = [
    # Factory functions
    'create_ffmpeg_factory',
    'create_command_executor',
    'create_metadata_service',
    'create_video_processing_pipeline',
    'create_pipeline',
    'create_youtube_audio_merger',
    
    # Component implementations
    'AsyncFFmpegCommandExecutor',
    'AsyncVideoMetadataService',
    'AsyncAudioVideoMerger',
    'AsyncCaptionAdder',
    'AsyncSplitCaptionAdder',
    'AsyncVideoConcatenator',
    'AsyncVideoProcessingPipeline',
    'AsyncYouTubeAudioMerger',
    
    # Utilities
    'configure_ffmpeg',
    'check_ffmpeg'
]
