from fastapi import APIRouter, Depends, HTTPException, Body, Response, status
from typing import Any, Dict, List, Optional

from app.common.config import ConfigService, get_config_service

router = APIRouter(
    prefix="/config",
    tags=["config"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_all_config(config_service: ConfigService = Depends(get_config_service)) -> Dict[str, Any]:
    """Get the entire configuration"""
    return config_service.config


@router.get("/env")
async def get_env_vars(
    key: Optional[str] = None,
    config_service: ConfigService = Depends(get_config_service)
) -> Dict[str, Any]:
    """
    Get environment variables loaded from .env file
    
    If key is provided, returns the specific environment variable.
    Otherwise, returns all environment variables.
    """
    if key:
        value = config_service.get_env(key)
        if value is None:
            raise HTTPException(status_code=404, detail=f"Environment variable '{key}' not found")
        return {key: value}
    return config_service.get_env()


@router.get("/video")
async def get_video_config(
    orientation: str = "mobile", 
    config_service: ConfigService = Depends(get_config_service)
) -> Dict[str, Any]:
    """Get video configuration for the specified orientation"""
    return config_service.get_video_config(orientation)


@router.get("/audio")
async def get_audio_config(config_service: ConfigService = Depends(get_config_service)) -> Dict[str, Any]:
    """Get audio configuration"""
    return config_service.get_audio_config()


@router.get("/voice")
async def get_voice_config(config_service: ConfigService = Depends(get_config_service)) -> Dict[str, Any]:
    """Get voice configuration"""
    return config_service.get_voice_config()


@router.get("/music")
async def get_music_config(config_service: ConfigService = Depends(get_config_service)) -> Dict[str, Any]:
    """Get music configuration"""
    return config_service.get_music_config()


@router.get("/memory")
async def get_memory_config(config_service: ConfigService = Depends(get_config_service)) -> Dict[str, Any]:
    """Get memory configuration"""
    return config_service.get_memory_config()


@router.get("/output")
async def get_output_config(config_service: ConfigService = Depends(get_config_service)) -> Dict[str, Any]:
    """Get output configuration"""
    return config_service.get_output_config()


@router.get("/prompts")
async def get_prompts(
    category: str = None, 
    config_service: ConfigService = Depends(get_config_service)
) -> Dict[str, Any]:
    """Get prompts for the specified category or all prompts"""
    return config_service.get_prompts(category)


@router.get("/video-list")
async def get_video_list(
    category: str = None, 
    config_service: ConfigService = Depends(get_config_service)
) -> Dict[str, Any]:
    """Get video list for the specified category or all video lists"""
    return config_service.get_video_list(category)


# Update endpoints

@router.put("/value")
async def update_config_value(
    path: str,
    value: Any = Body(...),
    config_service: ConfigService = Depends(get_config_service)
) -> Dict[str, bool]:
    """Update a specific configuration value by path"""
    success = config_service.set(path, value)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to update configuration at path: {path}")
    return {"success": True}


@router.delete("/value")
async def delete_config_value(
    path: str,
    config_service: ConfigService = Depends(get_config_service)
) -> Dict[str, bool]:
    """Delete a specific configuration value by path"""
    success = config_service.delete(path)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to delete configuration at path: {path}")
    return {"success": True}


@router.put("/video/{orientation}")
async def update_video_config(
    orientation: str,
    update_data: Dict[str, Any],
    config_service: ConfigService = Depends(get_config_service)
) -> Dict[str, bool]:
    """Update video configuration for specified orientation"""
    success = config_service.update_video_config(orientation, update_data)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to update video configuration for orientation: {orientation}")
    return {"success": True}


@router.put("/audio")
async def update_audio_config(
    update_data: Dict[str, Any],
    config_service: ConfigService = Depends(get_config_service)
) -> Dict[str, bool]:
    """Update audio configuration"""
    success = config_service.update_audio_config(update_data)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update audio configuration")
    return {"success": True}


@router.put("/voice")
async def update_voice_config(
    update_data: Dict[str, Any],
    config_service: ConfigService = Depends(get_config_service)
) -> Dict[str, bool]:
    """Update voice configuration"""
    success = config_service.update_voice_config(update_data)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update voice configuration")
    return {"success": True}


@router.put("/music")
async def update_music_config(
    update_data: Dict[str, Any],
    config_service: ConfigService = Depends(get_config_service)
) -> Dict[str, bool]:
    """Update music configuration"""
    success = config_service.update_music_config(update_data)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update music configuration")
    return {"success": True}


@router.put("/memory")
async def update_memory_config(
    update_data: Dict[str, Any],
    config_service: ConfigService = Depends(get_config_service)
) -> Dict[str, bool]:
    """Update memory configuration"""
    success = config_service.update_memory_config(update_data)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update memory configuration")
    return {"success": True}


@router.put("/output")
async def update_output_config(
    update_data: Dict[str, Any],
    config_service: ConfigService = Depends(get_config_service)
) -> Dict[str, bool]:
    """Update output configuration"""
    success = config_service.update_output_config(update_data)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update output configuration")
    return {"success": True}


@router.put("/prompts/{category}")
async def update_prompts(
    category: str,
    update_data: Dict[str, Any],
    config_service: ConfigService = Depends(get_config_service)
) -> Dict[str, bool]:
    """Update prompts for a specific category"""
    success = config_service.update_prompts(category, update_data)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to update prompts for category: {category}")
    return {"success": True}


@router.put("/video-list/{category}")
async def update_video_list(
    category: str,
    video_list: List[str],
    config_service: ConfigService = Depends(get_config_service)
) -> Dict[str, bool]:
    """Update video list for a specific category"""
    success = config_service.update_video_list(category, video_list)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to update video list for category: {category}")
    return {"success": True}
