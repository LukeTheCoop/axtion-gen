class PromptMerger:
    """Class for merging user prompts with additional parameters for different modes"""
    
    @staticmethod
    def merge_creative_prompt(
        user_prompt: str, 
        creative_prompt: str = "",
        story_arc_count: str = 0,
        depth_of_mothership: str = "medium",
        action_level: str = "medium",
        favorite_videos: list = None,
        video_list: list = None
    ) -> str:
        """
        Merge user prompt with creative mode parameters.
        
        Args:
            user_prompt: The original user prompt
            creative_prompt: The creative prompt template to use (optional)
            story_arc_count: Number of story arc examples to create
            depth_of_mothership: Level of commands from the Mothership (low, medium, high)
            action_level: Action level (low, medium, high)
            favorite_videos: List of favorite videos to reference
            video_list: List of video clips to reference
        Returns:
            The merged prompt
        """
        # Initialize empty lists if None is provided
        if favorite_videos is None:
            favorite_videos = []
        
        if video_list is None:
            video_list = []
        
        # Format favorite videos for display
        favorite_videos_str = ", ".join(favorite_videos) if favorite_videos else "None provided"
        
        # Start with the template if provided, otherwise just use the user prompt
        final_prompt = ""
        if creative_prompt:
            final_prompt = creative_prompt.strip() + "\n\n"
        
        # Add the user prompt if we're starting with a template
        final_prompt += f"{user_prompt.strip()}\n\n"
        
        # Add parameters
        final_prompt += f"Create {story_arc_count} story arc examples.\n"
        final_prompt += f"Ensure a {depth_of_mothership} level of commands from the Mothership.\n"
        final_prompt += f"Ensure a {action_level} action level.\n"
        
        # Add video list if available
        if video_list:
            final_prompt += f"\nAvailable video clips: {video_list}\n"
        
        # Add favorite videos if available
        if favorite_videos:
            final_prompt += f"\nPlease try to utilize some of these favorite videos: [{favorite_videos_str}]\n"
        
        return final_prompt
    
    @staticmethod
    def merge_polish_prompt(
        user_prompt: str,
        polish_prompt: str = "",
        duration: str = "medium",
        follow_creative: bool = True,
        specific_commands: list = None,
        video_list: list = None
    ) -> str:
        """
        Merge user prompt with polish mode parameters.
        
        Args:
            user_prompt: The original user prompt with creative output
            polish_prompt: The polish prompt template to use (optional)
            duration: Video duration (short, medium, long)
            follow_creative: Whether to follow the creative output
            specific_commands: List of specific commands to include
            video_list: List of video clips to reference
        Returns:
            The merged prompt
        """
        # Initialize empty lists if None is provided
        if specific_commands is None:
            specific_commands = []
        
        if video_list is None:
            video_list = []
        
        # Format commands for display
        commands_str = ".\n".join(specific_commands) if specific_commands else ""
        
        # Start with the template if provided, otherwise just use the user prompt
        final_prompt = ""
        if polish_prompt:
            final_prompt = polish_prompt.strip() + "\n\n"
        
        # Add the user prompt with creative output
        final_prompt += f"{user_prompt.strip()}\n\n"
        
        # Add parameters
        final_prompt += f"Create a {duration} duration video.\n"
        
        # Add video list if available
        if video_list:
            final_prompt += f"\nAvailable video clips: {video_list}\n"
        
        # Add creative follow instruction if needed
        if follow_creative:
            final_prompt += "\nFollow the creative output closely.\n"
        
        # Add specific commands if available
        if specific_commands:
            final_prompt += f"\nPlease follow these specific commands:\n{commands_str}\n"
        
        return final_prompt
