import os
import sys
import anthropic

# Add project root to Python path when running the script directly
if __name__ == "__main__":
    # Get the absolute path of the current script
    current_path = os.path.abspath(__file__)
    
    # Navigate up three directories to reach the project root (app/infrastructure/ai_services -> project root)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_path))))
    
    # Add the project root to the Python path if it's not already there
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from app.common.config import get_config_service

config_service = get_config_service()

class ClaudeGenerate:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config_service.get_env('ANTRO_CHAT'))

    def generate_text(self, user_prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=8000,
            temperature=0.7,  # Add some creativity while maintaining coherence
            messages=[{"role": "user", "content": user_prompt}]
        )

        return response.content[0].text.strip()
    def test_generate(self, test_prompt: str) -> str:
        """
        Test method for generating text with Claude, with a fixed model and parameters.
        Useful for testing and debugging.
        
        Args:
            test_prompt: The prompt to send to Claude
            
        Returns:
            The generated text response
        """
        response = self.client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=8000,
            temperature=0.5,  # Lower temperature for more deterministic outputs during testing
            messages=[{"role": "user", "content": test_prompt}]
        )
        
        return response.content[0].text.strip()


if __name__ == "__main__":
    # Simple test script to verify Claude generation is working
    generator = ClaudeGenerate()
    test_prompt = "Write a short paragraph about artificial intelligence."
    
    print("Testing Claude generation...")
    print("-" * 50)
    print(f"Prompt: {test_prompt}")
    print("-" * 50)
    
    try:
        result = generator.test_generate(test_prompt)
        print("Result:")
        print(result)
    except Exception as e:
        print(f"Error during generation: {e}")
