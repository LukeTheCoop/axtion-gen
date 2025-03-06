"""
Video Concatenator

This module provides functionality for concatenating multiple videos into a single video.
"""

import os
import tempfile
import logging
import shutil
import uuid
from typing import List
from datetime import datetime

from app.core.ffmpeg.interfaces import VideoConcatenator, FFmpegCommandExecutor

logger = logging.getLogger(__name__)

class AsyncVideoConcatenator(VideoConcatenator):
    """
    Asynchronous implementation of VideoConcatenator.
    Concatenates multiple videos into a single video using FFmpeg.
    """
    
    def __init__(self, command_executor: FFmpegCommandExecutor):
        """
        Initialize the concatenator.
        
        Args:
            command_executor: Command executor for running FFmpeg
        """
        self.command_executor = command_executor
    
    async def process(self, video_files: List[str], output_file: str, project_id: str = None) -> str:
        """
        Concatenate multiple videos.
        
        Args:
            video_files: List of video files to concatenate
            output_file: Path to save the concatenated video
            project_id: Optional project ID for organizing output
            
        Returns:
            str: Path to the concatenated video
        """
        if not video_files:
            logger.warning("No videos to concatenate")
            return None
        
        # Determine final output path with project_id
        if project_id:
            output_dir = f"./data/media/output/{project_id}"
            # Clear existing output directory
            if os.path.exists(output_dir):
                logger.info(f"Clearing output directory: {output_dir}")
                shutil.rmtree(output_dir)
            
            # Create fresh output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate unique ID for the final video
            unique_id = str(uuid.uuid4())[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"final_{timestamp}_{unique_id}.mp4"
            
            final_output_path = os.path.join(output_dir, filename)
        else:
            # If no project_id is provided, use the original output_file path
            final_output_path = output_file
            # Ensure output directory exists
            os.makedirs(os.path.dirname(final_output_path), exist_ok=True)
        
        logger.info(f"Will save final concatenated video to: {final_output_path}")
        
        if len(video_files) == 1:
            logger.info("Only one video provided, copying instead of concatenating")
            cmd = f"ffmpeg -i {video_files[0]} -c copy -y {final_output_path}"
            await self.command_executor.execute(cmd)
            logger.info(f"Successfully copied video to {final_output_path}")
            return final_output_path
        
        logger.info(f"Concatenating {len(video_files)} videos into {final_output_path}")
        
        # Create a temporary directory for normalized videos
        temp_dir = tempfile.mkdtemp()
        normalized_videos = []
        
        try:
            # First pass: normalize all videos to consistent parameters
            for i, video_file in enumerate(video_files):
                # Get video info to check frame rate
                video_info = await self.command_executor.get_video_info(video_file)
                
                # Create normalized output path
                normalized_path = os.path.join(temp_dir, f"normalized_{i}.mp4")
                normalized_videos.append(normalized_path)
                
                # Normalize video with explicit parameters for consistency
                norm_cmd = (
                    f"ffmpeg -i {video_file} -c:v libx264 -preset fast -crf 22 "
                    f"-r 30 -g 30 -keyint_min 30 -sc_threshold 0 "  # Force consistent frame rate and keyframes
                    f"-vsync cfr "  # Constant frame rate
                    f"-async 1 "    # Audio sync
                    f"-c:a aac -b:a 192k -ar 48000 "  # Consistent audio
                    f"-pix_fmt yuv420p "  # Standard pixel format
                    f"-y {normalized_path}"
                )
                
                logger.info(f"Normalizing video {i+1}/{len(video_files)}: {video_file}")
                await self.command_executor.execute(norm_cmd)
            
            # Create a new temporary file with normalized videos
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for norm_video in normalized_videos:
                    # Convert to absolute path and escape single quotes
                    abs_path = os.path.abspath(norm_video)
                    escaped_path = abs_path.replace("'", "\\'")
                    f.write(f"file '{escaped_path}'\n")
                concat_list_path = f.name
            
            # Second pass: concatenate the normalized videos
            cmd = (
                f"ffmpeg -f concat -safe 0 -i {concat_list_path} "
                f"-c:v libx264 -preset medium -crf 22 "
                f"-r 30 -g 30 -keyint_min 30 "  # Consistent frame rate and keyframes
                f"-vsync cfr "  # Constant frame rate output
                f"-c:a aac -b:a 192k -ar 48000 "  # Consistent audio
                f"-movflags +faststart "  # Optimize for streaming
                f"-y {final_output_path}"
            )
            
            await self.command_executor.execute(cmd)
            logger.info(f"Successfully concatenated {len(video_files)} videos to {final_output_path}")
            return final_output_path
        except Exception as e:
            logger.error(f"Error concatenating videos: {e}")
            return None
        finally:
            # Clean up the temporary file and directory
            try:
                os.unlink(concat_list_path)
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary files: {e}") 