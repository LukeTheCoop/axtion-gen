"""
FFmpeg Type Definitions

This module defines types used by the FFmpeg infrastructure.
"""

from enum import Enum, auto
from typing import TypedDict, List, Dict, Any, Optional

class VideoFormat(Enum):
    """Video format enumeration."""
    MP4 = "mp4"
    MOV = "mov"
    AVI = "avi"
    MKV = "mkv"
    WEBM = "webm"

class AudioFormat(Enum):
    """Audio format enumeration."""
    MP3 = "mp3"
    WAV = "wav"
    AAC = "aac"
    OGG = "ogg"
    FLAC = "flac"

class Position(Enum):
    """Caption position enumeration."""
    TOP = "top"
    BOTTOM = "bottom"
    MIDDLE = "middle"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"

class VideoMetadata(TypedDict, total=False):
    """Video metadata type."""
    duration: float
    width: int
    height: int
    fps: float
    codec: str
    bitrate: int
    audio_codec: Optional[str]
    has_audio: bool

class ProcessingOptions(TypedDict, total=False):
    """Options for video processing."""
    font_size: int
    position: str
    resolution: str
    quality: str
    output_format: str
    concatenate: bool
    output_path: str

class VideoProcessingData(TypedDict):
    """Data for processing a video."""
    line: str
    source_video: str
    options: Optional[ProcessingOptions]

class AudioMetadata(TypedDict):
    """Audio metadata type"""
    duration: float
    format: str
    codec: str
    bitrate: Optional[int]
    sample_rate: Optional[int]

class VideoProcessingOptions(TypedDict, total=False):
    """Options for video processing"""
    font_size: int
    position: Position
    quality: str
    overwrite: bool
    codec: str
    max_concurrent_processes: int

class CaptionStyle(TypedDict, total=False):
    """Caption styling options"""
    font_size: int
    font_color: str
    box: bool
    box_color: str
    box_opacity: float
    position: Position

class VideoData(TypedDict):
    """Video data for processing"""
    source_video: str
    clip: str
    line: str
    start_time: Optional[float]
    end_time: Optional[float]
    options: Optional[VideoProcessingOptions]

# Type aliases for common usage
CommandList = List[str]
VideoPathList = List[str]
VideoDict = Dict[str, VideoData] 