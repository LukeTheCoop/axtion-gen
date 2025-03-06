from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.api.routers import process
from app.api.routers import config  # Import the config router
from app.core.content.claude_llm_response import ClaudeLLMResponse
from app.core.content.standard_claude_response import StandardClaudeResponse
from app.core.content.standard_gpt_response import StandardGPTResponse
from app.core.content.merge_prompt import PromptMerger
from app.common.config import ConfigService, get_config_service
import os
import re
import json
import shutil  # Added import for folder clearing functionality

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Video Generation API",
    description="API for generating video ideas and scripts using Claude",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(process.router, prefix="/api", tags=["process"])
app.include_router(config.router, prefix="/api", tags=["config"])  

def clear_data_directories():
    folders_to_clear = ["data/current", "output"]
    
    for folder in folders_to_clear:
        if os.path.exists(folder):
            logger.info(f"Clearing contents of {folder}")
            shutil.rmtree(folder)  # Remove the folder and its contents

    os.makedirs("data/current", exist_ok=True)
    os.makedirs("output", exist_ok=True)

# Add direct endpoints for backwards compatibility
@app.get("/captions/enabled")
async def captions_enabled():
    """Check if captions are enabled"""
    return {"enabled": True}

@app.get("/memory")
async def memory_shortcut(config_service: ConfigService = Depends(get_config_service)):
    """Direct access to memory configuration for backwards compatibility"""
    return config_service.get_memory_config()

# Simple startup event
@app.on_event("startup")
async def startup_event():
    """Run initialization tasks on startup"""
    # Initialize data directories
    import os
    
    # Create necessary directories if they don't exist
    # Clear current and output directories if they exist
    clear_data_directories()
    
    # Recreate necessary directories
    os.makedirs("data/current", exist_ok=True)
    os.makedirs("data/media/videos/military", exist_ok=True)
    os.makedirs("data/media/videos/corporate", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    # Ensure the FFmpeg executable is available
    try:
        from app.infrastructure.ffmpeg.ffmpeg_utils import check_ffmpeg
        check_ffmpeg()
        logger.info("FFmpeg is available and ready to use.")
    except Exception as e:
        logger.warning(f"FFmpeg check failed: {e}. Video processing may not work correctly.")
    
    logger.info("Application startup complete. Using configuration from config.json.")

def extract_json_from_text(text):
    """
    Extract JSON from text, handling various formats including:
    - JSON surrounded by markdown code blocks
    - JSON with text before or after
    - Plain JSON
    - Special case handling for video_list.json structure
    - Handling truncated JSON responses
    
    Args:
        text (str): The text containing JSON
        
    Returns:
        dict: The extracted JSON as a dict, or empty dict if extraction fails
    """
    logger.info(f"Extracting JSON from text (length: {len(text)})...")
    
    # Special case: Look for patterns that might resemble video_list format
    video_pattern = r'audio_\d+\.mp3.*source_video.*clip.*line'
    if re.search(video_pattern, text, re.DOTALL):
        logger.info("Found potential video list structure")
        
        # Check if this is a markdown code block
        if text.strip().startswith('```') and '```' in text:
            logger.info("JSON appears to be in a markdown code block")
            
            # Try to find JSON in markdown code blocks first
            json_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
            matches = re.findall(json_block_pattern, text)
            
            if matches:
                logger.debug(f"Found {len(matches)} potential JSON code blocks")
                for i, match in enumerate(matches):
                    logger.debug(f"Match {i+1}: {match[:100]}...")
                    try:
                        # Clean the match from any escape characters
                        clean_match = match.strip()
                        parsed_json = json.loads(clean_match)
                        if parsed_json and isinstance(parsed_json, dict):
                            logger.info(f"Successfully parsed JSON from code block {i+1}")
                            return parsed_json
                    except json.JSONDecodeError as e:
                        logger.debug(f"Failed to parse JSON block {i+1}: {e}")
                        # Try to fix truncated JSON in code block
                        try:
                            fixed_json = _fix_truncated_json(clean_match)
                            parsed_json = json.loads(fixed_json)
                            if parsed_json and isinstance(parsed_json, dict):
                                logger.info(f"Successfully parsed fixed JSON from code block {i+1}")
                                return parsed_json
                        except json.JSONDecodeError as e2:
                            logger.debug(f"Failed to parse fixed JSON block {i+1}: {e2}")
                            continue
            
    # Special case for video_list.json format with direct extraction
    video_list_pattern = r'{\s*(?:"audio_\d+\.mp3"\s*:\s*{[^}]*},?\s*)+}'
    video_list_matches = re.search(video_list_pattern, text, re.DOTALL)
    if video_list_matches:
        try:
            video_list_json = video_list_matches.group(0)
            logger.info(f"Found video_list.json format directly, length: {len(video_list_json)}")
            try:
                parsed_json = json.loads(video_list_json)
                logger.info(f"Successfully parsed video_list JSON format with {len(parsed_json)} entries")
                return parsed_json
            except json.JSONDecodeError as e:
                logger.debug(f"Failed to parse video_list format: {e}")
                # Try with fixing
                try:
                    fixed_json = _fix_truncated_json(video_list_json)
                    parsed_json = json.loads(fixed_json)
                    logger.info(f"Successfully parsed fixed video_list JSON with {len(parsed_json)} entries")
                    return parsed_json
                except json.JSONDecodeError as e2:
                    logger.debug(f"Failed to parse fixed video_list format: {e2}")
        except Exception as e:
            logger.debug(f"Error during direct video_list extraction: {e}")
    
    # Try to find JSON in markdown code blocks (if not already tried above)
    json_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    matches = re.findall(json_block_pattern, text)
    
    if matches:
        logger.debug(f"Found {len(matches)} potential JSON code blocks")
        for i, match in enumerate(matches):
            logger.debug(f"Match {i+1}: {match[:100]}...")
            try:
                # Clean the match from any escape characters
                clean_match = match.strip()
                parsed_json = json.loads(clean_match)
                if parsed_json and isinstance(parsed_json, dict):
                    logger.info(f"Successfully parsed JSON from code block {i+1}")
                    return parsed_json
            except json.JSONDecodeError as e:
                logger.debug(f"Failed to parse JSON block {i+1}: {e}")
                try:
                    fixed_json = _fix_truncated_json(clean_match)
                    parsed_json = json.loads(fixed_json)
                    if parsed_json and isinstance(parsed_json, dict):
                        logger.info(f"Successfully parsed fixed JSON from code block {i+1}")
                        return parsed_json
                except json.JSONDecodeError:
                    continue
    
    # If there are no matches with code blocks, look for direct pattern
    # Extract entries that match the audio_*.mp3 pattern directly
    audio_entries_pattern = r'"(audio_\d+\.mp3)"\s*:\s*{([^{}]*(?:{[^{}]*}[^{}]*)*?)}'
    entries = re.findall(audio_entries_pattern, text, re.DOTALL)
    
    if entries:
        logger.info(f"Found {len(entries)} audio entries using direct pattern matching")
        video_list = {}
        
        for audio_file, content in entries:
            # Parse fields in the entry
            source_video_match = re.search(r'"source_video"\s*:\s*"([^"]*)"', content)
            clip_match = re.search(r'"clip"\s*:\s*"([^"]*)"', content)
            line_match = re.search(r'"line"\s*:\s*"([^"]*)"', content)
            
            entry = {}
            if source_video_match:
                entry["source_video"] = source_video_match.group(1)
            else:
                entry["source_video"] = "default_video.mp4"
                
            if clip_match:
                entry["clip"] = clip_match.group(1)
            else:
                entry["clip"] = f"clip_{audio_file.replace('audio_', '').replace('.mp3', '')}.mp4"
                
            if line_match:
                entry["line"] = line_match.group(1)
            else:
                # Check if there's partial line data
                line_partial_match = re.search(r'"line"\s*:\s*"([^"]*)', content)
                if line_partial_match:
                    entry["line"] = line_partial_match.group(1) + "..."
                else:
                    entry["line"] = "Default caption"
            
            video_list[audio_file] = entry
        
        if video_list:
            logger.info(f"Successfully created video_list with {len(video_list)} entries through pattern matching")
            return video_list
    
    # Look for JSON between curly braces as a last resort
    try:
        # Find the first opening brace and the last closing brace
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            json_str = text[start_idx:end_idx+1]
            logger.debug(f"Found JSON between braces: {json_str[:100]}...")
            try:
                parsed_json = json.loads(json_str)
                if parsed_json and isinstance(parsed_json, dict):
                    logger.info("Successfully parsed JSON between braces")
                    return parsed_json
            except json.JSONDecodeError as e:
                logger.debug(f"Failed to parse JSON between braces: {e}")
                # Try to fix truncated JSON and parse again
                try:
                    fixed_json = _fix_truncated_json(json_str)
                    parsed_json = json.loads(fixed_json)
                    if parsed_json and isinstance(parsed_json, dict):
                        logger.info("Successfully parsed fixed JSON between braces")
                        return parsed_json
                except json.JSONDecodeError as e2:
                    logger.debug(f"Failed to parse fixed JSON between braces: {e2}")
    except Exception as e:
        logger.debug(f"Error during JSON extraction: {e}")
    
    logger.warning("Failed to extract JSON from text using any method")
    logger.warning("Returning empty dictionary as fallback")
    return {}

def _fix_truncated_json(json_str):
    """
    Attempt to fix truncated JSON by:
    1. Ensuring all properties have values
    2. Ensuring all objects are properly closed
    3. Ensuring the entire structure is properly closed
    
    Args:
        json_str (str): The potentially truncated JSON string
        
    Returns:
        str: A fixed JSON string that might be parseable
    """
    logger.info("Attempting to fix truncated JSON")
    
    # If the JSON string doesn't end with }, add it
    if not json_str.rstrip().endswith('}'):
        # Count open and close braces
        open_count = json_str.count('{')
        close_count = json_str.count('}')
        
        # Add missing closing braces
        if open_count > close_count:
            missing_braces = open_count - close_count
            json_str = json_str.rstrip() + '"' + '"' * (json_str.rstrip().endswith(':')) + '}' * missing_braces
            logger.debug(f"Added {missing_braces} closing braces to fix JSON structure")
    
    # Find incomplete property definitions (property name without value)
    incomplete_prop_pattern = r'"([^"]+)"\s*:\s*(?!["{}\[\]0-9])'
    if re.search(incomplete_prop_pattern, json_str):
        # Fix by adding a default value
        json_str = re.sub(incomplete_prop_pattern, r'"\1": "default"', json_str)
        logger.debug("Fixed incomplete properties in JSON")
    
    # Check for comma after the last property in an object
    trailing_comma_pattern = r',(\s*})'
    if re.search(trailing_comma_pattern, json_str):
        # Remove trailing commas
        json_str = re.sub(trailing_comma_pattern, r'\1', json_str)
        logger.debug("Removed trailing commas in JSON")
    
    logger.debug(f"Fixed JSON: {json_str[:100]}...")
    return json_str

def ensure_video_list_format(json_data, genre):
    """
    Ensure the JSON data has the correct structure for video_list.json.
    
    Args:
        json_data (dict): The extracted JSON data
        genre (str): The video genre for defaults
        
    Returns:
        dict: Properly formatted video_list.json structure
    """
    logger.info("Ensuring video_list.json has the correct structure")
    
    # Check if it's already in the correct format
    # The format should be: {"audio_X.mp3": {"source_video": "...", "clip": "...", "line": "..."}, ...}
    
    # If the JSON is not a dictionary, convert it to one
    if not isinstance(json_data, dict):
        logger.warning(f"JSON data is not a dictionary, converting: {type(json_data)}")
        if isinstance(json_data, list) and json_data:
            # Convert list to dictionary with audio keys
            json_data = {
                f"audio_{i+1}.mp3": item if isinstance(item, dict) else {"line": str(item)}
                for i, item in enumerate(json_data)
            }
        else:
            logger.warning("Cannot convert JSON to proper format, using empty dict")
            json_data = {}
    
    # Check each entry to ensure it has the required fields
    formatted_data = {}
    for key, value in json_data.items():
        # Skip non-audio entries or convert them
        if not key.startswith("audio_") and not key.endswith(".mp3"):
            # Try to convert to audio entry if it looks like a number or index
            if key.isdigit() or (isinstance(key, int)):
                new_key = f"audio_{key}.mp3"
            else:
                # Use the key as a line in a new entry
                new_key = f"audio_{len(formatted_data)+1}.mp3"
                
            logger.debug(f"Converted key '{key}' to '{new_key}'")
            key = new_key
        
        # Ensure the value is a dictionary with required fields
        if not isinstance(value, dict):
            # Convert to proper structure
            if isinstance(value, str):
                value = {"line": value, "source_video": f"{genre}_video_default.mp4", "clip": f"clip_{len(formatted_data)+1}.mp4"}
            else:
                value = {"line": str(value), "source_video": f"{genre}_video_default.mp4", "clip": f"clip_{len(formatted_data)+1}.mp4"}
        
        # Ensure all required fields exist
        if "source_video" not in value:
            value["source_video"] = f"{genre}_video_default.mp4"
        if "clip" not in value:
            value["clip"] = f"clip_{key.replace('audio_', '').replace('.mp3', '')}"
        if "line" not in value:
            value["line"] = f"Caption for {key}"
        
        formatted_data[key] = value
    
    # If no entries were found, create at least one default entry
    if not formatted_data:
        formatted_data = {
            "audio_1.mp3": {
                "source_video": f"{genre}_video_default.mp4",
                "clip": "clip_1.mp4",
                "line": "Default caption"
            }
        }
    
    logger.info(f"Formatted video_list with {len(formatted_data)} entries")
    return formatted_data

def extract_and_merge_json_from_text(text):
    json_objects = []
    json_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    matches = re.findall(json_block_pattern, text)
    
    for match in matches:
        clean_match = match.strip()
        try:
            parsed_json = json.loads(clean_match)
            if isinstance(parsed_json, dict):
                json_objects.append(parsed_json)
        except json.JSONDecodeError:
            try:
                fixed_json = _fix_truncated_json(clean_match)
                parsed_json = json.loads(fixed_json)
                if isinstance(parsed_json, dict):
                    json_objects.append(parsed_json)
            except json.JSONDecodeError:
                continue
    
    # Merge the dictionaries (if keys conflict, later ones will override earlier ones)
    merged_json = {}
    for obj in json_objects:
        merged_json.update(obj)
    
    return merged_json

def start_video_pipeline(
    mothership: str,
    user_prompt: str,
    config_service: ConfigService,
    genre: str = "military"  # Default to military genre if not specified
) -> tuple:
    """
    Start the video generation pipeline.
    
    Args:
        mothership: The mothership prompt
        user_prompt: The user's prompt
        config_service: The config service instance
        genre: The genre/type of video to generate (e.g., military, corporate)
        
    Returns:
        Tuple of (creative_output, polish_output)
    """
    clear_data_directories()
    logger.info(f"Starting video generation pipeline for {genre} video with prompt: {user_prompt[:50]}...")
    
    # Verify the genre exists in the configuration
    available_genres = config_service.get("video_list", {}).keys()
    print(f"MAIN PIPELINE - AVAILABLE GENRES: {list(available_genres)}")
    
    # If the requested genre doesn't exist in the config, fall back to the default
    if genre not in available_genres:
        default_genre = config_service.get("default_genre", "military")
        print(f"MAIN PIPELINE - REQUESTED GENRE '{genre}' NOT FOUND, USING DEFAULT: {default_genre}")
        genre = default_genre
    
    # Load genre-specific configurations
    # 1. Check for genre-specific prompts
    genre_prompts = config_service.get("prompts", {}).get(genre, {})
    print(f"MAIN PIPELINE - PROMPTS: Found {len(genre_prompts)} keys for genre '{genre}'")
    
    # 2. Get genre-specific video list
    video_list = config_service.get("video_list", {}).get(genre, [])
    print(f"MAIN PIPELINE - CONFIG SERVICE TYPE: {type(config_service)}")
    print(f"MAIN PIPELINE - CONFIG SERVICE ID: {id(config_service)}")
    print(f"MAIN PIPELINE - VIDEO LIST TYPE: {type(video_list)}")
    print(f"MAIN PIPELINE - VIDEO LIST LENGTH: {len(video_list)}")
    
    print(config_service)
    print(f'HERE IS VIDEO LIST:\n\n{video_list}')
    
    # 3. Get creative parameters
    creative_config = genre_prompts.get("creative", {})
    creative_template = creative_config.get("prompt")
    story_arc_count = creative_config.get("story_arc_count")
    depth_of_mothership = creative_config.get("depth_of_mothership", "medium")
    action_level = creative_config.get("action_level", "medium")
    favorite_videos = creative_config.get("favorite_videos", [])
    
    # 4. Get polish parameters
    polish_config = genre_prompts.get("polish", {})
    polish_template = polish_config.get("prompt", "")
    duration = polish_config.get("duration", "medium")
    
    # Handle the case where follow_creative might be a string like "high" instead of boolean
    if isinstance(polish_config.get("follow_creative"), str):
        follow_creative = polish_config.get("follow_creative", "medium") != "none"
    else:
        follow_creative = polish_config.get("follow_creative", True)

    specific_commands = polish_config.get("specific_commands", [])
    
    # Fall back to global settings from video_generation if genre-specific config is missing
    # if not creative_template:
    #     creative_template = video_gen_config.get("creative_prompt", "")
    # if not story_arc_count:
    #     print('FOUND NO STORY ARC')
    #     story_arc_count = video_gen_config.get("story_arc_count")
    # if not depth_of_mothership:
    #     depth_of_mothership = video_gen_config.get("depth_of_mothership", "medium")
    # if not action_level:
    #     action_level = video_gen_config.get("action_level", "medium")
    # if not favorite_videos:
    #     favorite_videos = video_gen_config.get("favorite_videos", [])
    # if not polish_template:
    #     polish_template = video_gen_config.get("polish_prompt", "")
    # if not duration:
    #     duration = video_gen_config.get("duration", "medium")
    # if not specific_commands:
    #     specific_commands = video_gen_config.get("specific_commands", [])
    
    # Initialize LLM services with config
    creative_llm = ClaudeLLMResponse(config_service)
    polish_llm = StandardClaudeResponse(config_service)
    final_llm = StandardGPTResponse(config_service)
    
    # Step 1: Combine the mothership and user prompt for the creative phase
    
    combined_prompt = f"MOTHERSHIP PROMPT: {mothership}\n\nUSER PROMPT: {user_prompt}"
    
    # Step 2: Merge with creative parameters
    final_creative_prompt = PromptMerger.merge_creative_prompt(
        user_prompt=combined_prompt,
        creative_prompt=creative_template,  # Using the template from config
        story_arc_count=story_arc_count,
        depth_of_mothership=depth_of_mothership,
        action_level=action_level,
        favorite_videos=favorite_videos,
        video_list=video_list
    )
    
    # Step 3: Generate creative response with thinking
    logger.info("Generating creative response with thinking...")
    print(f'FINAL CREATIVE PROMPT: {final_creative_prompt}')
    creative_output = creative_llm.generate_response(final_creative_prompt)

    # Step 4: Merge with polish parameters, including the creative output
    final_polish_prompt = PromptMerger.merge_polish_prompt(
        user_prompt=f"{combined_prompt}\n\nCreative output:\n{creative_output}",
        polish_prompt=polish_template,  # Using the template from config
        duration=duration,
        follow_creative=follow_creative,
        specific_commands=specific_commands,
        video_list=video_list
    )
    
    # Step 5: Generate polish response without thinking
    logger.info("Generating polish response without thinking...")
    polish_output = polish_llm.generate_response(final_polish_prompt)

    # Get the list prompt from genre_prompts
    list_prompt = genre_prompts.get("list", "")
    list_prompt +=  f'{str(video_list)} Here is the script: {polish_output}'
    final_response = ''
    
    # Send to GPT for list generation - list_prompt acts as system instructions,
    # while polish_output provides the content to be transformed into a structured list
    while 'finish' not in final_response.lower():
        final_response += creative_llm.generate_response(f'{list_prompt}, current progress {final_response}')
    
    # Extract JSON from the final response and save it to a file
    logger.info(f"Extracting JSON structure from final response (length: {len(final_response)})")
    video_list_json = extract_and_merge_json_from_text(final_response)
    
    # Ensure video_list.json is always created/overwritten
    json_file_path = os.path.join("data", "current", "video_list.json")
    
    if video_list_json:
        logger.info(f"Successfully extracted JSON with {len(video_list_json)} entries")
        # Ensure the JSON has the correct structure
        video_list_json = ensure_video_list_format(video_list_json, genre)
    else:
        # Create a default structure if no valid JSON was found
        logger.warning("No valid JSON found in final response, creating default structure")
        # Use a sample structure based on the polish output
        lines = [line.strip() for line in polish_output.split('\n') if line.strip() and len(line.strip()) > 5][:10]
        if not lines:
            lines = ["Default caption"]
            
        video_list_json = {
            f"audio_{i+1}.mp3": {
                "source_video": f"{genre}_video_example.mp4",
                "clip": f"clip_{i+1}.mp4",
                "line": line
            }
            for i, line in enumerate(lines)
        }
    
    # Always write to the file, regardless of content
    try:
        # Explicitly delete any existing file first to ensure overwrite
        if os.path.exists(json_file_path):
            logger.info(f"Removing existing video_list.json file")
            os.remove(json_file_path)
            
        # Write the new file
        with open(json_file_path, "w") as f:
            json.dump(video_list_json, f, indent=2)
        logger.info(f"Successfully saved video_list.json to {json_file_path}")
        
        # Debug output to verify file was written
        file_size = os.path.getsize(json_file_path)
        logger.info(f"video_list.json file size: {file_size} bytes")
    except Exception as e:
        logger.error(f"Error saving video_list.json: {e}")
    
    logger.info("Video generation pipeline completed successfully!")
    return creative_output, polish_output, final_response

async def clear_processing_folders():
    """
    Clears the 'current' and 'output' folders after pipeline processing is complete.
    Removes all files but preserves the folder structure.
    """
    folders_to_clear = [
        os.path.join("data", "current"),
        os.path.join("data", "output")
    ]
    
    logger.info("Clearing processing folders...")
    
    for folder in folders_to_clear:
        if os.path.exists(folder):
            logger.info(f"Clearing contents of {folder}")
            try:
                # Remove all files and subdirectories in the folder
                for item in os.listdir(folder):
                    item_path = os.path.join(folder, item)
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                logger.info(f"Successfully cleared {folder}")
            except Exception as e:
                logger.error(f"Error clearing {folder}: {e}")
        else:
            logger.warning(f"Folder {folder} does not exist, skipping cleanup")

async def process_videos_with_ffmpeg(creative_output: str, polish_output: str, genre: str):
    """
    Process videos using FFmpeg based on creative and polish outputs.
    
    Args:
        creative_output: The creative output from the LLM
        polish_output: The polished output from the LLM
        genre: The genre/type of video to generate
        
    Returns:
        List[str]: List of processed video file paths
    """
    from app.api.services.video_processor import VideoProcessorService
    from app.common.config import get_config_service
    
    logger.info(f"Starting FFmpeg video processing for {genre}...")
    
    # Get config service
    config_service = get_config_service()
    
    # Create video processor service
    video_processor = VideoProcessorService(config_service)
    
    # Prepare prompts data
    prompts_data = {
        "creative": creative_output,
        "polish": polish_output
    }
    
    # Process videos asynchronously
    try:
        processed_videos = await video_processor.process_videos(prompts_data, genre)
        
        # Optionally concatenate videos
        if config_service.get("ffmpeg", {}).get("concatenate_videos", False):
            output_path = f"output/final_{genre}_video.mp4"
            await video_processor.concatenate_videos(processed_videos, output_path)
            
        logger.info(f"FFmpeg video processing completed with {len(processed_videos)} videos.")
        
        # Clear processing folders after the pipeline completes
        await clear_processing_folders()
        
        return processed_videos
    
    except Exception as e:
        logger.error(f"Error in FFmpeg video processing: {e}")
        return []

@app.get("/")
async def root():
    """Root endpoint to verify API is running"""
    return {"status": "operational", "version": "1.0.0"}

# Add this block to make the script runnable directly
if __name__ == "__main__":
    import uvicorn
    import os
    import sys
    
    # Add the parent directory to sys.path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        
    # Run the FastAPI app with uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
