"""
Configuration Service

This module provides a configuration service for the application.
"""

import os
import json
import logging
from typing import Any, Dict, Optional, Union, List
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigService:
    """
    Service for retrieving configuration values from a JSON file.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the configuration service.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.env_vars = {}
        
        # Print config for debugging
        print(f"CONFIG SERVICE LOADED FROM: {os.path.abspath(self.config_path)}")
        print(f"CONFIG CONTAINS KEYS: {list(self.config.keys())}")
        if "video_list" in self.config:
            print(f"VIDEO LIST KEYS: {list(self.config.get('video_list', {}).keys())}")
            if "military" in self.config.get("video_list", {}):
                print(f"MILITARY VIDEOS COUNT: {len(self.config.get('video_list', {}).get('military', []))}")
        
        # Load any environment variables from .env file if present
        self._load_env_vars()
        
        # Add default FFmpeg config if not present
        if "ffmpeg" not in self.config:
            self.config["ffmpeg"] = {
                "max_concurrent_processes": 4,
                "font_size": 24,
                "position": "bottom",
                "output_directory": "./output"
            }
            self._save_config()
            
        # Ensure default genre is set
        if "default_genre" not in self.config:
            self.config["default_genre"] = "military"
            self._save_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration from the JSON file.
        
        Returns:
            Dict[str, Any]: The configuration
        """
        if not os.path.exists(self.config_path):
            logger.warning(f"Configuration file not found: {self.config_path}")
            return self._create_default_config()
        
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self._create_default_config()
    
    def _load_env_vars(self) -> None:
        """
        Load environment variables from .env file if present.
        Otherwise, use current environment variables.
        """
        # First check for .env file
        env_path = ".env"
        if os.path.exists(env_path):
            try:
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        key, value = line.split("=", 1)
                        self.env_vars[key.strip()] = value.strip()
                logger.info(f"Environment variables loaded from {env_path}")
            except Exception as e:
                logger.error(f"Error loading environment variables from {env_path}: {e}")
        
        # Also add any environment variables from the OS
        for key, value in os.environ.items():
            if key not in self.env_vars:
                self.env_vars[key] = value
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        Create a default configuration.
        
        Returns:
            Dict[str, Any]: The default configuration
        """
        default_config = {
            "ffmpeg": {
                "max_concurrent_processes": 4,
                "font_size": 24,
                "position": "bottom",
                "output_directory": "./output"
            },
            "default_genre": "military",
            "video_generation": {
                "creative_prompt": "Generate a creative video concept",
                "polish_prompt": "Polish the video concept",
                "story_arc_count": 10,
                "depth_of_mothership": "medium",
                "action_level": "medium",
                "duration": "medium",
                "favorite_videos": []
            },
            "prompts": {
                "military": {
                    "creative": {
                        "prompt": "Generate a military-themed video",
                        "story_arc_count": 9,
                        "depth_of_mothership": "medium",
                        "action_level": "high",
                        "favorite_videos": []
                    },
                    "polish": {
                        "prompt": "Polish the military-themed video",
                        "duration": "medium",
                        "follow_creative": "high",
                        "specific_commands": []
                    }
                },
                "corporate": {
                    "creative": {
                        "prompt": "Generate a corporate-themed video",
                        "story_arc_count": 2,
                        "depth_of_mothership": "low",
                        "action_level": "low",
                        "favorite_videos": []
                    },
                    "polish": {
                        "prompt": "Polish the corporate-themed video",
                        "duration": "short",
                        "follow_creative": "medium",
                        "specific_commands": []
                    }
                }
            },
            "video_list": {
                "military": [],
                "corporate": []
            },
            "memory": {
                "enabled": True,
                "limit": 10
            }
        }
        
        # Create the file
        try:
            with open(self.config_path, "w") as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Default configuration created at {self.config_path}")
        except Exception as e:
            logger.error(f"Error creating default configuration: {e}")
        
        return default_config
    
    def _save_config(self) -> None:
        """Save the current configuration to the JSON file."""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key (str): The configuration key
            default (Any): The default value if the key is not found
            
        Returns:
            Any: The configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set a configuration value by dot-separated path.
        
        Args:
            key (str): The configuration key path (e.g., "prompts.military.creative.prompt")
            value (Any): The value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Handle dot notation for nested paths
            if "." in key:
                parts = key.split(".")
                current = self.config
                
                # Navigate to the nested dictionary
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    if not isinstance(current[part], dict):
                        current[part] = {}
                    current = current[part]
                
                # Set the value
                current[parts[-1]] = value
            else:
                # Simple top-level key
                self.config[key] = value
            
            self._save_config()
            logger.info(f"Successfully updated configuration at path: {key}")
            return True
        except Exception as e:
            logger.error(f"Error setting configuration at path {key}: {e}")
            return False
            
    def delete(self, key: str) -> bool:
        """
        Delete a configuration value by dot-separated path.
        
        Args:
            key (str): The configuration key path (e.g., "prompts.military.creative.prompt")
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Handle dot notation for nested paths
            if "." in key:
                parts = key.split(".")
                current = self.config
                
                # Navigate to the nested dictionary
                for part in parts[:-1]:
                    if part not in current:
                        # Path doesn't exist, nothing to delete
                        return True
                    current = current[part]
                
                # Delete the key if it exists
                if parts[-1] in current:
                    del current[parts[-1]]
            else:
                # Simple top-level key
                if key in self.config:
                    del self.config[key]
            
            self._save_config()
            logger.info(f"Successfully deleted configuration at path: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting configuration at path {key}: {e}")
            return False
    
    def get_memory_config(self) -> Dict[str, Any]:
        """
        Get the memory configuration.
        
        Returns:
            Dict[str, Any]: The memory configuration
        """
        return self.config.get("memory", {"enabled": True, "limit": 10})
    
    def get_audio_config(self) -> Dict[str, Any]:
        """
        Get the audio configuration.
        
        Returns:
            Dict[str, Any]: The audio configuration
        """
        return self.config.get("audio", {})
    
    def get_video_config(self, orientation: str = "mobile") -> Dict[str, Any]:
        """
        Get the video configuration for the specified orientation.
        
        Args:
            orientation (str): The orientation (mobile, desktop)
            
        Returns:
            Dict[str, Any]: The video configuration
        """
        return self.config.get("video", {}).get(orientation, {})
    
    def get_voice_config(self) -> Dict[str, Any]:
        """
        Get the voice configuration.
        
        Returns:
            Dict[str, Any]: The voice configuration
        """
        return self.config.get("voice", {})
    
    def get_music_config(self) -> Dict[str, Any]:
        """
        Get the music configuration.
        
        Returns:
            Dict[str, Any]: The music configuration
        """
        return self.config.get("music", {})
    
    def get_youtube_audio_config(self) -> Dict[str, Any]:
        """
        Get the YouTube audio configuration.
        
        Returns:
            Dict[str, Any]: The YouTube audio configuration
        """
        return self.config.get("youtube_audio", {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """
        Get the output configuration.
        
        Returns:
            Dict[str, Any]: The output configuration
        """
        return self.config.get("output", {})
    
    def get_prompts(self, category: str = None) -> Dict[str, Any]:
        """
        Get prompts for the specified category or all prompts.
        
        Args:
            category (str): The category
            
        Returns:
            Dict[str, Any]: The prompts
        """
        prompts = self.config.get("prompts", {})
        if category:
            return prompts.get(category, {})
        return prompts
    
    def get_video_list(self, category: str = None) -> Dict[str, Any]:
        """
        Get video list for the specified category or all video lists.
        
        Args:
            category (str): The category
            
        Returns:
            Dict[str, Any]: The video list
        """
        video_list = self.config.get("video_list", {})
        print(f"GET_VIDEO_LIST CALLED with category={category}")
        print(f"AVAILABLE VIDEO_LIST KEYS: {list(video_list.keys())}")
        
        if category:
            # If the category doesn't exist but we have a default genre, try that instead
            if category not in video_list and "default_genre" in self.config:
                default_genre = self.config["default_genre"]
                print(f"Category {category} not found in video_list, trying default_genre: {default_genre}")
                if default_genre in video_list:
                    result = video_list.get(default_genre, [])
                    print(f"RETURNING {len(result)} VIDEOS FOR DEFAULT GENRE {default_genre}")
                    return result
            
            result = video_list.get(category, [])
            print(f"RETURNING {len(result)} VIDEOS FOR CATEGORY {category}")
            return result
        return video_list
    
    def update_audio_config(self, update_data: Dict[str, Any]) -> bool:
        """
        Update audio configuration.
        
        Args:
            update_data (Dict[str, Any]): The update data
            
        Returns:
            bool: True if successful
        """
        try:
            if "audio" not in self.config:
                self.config["audio"] = {}
            
            # Deep merge instead of simple update
            self._deep_update(self.config["audio"], update_data)
            
            self._save_config()
            logger.info("Successfully updated audio configuration")
            return True
        except Exception as e:
            logger.error(f"Error updating audio configuration: {e}")
            return False
    
    def update_video_config(self, orientation: str, update_data: Dict[str, Any]) -> bool:
        """
        Update video configuration for a specific orientation.
        
        Args:
            orientation (str): The orientation (e.g., "mobile", "landscape")
            update_data (Dict[str, Any]): The update data
            
        Returns:
            bool: True if successful
        """
        try:
            if "video" not in self.config:
                self.config["video"] = {}
            
            if orientation not in self.config["video"]:
                self.config["video"][orientation] = {}
            
            # Deep merge instead of simple update
            self._deep_update(self.config["video"][orientation], update_data)
            
            self._save_config()
            logger.info(f"Successfully updated video configuration for orientation: {orientation}")
            return True
        except Exception as e:
            logger.error(f"Error updating video configuration: {e}")
            return False
    
    def update_voice_config(self, update_data: Dict[str, Any]) -> bool:
        """
        Update voice configuration.
        
        Args:
            update_data (Dict[str, Any]): The update data
            
        Returns:
            bool: True if successful
        """
        try:
            if "voice" not in self.config:
                self.config["voice"] = {}
                
            # Deep merge instead of simple update
            self._deep_update(self.config["voice"], update_data)
            
            self._save_config()
            logger.info("Successfully updated voice configuration")
            return True
        except Exception as e:
            logger.error(f"Error updating voice configuration: {e}")
            return False
    
    def update_music_config(self, update_data: Dict[str, Any]) -> bool:
        """
        Update music configuration.
        
        Args:
            update_data (Dict[str, Any]): The update data
            
        Returns:
            bool: True if successful
        """
        try:
            if "music" not in self.config:
                self.config["music"] = {}
            
            # Deep merge instead of simple update
            self._deep_update(self.config["music"], update_data)
            
            self._save_config()
            logger.info("Successfully updated music configuration")
            return True
        except Exception as e:
            logger.error(f"Error updating music configuration: {e}")
            return False
    
    def update_youtube_audio_config(self, update_data: Dict[str, Any]) -> bool:
        """
        Update YouTube audio configuration.
        
        Args:
            update_data (Dict[str, Any]): The update data
            
        Returns:
            bool: True if successful
        """
        try:
            if "youtube_audio" not in self.config:
                self.config["youtube_audio"] = {}
            
            # Deep merge instead of simple update
            self._deep_update(self.config["youtube_audio"], update_data)
            
            self._save_config()
            logger.info("Successfully updated YouTube audio configuration")
            return True
        except Exception as e:
            logger.error(f"Error updating YouTube audio configuration: {e}")
            return False
    
    def update_memory_config(self, update_data: Dict[str, Any]) -> bool:
        """
        Update memory configuration.
        
        Args:
            update_data (Dict[str, Any]): The update data
            
        Returns:
            bool: True if successful
        """
        try:
            if "memory" not in self.config:
                self.config["memory"] = {}
            
            # Deep merge instead of simple update
            self._deep_update(self.config["memory"], update_data)
            
            self._save_config()
            logger.info("Successfully updated memory configuration")
            return True
        except Exception as e:
            logger.error(f"Error updating memory configuration: {e}")
            return False
    
    def update_output_config(self, update_data: Dict[str, Any]) -> bool:
        """
        Update output configuration.
        
        Args:
            update_data (Dict[str, Any]): The update data
            
        Returns:
            bool: True if successful
        """
        try:
            if "output" not in self.config:
                self.config["output"] = {}
            
            # Deep merge instead of simple update
            self._deep_update(self.config["output"], update_data)
            
            self._save_config()
            logger.info("Successfully updated output configuration")
            return True
        except Exception as e:
            logger.error(f"Error updating output configuration: {e}")
            return False
    
    def update_prompts(self, category: str, update_data: Dict[str, Any]) -> bool:
        """
        Update prompts for a specific category.
        
        Args:
            category (str): The category
            update_data (Dict[str, Any]): The update data
            
        Returns:
            bool: True if successful
        """
        try:
            if "prompts" not in self.config:
                self.config["prompts"] = {}
            
            if category not in self.config["prompts"]:
                self.config["prompts"][category] = {}
            
            # Deep merge the update_data with existing config
            for key, value in update_data.items():
                if key in self.config["prompts"][category] and isinstance(value, dict) and isinstance(self.config["prompts"][category][key], dict):
                    # For nested dictionaries, recursively update instead of replacing
                    self._deep_update(self.config["prompts"][category][key], value)
                else:
                    # For other types, just set the value
                    self.config["prompts"][category][key] = value
            
            self._save_config()
            logger.info(f"Successfully updated prompts for category: {category}")
            return True
        except Exception as e:
            logger.error(f"Error updating prompts: {e}")
            return False
            
    def _deep_update(self, target_dict: Dict, update_dict: Dict) -> None:
        """
        Deep update a dictionary with another dictionary.
        
        Args:
            target_dict: The dictionary to update
            update_dict: The dictionary with updates
        """
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in target_dict and isinstance(target_dict[key], dict):
                # Recursively update nested dictionaries
                self._deep_update(target_dict[key], value)
            else:
                # Update or add the key
                target_dict[key] = value
    
    def update_video_list(self, category: str, video_list: List[str]) -> bool:
        """
        Update video list for a specific category.
        
        Args:
            category (str): The category
            video_list (List[str]): The video list
            
        Returns:
            bool: True if successful
        """
        try:
            if "video_list" not in self.config:
                self.config["video_list"] = {}
            
            # Set the video list
            self.config["video_list"][category] = video_list
            self._save_config()
            return True
        except Exception as e:
            logger.error(f"Error updating video list: {e}")
            return False
    
    def get_env(self, key: Optional[str] = None, default: Any = None) -> Union[str, Dict[str, str]]:
        """
        Get an environment variable by key or all environment variables.
        
        Args:
            key (Optional[str]): The environment variable key
            default (Any): The default value if the key is not found
            
        Returns:
            Union[str, Dict[str, str]]: The environment variable value or all environment variables
        """
        if key is None:
            return self.env_vars
        
        # First check self.env_vars which includes .env file and os.environ
        if key in self.env_vars:
            return self.env_vars[key]
        
        # If not found, try to get from environment
        return os.environ.get(key, default)

@lru_cache()
def get_config_service() -> ConfigService:
    """
    Get or create the configuration service.
    
    Returns:
        ConfigService: The configuration service
    """
    # Use absolute path to the config.json in the project root
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(root_dir, "config.json")
    print(f"LOADING CONFIG FROM: {config_path}")
    return ConfigService(config_path) 