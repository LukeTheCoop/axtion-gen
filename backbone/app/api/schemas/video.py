"""
Video API Schemas

This module defines Pydantic models for the video API.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class VideoGenerationRequest(BaseModel):
    """Request model for video generation."""
    mothership: str = Field(..., description="The mothership prompt")
    user_prompt: str = Field(..., description="The user's prompt")
    genre: Optional[str] = Field("military", description="Genre/type of video to generate")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options for video generation")

class VideoGenerationResponse(BaseModel):
    """Response model for video generation."""
    creative_output: str = Field(..., description="The creative output from the LLM")
    polish_output: str = Field(..., description="The polished output from the LLM")
    video_urls: Optional[List[str]] = Field(None, description="URLs to the generated videos")
    status: str = Field("success", description="Status of the request")
    message: Optional[str] = Field(None, description="Additional information about the response")

class VideoProcessingRequest(BaseModel):
    """Request model for video processing."""
    prompts: Dict[str, str] = Field(..., description="Prompts for the videos")
    genre: Optional[str] = Field("military", description="Genre/type of videos to use")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options for processing")

class VideoProcessingResponse(BaseModel):
    """Response model for video processing."""
    videos: List[str] = Field(..., description="Paths to the processed videos")
    concatenated_video: Optional[str] = Field(None, description="Path to the concatenated video if requested")
    status: str = Field("success", description="Status of the request")
    message: Optional[str] = Field(None, description="Additional information about the response") 