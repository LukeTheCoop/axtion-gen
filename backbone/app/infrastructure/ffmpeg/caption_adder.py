"""
Caption Adder

This module provides functionality for adding captions to videos.
"""

from app.core.ffmpeg.interfaces import CaptionAdder, FFmpegCommandExecutor
from app.infrastructure.ffmpeg.ffmpeg_utils import check_ffmpeg

class AsyncCaptionAdder(CaptionAdder):
    """
    Asynchronous implementation of CaptionAdder.
    Adds captions to videos using FFmpeg.
    """
    
    def __init__(self, command_executor: FFmpegCommandExecutor):
        """
        Initialize the caption adder with a command executor.
        
        Args:
            command_executor (FFmpegCommandExecutor): Command executor for running FFmpeg
        """
        self.command_executor = command_executor
    
    async def process(self, video_path: str, caption_text: str, output_path: str, 
                     font_size: int = 24, position: str = "bottom") -> str:
        """
        Add a caption to a video file asynchronously.
        
        Args:
            video_path (str): Path to the input video file
            caption_text (str): Text to display as caption
            output_path (str): Path where the output video will be saved
            font_size (int, optional): Size of the font. Defaults to 24
            position (str, optional): Position of the caption. Defaults to "bottom"
            
        Returns:
            str: Path to the output video file
        """
        check_ffmpeg()
        
        # Define position coordinates based on the position parameter
        position_dict = {
            "bottom": "x=(w-text_w)/2:y=h-th-50",
            "top": "x=(w-text_w)/2:y=50",
            "center": "x=(w-text_w)/2:y=(h-text_h)/2",
            "middle": "x=(w-text_w)/2:y=(h-text_h)/2"
        }
        
        pos = position_dict.get(position.lower(), position_dict["bottom"])
        
        # Escape single quotes in the caption text
        safe_caption = caption_text.replace("'", "'\\''")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"drawtext=text='{safe_caption}':fontsize={font_size}:{pos}:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5",
            "-c:a", "copy",  # Copy audio without re-encoding
            "-y",            # Overwrite output if it exists
            output_path
        ]
        
        await self.command_executor.execute_command(
            cmd, f"Adding caption to {video_path}"
        )
        return output_path 