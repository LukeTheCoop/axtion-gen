"""
Split Caption Adder

This module provides functionality for adding split captions to videos.
"""

import os
import shlex
import textwrap
import logging
from typing import List, Optional

from app.core.ffmpeg.interfaces import SplitCaptionAdder, FFmpegCommandExecutor

logger = logging.getLogger(__name__)

class AsyncSplitCaptionAdder(SplitCaptionAdder):
    """
    Asynchronous implementation of SplitCaptionAdder.
    Adds captions to videos using FFmpeg, splitting long captions into multiple lines.
    """
    
    def __init__(self, command_executor: FFmpegCommandExecutor):
        """
        Initialize the caption adder.
        
        Args:
            command_executor: Command executor for running FFmpeg
        """
        self.command_executor = command_executor
        self.default_font = "Arial"
        self.default_color = "white"
        self.default_bg_color = "black@0.5"  # Semi-transparent black background
    
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
            output_file: Path to the captioned video
            position: Position of the caption (top, bottom)
            font_size: Font size for the caption
            max_chars_per_line: Maximum characters per line
            
        Returns:
            str: Path to the captioned video
        """
        # Safety check - ensure filenames don't match caption words
        # This prevents issues where a caption word is being used as a filename
        if captions and output_file:
            first_caption_word = captions.split()[0] if captions.split() else ""
            if output_file == first_caption_word:
                # If output_file is the same as the first word in the caption, add a prefix
                output_file = f"captioned_{output_file}"
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Adding split captions to {input_file}")
        
        # Ensure output file has a valid extension - more robust handling
        base, ext = os.path.splitext(output_file)
        if not ext:
            output_file = f"{base}.mp4"
            
        # If output_file has no directory, use a default
        if not os.path.dirname(output_file):
            output_file = os.path.join("./output", output_file)
            
        try:
            # Get video duration
            video_info = await self.command_executor.get_video_info(input_file)
            duration = float(video_info['format']['duration'])
            
            # Determine number of segments based on caption length
            words = captions.split()
            total_chars = len(captions)
            
            # Determine optimal number of segments based on caption length
            if total_chars <= 30:
                num_segments = 1  # Very short captions don't need splitting
            elif total_chars <= 50:
                num_segments = 2  # Short captions split in half
            else:
                num_segments = 3  # Most captions will now be split into thirds
                
            logger.info(f"Splitting caption into {num_segments} segments (length: {total_chars} chars)")
            
            # Determine position coordinates based on the position parameter
            position_dict = {
                "bottom": "x=(w-text_w)/2:y=h-th-50",
                "top": "x=(w-text_w)/2:y=50",
                "center": "x=(w-text_w)/2:y=(h-text_h)/2",
                "middle": "x=(w-text_w)/2:y=(h-text_h)/2"
            }
            pos = position_dict.get(position.lower(), position_dict["bottom"])
            
            # For a single segment, just use regular caption
            if num_segments == 1:
                # Just wrap the text for better display on mobile
                wrapped_text = self._wrap_text(captions, max_chars_per_line)
                # Escape special characters
                safe_text = wrapped_text.replace("'", "'\\\''")
                
                filter_text = (
                    f"drawtext=text='{safe_text}':fontsize={font_size}:{pos}:"
                    f"fontcolor={self.default_color}:box=1:boxcolor={self.default_bg_color}:boxborderw=5"
                )
            else:
                # Split caption into multiple segments, exactly like in the example
                segment_size = len(words) // num_segments
                segments = []
                
                for i in range(num_segments):
                    start_idx = i * segment_size
                    end_idx = (i + 1) * segment_size if i < num_segments - 1 else len(words)
                    segment_text = " ".join(words[start_idx:end_idx])
                    
                    # Wrap the text segment for better display
                    wrapped_text = self._wrap_text(segment_text, max_chars_per_line)
                    segments.append(wrapped_text)
                
                # Calculate time for each segment
                segment_duration = duration / num_segments
                
                # Now create multiple drawtext filters with timing constraints
                filter_parts = []
                
                for i, segment in enumerate(segments):
                    # Calculate start and end times for this segment
                    start_time = i * segment_duration
                    end_time = (i + 1) * segment_duration
                    
                    # Escape special characters (same as in example)
                    safe_text = segment.replace("'", "'\\\''")
                    
                    # Create filter with enable constraint for specific time period
                    filter_part = (
                        f"drawtext=text='{safe_text}':fontsize={font_size}:{pos}:"
                        f"fontcolor={self.default_color}:box=1:boxcolor={self.default_bg_color}:boxborderw=5:"
                        f"enable='between(t,{start_time},{end_time})'"
                    )
                    filter_parts.append(filter_part)
                
                # Join all filter parts with commas - this is the key to displaying them sequentially
                filter_text = ", ".join(filter_parts)
            
            # Create the FFmpeg command using the filter
            cmd_parts = [
                "ffmpeg",
                "-i", input_file,
                "-vf", filter_text,
                "-c:a", "copy",  # Copy audio without re-encoding
                "-y",            # Overwrite output if it exists
                output_file
            ]
            
            # Convert command parts to a string
            cmd = " ".join([shlex.quote(str(part)) for part in cmd_parts])
            
            # Execute the command
            await self.command_executor.execute(cmd)
            logger.info(f"Successfully added {num_segments} split captions to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error adding split captions: {e}")
            # If adding captions fails, return the original file
            return input_file
    
    def _wrap_text(self, text: str, max_chars: int) -> str:
        """
        Wrap text to a maximum number of characters per line.
        
        Args:
            text: The text to wrap
            max_chars: Maximum characters per line
            
        Returns:
            str: The wrapped text
        """
        lines = []
        for paragraph in text.splitlines():
            if not paragraph:
                lines.append("")
            else:
                wrapped = textwrap.fill(paragraph, width=max_chars)
                lines.extend(wrapped.splitlines())
        
        return '\\n'.join(lines)
