import anthropic
import os
import sys
from dotenv import load_dotenv
from app.common.config import ConfigService, get_config_service

class ClaudeThinkingGenerate:
    def __init__(self, config_service: ConfigService = None):
        # Load environment variables from .env file
        load_dotenv()
        # Get or create ConfigService instance
        self.config_service = config_service or get_config_service()
        # Initialize Claude client with API key from environment
        self.client = anthropic.Anthropic(api_key=self.config_service.get_env('ANTRO_CHAT'))

    def generate_text_with_thinking(self, user_prompt: str) -> str:
        """
        Generate a text response from Claude with thinking enabled.
        This returns the final text output, not the thinking process.
        
        Args:
            user_prompt: The prompt to send to Claude
            
        Returns:
            The final text response from Claude
        """
        # Get Claude API configuration
        claude_config = self.config_service.get("claude_api", {})
        
        # Get parameters with defaults
        model = claude_config.get("model", "claude-3-7-sonnet-20250219")
        creative_max_tokens = claude_config.get("creative_max_tokens", 4000)
        creative_temperature = claude_config.get("creative_temperature", 1.0)
        thinking_budget_tokens = claude_config.get("thinking_budget_tokens", 1500)
        
        response = self.client.messages.create(
            model=model,
            max_tokens=creative_max_tokens,
            temperature=creative_temperature,
            thinking={
                "type": "enabled",
                "budget_tokens": thinking_budget_tokens
            },
            messages=[{"role": "user", "content": user_prompt}]
        )

        # Extract the text content (the final response)
        if hasattr(response, 'content') and isinstance(response.content, list):
            for block in response.content:
                if hasattr(block, 'type') and block.type == 'text':
                    if hasattr(block, 'text'):
                        return block.text
        
        # Return empty string if no text content found
        return ""
    
    def test_generate(self, user_prompt: str) -> str:
        """
        Test method for generating text with Claude, with a fixed model and parameters.
        Useful for testing and debugging.
        
        Args:
            user_prompt: The prompt to send to Claude
            
        Returns:
            The generated text response
        """
        # Get Claude API configuration
        claude_config = self.config_service.get("claude_api", {})
        
        # Get parameters with defaults
        model = claude_config.get("model", "claude-3-7-sonnet-20250219")
        polish_max_tokens = claude_config.get("polish_max_tokens", 1000)
        polish_temperature = claude_config.get("polish_temperature", 0.5)
        
        response = self.client.messages.create(
            model=model,
            max_tokens=polish_max_tokens,
            temperature=polish_temperature,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        return response.content[0].text.strip()


if __name__ == "__main__":
    # Get the absolute path of the current script
    current_path = os.path.abspath(__file__)
    
    # Navigate up three directories to reach the project root (app/infrastructure/ai_services -> project root)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_path))))
    
    # Add the project root to the Python path if it's not already there
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Load environment variables from .env file
    load_dotenv(os.path.join(project_root, '.env'))

    # Simple test script to verify Claude generation with thinking enabled
    generator = ClaudeThinkingGenerate()
    test_prompt = "Write a short paragraph about artificial intelligence."
    
    print(f"Testing Claude text generation with thinking enabled. Prompt: '{test_prompt}'")
    
    try:
        # Get the text content with thinking enabled
        result = generator.generate_text_with_thinking(test_prompt)
        
        # Print just the text content
        print("\nFINAL TEXT OUTPUT:")
        print(result)
        
    except Exception as e:
        print(f"Error during generation: {e}")
        import traceback
        traceback.print_exc()