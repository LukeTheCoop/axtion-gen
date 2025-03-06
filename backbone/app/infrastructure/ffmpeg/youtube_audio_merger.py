"""
YouTube Audio Merger

This module provides functionality for downloading audio from YouTube and merging it with videos.
"""

import os
import subprocess
import tempfile
import logging
from typing import Optional

from app.core.ffmpeg.interfaces import YouTubeAudioMerger, FFmpegCommandExecutor

logger = logging.getLogger(__name__)

class AsyncYouTubeAudioMerger(YouTubeAudioMerger):
    """
    Asynchronous implementation of YouTubeAudioMerger.
    Downloads audio from YouTube and merges it with videos using FFmpeg.
    """
    
    def __init__(self, command_executor: FFmpegCommandExecutor):
        """
        Initialize the merger.
        
        Args:
            command_executor: Command executor for running FFmpeg commands
        """
        self.command_executor = command_executor
    
    async def _download_youtube_audio(self, youtube_url: str, output_path: str) -> str:
        """
        Download audio from a YouTube video as mp3.
        
        Args:
            youtube_url: YouTube URL to download audio from
            output_path: Path to save the downloaded audio
            
        Returns:
            str: Path to the downloaded mp3
        """
        cmd = [
            'yt-dlp',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '0',  # 0 is best quality
            '-o', output_path,
            youtube_url
        ]
        
        logger.info(f"Starting YouTube audio download from {youtube_url}")
        logger.info(f"Using yt-dlp with audio format: mp3, quality: 0 (best)")
        
        # Execute the command through our executor (supports both async and sync)
        cmd_str = ' '.join(cmd)
        try:
            await self.command_executor.execute(cmd_str)
            final_path = f"{output_path}.mp3"
            logger.info(f"YouTube audio download complete: {final_path}")
            # yt-dlp adds extension automatically, so we need to add it back
            return final_path
        except Exception as e:
            logger.error(f"YouTube audio download failed: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
    
    async def _get_media_duration(self, file_path: str) -> float:
        """
        Get the duration of a media file using ffprobe.
        
        Args:
            file_path: Path to the media file
            
        Returns:
            float: Duration in seconds
        """
        logger.debug(f"Getting duration for media file: {file_path}")
        
        try:
            # Create a temporary directory for the script
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create a temporary file for the output
                duration_output = os.path.join(temp_dir, "duration.txt")
                
                # Create a script file for the ffprobe command
                script_file = os.path.join(temp_dir, "ffprobe_duration.sh")
                with open(script_file, 'w') as f:
                    f.write("#!/bin/bash\n")
                    f.write(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}" > "{duration_output}"\n')
                
                # Make the script executable
                os.chmod(script_file, 0o755)
                
                # Execute the script
                await self.command_executor.execute(script_file)
                
                # Read the duration from the output file
                with open(duration_output, 'r') as f:
                    duration_str = f.read().strip()
                    duration = float(duration_str) if duration_str else 0.0
            
            logger.debug(f"Media duration: {duration:.2f} seconds for {file_path}")
            return duration
        except Exception as e:
            logger.error(f"Failed to get media duration for {file_path}: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return 0.0
    
    async def _trim_audio(self, input_audio: str, trim_start: float, output_audio: str) -> str:
        """
        Trim the beginning of an audio file.
        
        Args:
            input_audio: Path to the input audio file
            trim_start: Start time to trim from in seconds
            output_audio: Path to save the trimmed audio
            
        Returns:
            str: Path to the trimmed audio
        """
        logger.info(f"Trimming audio file {input_audio}")
        logger.info(f"  - Removing first {trim_start:.2f} seconds")
        logger.info(f"  - Output will be saved to {output_audio}")
        
        try:
            # Create a temporary directory for the script
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create a script file for the FFmpeg command
                script_file = os.path.join(temp_dir, "ffmpeg_trim.sh")
                with open(script_file, 'w') as f:
                    f.write("#!/bin/bash\n")
                    f.write(f'ffmpeg -i "{input_audio}" -ss {trim_start} -c:a copy "{output_audio}"\n')
                
                # Make the script executable
                os.chmod(script_file, 0o755)
                
                # Execute the script
                await self.command_executor.execute(script_file)
                
            logger.info(f"Audio trimming complete: {output_audio}")
            return output_audio
        except Exception as e:
            logger.error(f"Audio trimming failed: {e}")
            logger.warning(f"Using original untrimmed audio: {input_audio}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return input_audio  # Return original if trim fails
    
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
            str: Path to the merged file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        logger.info(f"========== YOUTUBE AUDIO MERGER PROCESS ==========")
        logger.info(f"Input video: {video_file}")
        logger.info(f"YouTube URL: {youtube_url}")
        logger.info(f"Output file: {output_file}")
        logger.info(f"Parameters: start_time={start_time}s, trim_audio={trim_audio}s, volume={volume}")
        
        # Create temporary directory for the audio download and processing
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Validate volume
                if volume < 0 or volume > 1.0:
                    logger.warning(f"Invalid volume value {volume}, using 1.0")
                    volume = 1.0
                
                # STEP 1: Download the YouTube audio
                logger.info(f"STEP 1: DOWNLOADING YOUTUBE AUDIO from {youtube_url}")
                temp_audio_path = os.path.join(temp_dir, "audio")
                audio_path = await self._download_youtube_audio(youtube_url, temp_audio_path)
                
                # STEP 2: Trim the audio if needed
                if trim_audio > 0:
                    logger.info(f"STEP 2: TRIMMING AUDIO by {trim_audio} seconds")
                    trimmed_audio_path = os.path.join(temp_dir, "trimmed_audio.mp3")
                    audio_path = await self._trim_audio(audio_path, trim_audio, trimmed_audio_path)
                else:
                    logger.info(f"STEP 2: NO TRIMMING NEEDED (trim_audio={trim_audio})")
                
                # STEP 3: Get durations and prepare for merging
                logger.info(f"STEP 3: ANALYZING MEDIA DURATIONS")
                video_duration = await self._get_media_duration(video_file)
                audio_duration = await self._get_media_duration(audio_path)
                
                # Validate start time
                if start_time >= video_duration:
                    logger.warning(f"Start time ({start_time}s) is greater than video duration ({video_duration}s). Setting to 0.")
                    start_time = 0
                
                # Calculate how many times to loop the audio to cover the video
                remaining_video_duration = video_duration - float(start_time)
                loop_count = max(1, int(remaining_video_duration / audio_duration) + 1)
                
                logger.info(f"  - Video duration: {video_duration:.2f} seconds")
                logger.info(f"  - Audio duration: {audio_duration:.2f} seconds")
                logger.info(f"  - Starting audio at: {start_time:.2f} seconds into the video")
                logger.info(f"  - YouTube audio volume: {volume}")
                logger.info(f"  - Looping audio {loop_count} times to cover the video")
                
                # STEP 4: Prepare concatenated audio
                logger.info(f"STEP 4: PREPARING CONCATENATED AUDIO")
                # Create a file with the concatenation instructions
                concat_file = os.path.join(temp_dir, "concat.txt")
                with open(concat_file, 'w') as f:
                    for i in range(loop_count):
                        f.write(f"file '{audio_path}'\n")
                
                # Path to the temporary concatenated audio
                concat_audio = os.path.join(temp_dir, "concat_audio.mp3")
                
                # Concatenate the audio files using a script approach
                try:
                    # First attempt: Try the script method
                    try:
                        # Create a temporary script for the concatenation
                        concat_script = os.path.join(temp_dir, "ffmpeg_concat.sh")
                        with open(concat_script, 'w') as f:
                            f.write("#!/bin/bash\n")
                            f.write(f'ffmpeg -f concat -safe 0 -i "{concat_file}" -c copy "{concat_audio}"\n')
                        
                        # Make the script executable
                        os.chmod(concat_script, 0o755)
                        
                        logger.info(f"  - Created FFmpeg concat script: {concat_script}")
                        logger.info(f"  - Concatenating audio {loop_count} times")
                        
                        # Execute the script
                        await self.command_executor.execute(concat_script)
                    
                    except Exception as script_error:
                        # Second attempt: Fallback to direct subprocess method like in the example code
                        logger.warning(f"Concat script method failed with error: {script_error}. Trying direct subprocess method...")
                        
                        # Build the command as a list like in the example code
                        cmd = [
                            'ffmpeg',
                            '-f', 'concat',
                            '-safe', '0',
                            '-i', concat_file,
                            '-c', 'copy',
                            concat_audio
                        ]
                        
                        logger.info(f"  - Using direct subprocess with command: {cmd}")
                        
                        # Execute using direct subprocess
                        import subprocess
                        subprocess.run(cmd, check=True)
                        logger.info(f"  - Direct subprocess method successful for concatenation")
                
                except Exception as e:
                    logger.error(f"Both script and direct subprocess methods failed for concatenation: {e}")
                    raise
                
                # STEP 5: Merge the video with the concatenated audio
                logger.info(f"STEP 5: MERGING VIDEO WITH YOUTUBE AUDIO")
                
                try:
                    # First attempt: Try the script method
                    try:
                        # Create a temporary script file with the FFmpeg command
                        script_file = os.path.join(temp_dir, "ffmpeg_merge.sh")
                        with open(script_file, 'w') as f:
                            f.write("#!/bin/bash\n")
                            f.write(f'ffmpeg -i "{video_file}" -i "{concat_audio}" \\\n')
                            # The key fix here is using proper escaping for the between function
                            f.write(f'  -filter_complex "[1:a]volume=0:enable=\'between(t,0,{start_time})\',volume={volume}[youtube_audio]; [0:a][youtube_audio]amix=inputs=2:duration=first[a]" \\\n')
                            f.write(f'  -map 0:v -map "[a]" -c:v copy "{output_file}"\n')
                        
                        # Make the script executable
                        os.chmod(script_file, 0o755)
                        
                        logger.info(f"  - Created FFmpeg merge script: {script_file}")
                        
                        # For debugging, dump the script content to logs
                        with open(script_file, 'r') as f:
                            script_content = f.read()
                            logger.info(f"  - Script content:\n{script_content}")
                        
                        # Execute the script directly
                        merge_cmd = script_file
                        await self.command_executor.execute(merge_cmd)
                    
                    except Exception as script_error:
                        # Second attempt: Fallback to direct subprocess method like in the example code
                        logger.warning(f"Script method failed with error: {script_error}. Trying direct subprocess method...")
                        
                        # Create the filter complex string with proper escaping
                        filter_complex = f"[1:a]volume=0:enable='between(t,0,{start_time})',volume={volume}[youtube_audio]; [0:a][youtube_audio]amix=inputs=2:duration=first[a]"
                        
                        # Build the command as a list like in the example code
                        cmd = [
                            'ffmpeg',
                            '-i', video_file,
                            '-i', concat_audio,
                            '-filter_complex', filter_complex,
                            '-map', '0:v',
                            '-map', '[a]',
                            '-c:v', 'copy',
                            output_file
                        ]
                        
                        logger.info(f"  - Using direct subprocess with command: {cmd}")
                        
                        # Execute using direct subprocess
                        import subprocess
                        subprocess.run(cmd, check=True)
                        logger.info(f"  - Direct subprocess method successful")
                
                except Exception as e:
                    logger.error(f"Both script and direct subprocess methods failed: {e}")
                    raise
                
                logger.info(f"STEP 6: SUCCESSFULLY COMPLETED YOUTUBE AUDIO MERGING")
                logger.info(f"  - Final output: {output_file}")
                logger.info(f"========== YOUTUBE AUDIO MERGER COMPLETE ==========")
                return output_file
                
            except Exception as e:
                logger.error(f"ERROR IN YOUTUBE AUDIO MERGING: {e}")
                logger.error(f"Falling back to original video: {video_file}")
                import traceback
                logger.debug(f"Traceback: {traceback.format_exc()}")
                return video_file 