#!/usr/bin/env python3
"""
FFmpeg Async Usage Example

This example demonstrates how to use the asynchronous FFmpeg processing system.
"""

import asyncio
import logging
from typing import Dict, List

# Import from our modular FFmpeg infrastructure
from app.infrastructure.ffmpeg import create_pipeline, configure_ffmpeg

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """
    Main function demonstrating asynchronous video processing.
    """
    # Sample video data - in a real application, this might come from a database or API
    video_data = {
        "audio_1.mp3": {
            "line": "This is the first part. This is the second part.",
            "source_video": "source_1.mp4"
        },
        "audio_2.mp3": {
            "line": "Another first part. Another second part.",
            "source_video": "source_2.mp4"
        },
        "audio_3.mp3": {
            "line": "Third video first part. Third video second part.",
            "source_video": "source_3.mp4"
        }
    }
    
    # Configure the FFmpeg system
    config = {
        "max_concurrent_processes": 4,  # Process up to 4 videos simultaneously
        "output_directory": "./output",
        "font_size": 28,
        "position": "bottom"
    }
    
    # Create the video processing pipeline
    pipeline = create_pipeline(config)
    
    logger.info("Starting asynchronous video processing")
    
    # Process all videos in parallel
    try:
        # The input_video is the template video that will be combined with audio
        processed_videos = await pipeline.process_videos(video_data, "input_video.mp4")
        
        logger.info(f"Successfully processed {len(processed_videos)} videos")
        logger.info(f"Processed videos: {processed_videos}")
        
        # Optional: Concatenate all videos into one final video
        # from app.infrastructure.ffmpeg import create_ffmpeg_factory
        # factory = create_ffmpeg_factory(config)
        # concatenator = factory.create_video_concatenator()
        # final_video = await concatenator.process(processed_videos, "final_output.mp4")
        # logger.info(f"Created final concatenated video: {final_video}")
        
    except Exception as e:
        logger.error(f"Error processing videos: {e}")
        raise

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 