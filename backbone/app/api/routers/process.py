"""
Process Router

This module provides API endpoints for processing video generation requests.
"""

import os
import shutil
import asyncio
import time
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Set

from app.common.config import ConfigService, get_config_service
from app.api.services.video_processor import VideoProcessorService
from app.api.services.audio_processor import AudioProcessorService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

class ProcessRequest(BaseModel):
    """Request model for video processing."""
    mothership: str
    prompt: str
    genre: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

class ProcessResponse(BaseModel):
    """Response model for video processing."""
    creative: str
    polish: str
    final_response: Optional[str] = None
    video_urls: Optional[List[str]] = None
    status: str = "success"
    message: Optional[str] = None

class UploadResponse(BaseModel):
    """Response model for file uploads."""
    status: str
    file_path: str
    prompt_id: str
    message: str

class AudioGenerationResponse(BaseModel):
    """Response model for audio generation."""
    status: str = "success"
    message: str
    audio_files: List[str] = []
    missing_files: List[str] = []

@router.post("/process", response_model=ProcessResponse)
async def process_request(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Process a video generation request, creating videos from the provided prompts.
    
    Args:
        request: The process request containing mothership, prompt, and genre
        background_tasks: FastAPI background tasks for async processing
        config_service: Configuration service
        
    Returns:
        ProcessResponse: Response with creative, polish, and final outputs
    """
    from app.main import start_video_pipeline
    
    try:
        # Get genre, defaulting to military if not provided
        requested_genre = request.genre or config_service.get("default_genre", "military")
        
        # Verify the genre exists in the configuration
        available_genres = config_service.get("video_list", {}).keys()
        print(f"PROCESS ROUTER - AVAILABLE GENRES: {list(available_genres)}")
        
        # If the requested genre doesn't exist in the config, fall back to the default
        if requested_genre not in available_genres:
            default_genre = config_service.get("default_genre", "military")
            print(f"PROCESS ROUTER - REQUESTED GENRE '{requested_genre}' NOT FOUND, USING DEFAULT: {default_genre}")
            genre = default_genre
        else:
            genre = requested_genre
        
        print(f"PROCESS ROUTER - CONFIG SERVICE TYPE: {type(config_service)}")
        print(f"PROCESS ROUTER - CONFIG SERVICE ID: {id(config_service)}")
        
        # Add default empty list when genre doesn't exist
        video_list = config_service.get("video_list", {}).get(genre, [])
        print(f"PROCESS ROUTER - VIDEO LIST TYPE: {type(video_list)}")
        print(f"PROCESS ROUTER - VIDEO LIST LENGTH: {len(video_list) if video_list else 0}")
        print(f'Look here, empty video list {video_list}')
        creative, polish, final_response = start_video_pipeline(
            mothership=request.mothership,
            user_prompt=request.prompt,
            config_service=config_service,
            genre=genre
        )
        
        # Initialize the response
        response = ProcessResponse(
            creative=creative,
            polish=polish,
            final_response=final_response,
            status="success",
            message="Video generation completed. Video processing started in background."
        )
        
        # Schedule video processing in the background
        background_tasks.add_task(
            process_videos_background,
            ProcessRequest(
                mothership=final_response,
                prompt=creative,
                genre=genre,
                options=request.options if hasattr(request, 'options') else None
            ),
            background_tasks,
            config_service
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@router.post("/upload/audio", response_model=UploadResponse)
async def upload_audio(
    file: UploadFile = File(...),
    prompt_id: str = Form(...),
    prompt_text: str = Form(...),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Upload an audio file to be processed.
    
    This endpoint would normally be part of the ElevenLabs integration,
    but is provided here for testing with pre-generated audio files.
    
    Args:
        file: The audio file to upload
        prompt_id: ID for the prompt
        prompt_text: Text of the prompt
        config_service: Configuration service
        
    Returns:
        UploadResponse: Response with status and file path
    """
    try:
        # Ensure the audio directory exists
        audio_dir = "data/current"
        os.makedirs(audio_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(audio_dir, f"{prompt_id}{os.path.splitext(file.filename)[1]}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return UploadResponse(
            status="success",
            file_path=file_path,
            prompt_id=prompt_id,
            message=f"File uploaded successfully to {file_path}"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.post("/process/videos", response_model=List[str])
async def process_videos_endpoint(
    prompts_data: Dict[str, str],
    genre: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    background_tasks: BackgroundTasks = None,
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Process videos directly using the provided prompts data.
    This endpoint allows bypassing the LLM generation step if you already have the text.
    
    Args:
        prompts_data: Dictionary mapping prompt IDs to prompt text
        genre: Genre for video selection, defaults to value in config
        options: Additional processing options
        background_tasks: FastAPI background tasks
        config_service: Configuration service
        
    Returns:
        List[str]: List of processed video paths (if not backgrounded)
    """
    try:
        # If background_tasks is provided, process in background
        if background_tasks:
            background_tasks.add_task(
                process_videos_background,
                ProcessRequest(
                    mothership=prompts_data.get("final", ""),
                    prompt=prompts_data.get("creative", ""),
                    genre=genre,
                    options=options
                ),
                background_tasks,
                config_service
            )
            return []
        
        # Otherwise process immediately (blocking)
        video_processor = VideoProcessorService(config_service)
        processed_videos = await video_processor.process_videos(prompts_data, genre)
        
        return processed_videos
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing videos: {str(e)}")

@router.post("/background", response_model=ProcessResponse)
async def process_videos_background(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Start video processing in the background.
    
    Args:
        request (ProcessRequest): The processing request
        background_tasks (BackgroundTasks): Background tasks handler
        config_service (ConfigService): Config service
        
    Request parameters:
        - prompts (Dict[str, str]): Dictionary mapping prompt IDs to captions
        - genre (str): Genre for selecting videos
        - options (Dict[str, Any]): Optional configuration:
            - project_id (str): Custom project ID
            - youtube_audio: YouTube audio configuration for final video:
                {
                    "url": "YouTube URL to download audio from",
                    "start_time": 0.0,  # Start time in seconds
                    "trim_audio": 0.0,  # Trim the beginning of the YouTube audio
                    "volume": 1.0       # Volume of the YouTube audio (0.0-1.0)
                }
                Note: This can also be configured in config.json under "youtube_audio"
    
    Returns:
        ProcessResponse: Processing response with job ID
    """
    try:
        # Get genre, defaulting to military if not provided
        requested_genre = request.genre or config_service.get("default_genre", "military")
        
        # Verify the genre exists in the configuration
        available_genres = config_service.get("video_list", {}).keys()
        print(f"PROCESS ROUTER - AVAILABLE GENRES: {list(available_genres)}")
        
        # If the requested genre doesn't exist in the config, fall back to the default
        if requested_genre not in available_genres:
            default_genre = config_service.get("default_genre", "military")
            print(f"PROCESS ROUTER - REQUESTED GENRE '{requested_genre}' NOT FOUND, USING DEFAULT: {default_genre}")
            genre = default_genre
        else:
            genre = requested_genre
        
        print(f"PROCESS ROUTER - CONFIG SERVICE TYPE: {type(config_service)}")
        print(f"PROCESS ROUTER - CONFIG SERVICE ID: {id(config_service)}")
        
        # Add default empty list when genre doesn't exist
        video_list = config_service.get("video_list", {}).get(genre, [])
        print(f"PROCESS ROUTER - VIDEO LIST TYPE: {type(video_list)}")
        print(f"PROCESS ROUTER - VIDEO LIST LENGTH: {len(video_list) if video_list else 0}")
        print(f'Look here, empty video list {video_list}')
        
        # Log YouTube audio options if present
        if request.options and "youtube_audio" in request.options:
            youtube_audio = request.options["youtube_audio"]
            logger.info(f"YouTube audio will be applied with URL: {youtube_audio.get('url', 'Not provided')}")
        else:
            # Check if YouTube audio is configured in config
            config_youtube_audio = config_service.get_youtube_audio_config()
            if config_youtube_audio and "url" in config_youtube_audio:
                logger.info(f"YouTube audio from config will be applied with URL: {config_youtube_audio.get('url')}")
            else:
                # Check if music configuration has track_id to use as YouTube audio
                music_config = config_service.get_music_config()
                if music_config and "track_id" in music_config:
                    track_id = music_config.get("track_id")
                    logger.info(f"Music track_id '{track_id}' will be used as YouTube audio source")
        
        # Check if video_list.json exists
        video_list_path = "data/current/video_list.json"
        
        if os.path.exists(video_list_path):
            logger.info(f"Found video_list.json at {video_list_path}")
        else:
            logger.info("No video_list.json found, will use prompts data for captions")
            
        # Create video processor service
        video_processor = VideoProcessorService(config_service)
        
        # Convert request to prompts_data format expected by process_videos
        prompts_data = {
            "creative": request.prompt,
            "polish": request.prompt,
            "final": request.mothership
        }
        
        # Process videos asynchronously with the project_id and options
        processed_videos = await video_processor.process_videos(
            prompts_data, 
            genre, 
            request.options.get("project_id") if request.options else None,
            request.options
        )
        
        logger.info(f"Video processing complete. Created {len(processed_videos)} videos.")
        
        # The final concatenated video should now be included in processed_videos
        # Verify if it was created
        final_videos = [v for v in processed_videos if "final_" in os.path.basename(v)]
        if final_videos:
            logger.info(f"Final concatenated video created: {final_videos[0]}")
        else:
            logger.warning("No final concatenated video was created. This might be an issue.")
            
            # Double-check the output directory
            output_dir = f"./data/media/output/{request.options.get('project_id') if request.options else None}"
            if os.path.exists(output_dir):
                output_files = os.listdir(output_dir)
                logger.info(f"Files in output directory {output_dir}: {output_files}")
        
        return ProcessResponse(
            creative=request.prompt,
            polish=request.prompt,
            final_response=request.mothership,
            status="success",
            message="Video processing completed successfully",
            video_urls=processed_videos
        )
    
    except Exception as e:
        logger.error(f"Error in background video processing: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return ProcessResponse(
            status="error",
            message=f"Error processing videos: {str(e)}",
            video_urls=None
        )

@router.get("/videos", response_model=List[str])
async def get_processed_videos(
    genre: Optional[str] = None,
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Get a list of processed videos.
    
    Args:
        genre: Optional genre filter
        config_service: Configuration service
        
    Returns:
        List[str]: List of video paths
    """
    import os
    
    output_dir = config_service.get("ffmpeg", {}).get("output_directory", "./output")
    
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        return []
    
    # Get all video files in the output directory
    video_files = [
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith(('.mp4', '.mov', '.avi'))
    ]
    
    # Filter by genre if provided
    if genre and video_files:
        genre_files = [v for v in video_files if f"_{genre}_" in v or f"{genre}" in v]
        return genre_files if genre_files else video_files
    
    return video_files

@router.get("/genres", response_model=List[str])
async def get_available_genres(
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Get a list of available video genres.
    
    Args:
        config_service: Configuration service
        
    Returns:
        List[str]: List of available genres
    """
    base_dir = "data/media/videos"
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir, exist_ok=True)
        return []
    
    # Get all directories in the videos directory
    genres = [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
    ]
    
    return genres

@router.post("/generate/audio", response_model=AudioGenerationResponse)
async def generate_audio(
    background_tasks: BackgroundTasks = None,
    force_retry: bool = Query(False, description="Force retry generation of existing files"),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Generate audio files from video_list.json.
    
    Args:
        background_tasks: FastAPI background tasks for async processing
        force_retry: Force retry generation even for files that already exist
        config_service: Configuration service
        
    Returns:
        AudioGenerationResponse: Result of audio generation process
    """
    try:
        # Create audio processor service
        audio_processor = AudioProcessorService(config_service)
        
        video_list_path = "data/current/video_list.json"
        if not os.path.exists(video_list_path):
            raise HTTPException(status_code=404, detail=f"video_list.json not found at {video_list_path}")
        
        # If force_retry is true, rename existing audio files to force regeneration
        if force_retry:
            try:
                # Get all existing audio files
                audio_files = audio_processor._get_audio_files_from_video_list(video_list_path)
                
                # Backup directory for old files
                backup_dir = os.path.join(audio_processor.audio_config["audio_output_dir"], "backup")
                os.makedirs(backup_dir, exist_ok=True)
                
                # Move existing files to backup
                for audio_file in audio_files:
                    if os.path.exists(audio_file):
                        # Create backup filename with timestamp
                        filename = os.path.basename(audio_file)
                        backup_file = os.path.join(backup_dir, f"{int(time.time())}_{filename}")
                        
                        # Move file to backup
                        shutil.move(audio_file, backup_file)
                        logger.info(f"Backed up {audio_file} to {backup_file}")
            except Exception as e:
                logger.error(f"Error backing up audio files: {e}")
                # Continue even if backup fails
        
        # If background_tasks is provided, process in background
        if background_tasks:
            background_tasks.add_task(
                generate_audio_background,
                config_service=config_service
            )
            return AudioGenerationResponse(
                status="processing",
                message="Audio generation started in background",
                audio_files=[]
            )
        
        # Otherwise process immediately (blocking)
        audio_files = await audio_processor.process_audio(video_list_path)
        
        # Check if any files are still missing
        all_required_files = audio_processor._get_audio_files_from_video_list(video_list_path)
        missing_files = [f for f in all_required_files if not os.path.exists(f)]
        
        if missing_files:
            return AudioGenerationResponse(
                status="partial",
                message=f"Generated {len(audio_files)} audio files, but {len(missing_files)} files are still missing",
                audio_files=audio_files,
                missing_files=missing_files
            )
        
        return AudioGenerationResponse(
            status="success",
            message=f"Successfully generated {len(audio_files)} audio files",
            audio_files=audio_files
        )
        
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

async def generate_audio_background(
    config_service: ConfigService
) -> List[str]:
    """
    Generate audio files in the background.
    
    Args:
        config_service: Configuration service
        
    Returns:
        List[str]: Paths to generated audio files
    """
    try:
        logger.info("Starting background audio generation")
        
        # Create audio processor service
        audio_processor = AudioProcessorService(config_service)
        
        # Process audio
        audio_files = await audio_processor.process_audio()
        
        # Check if any files are still missing
        all_required_files = audio_processor._get_audio_files_from_video_list("data/current/video_list.json")
        missing_files = [f for f in all_required_files if not os.path.exists(f)]
        
        if missing_files:
            logger.warning(f"Generated {len(audio_files)} audio files, but {len(missing_files)} files are still missing")
            for missing in missing_files:
                logger.warning(f"Missing audio file: {missing}")
        else:
            logger.info(f"Successfully generated all {len(audio_files)} audio files")
        
        return audio_files
        
    except Exception as e:
        logger.error(f"Error in background audio generation: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []