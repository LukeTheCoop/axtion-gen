"""
FFmpeg Core Package

This package provides the core interfaces and types for the FFmpeg processing system.
"""

from app.core.ffmpeg.interfaces import (
    FFmpegCommandExecutor,
    VideoMetadataService,
    VideoOperation,
    AudioVideoMerger,
    CaptionAdder,
    SplitCaptionAdder,
    VideoConcatenator,
    VideoProcessingPipeline,
    YouTubeAudioMerger
)

from app.core.ffmpeg.types import (
    VideoFormat,
    AudioFormat,
    Position,
    VideoMetadata,
    ProcessingOptions,
    VideoProcessingData
)

__all__ = [
    # Interfaces
    'FFmpegCommandExecutor',
    'VideoMetadataService',
    'VideoOperation',
    'AudioVideoMerger',
    'CaptionAdder',
    'SplitCaptionAdder',
    'VideoConcatenator',
    'VideoProcessingPipeline',
    'YouTubeAudioMerger',
    
    # Types
    'VideoFormat',
    'AudioFormat',
    'Position',
    'VideoMetadata',
    'ProcessingOptions',
    'VideoProcessingData'
] 