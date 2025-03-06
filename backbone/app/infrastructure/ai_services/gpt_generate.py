import os
import sys
import openai
import logging

# Configure logging
logger = logging.getLogger(__name__)

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

class GPTGenerate:
    def __init__(self):
        api_key = config_service.get_env('OPENAI_API_KEY')
        if not api_key:
            logger.warning("No OpenAI API key found, using empty string")
            api_key = ""
        logger.info(f"Initializing OpenAI client (API key {'provided' if api_key else 'missing'})")
        self.client = openai.OpenAI(api_key=api_key)

    def generate_text(self, user_prompt: str, system_prompt: str = None) -> str:
        """
        Generate text using OpenAI's GPT model.
        
        Args:
            user_prompt: The prompt to send to the model
            system_prompt: Optional system prompt to control behavior
            
        Returns:
            The generated text response
        """
        logger.info(f"Generating text with OpenAI (prompt length: {len(user_prompt)})")
        
        messages = []
        
        # Add system message if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            # Default system prompt
            messages.append({"role": "system", "content": "You are a helpful assistant specialized in creating engaging video scripts and descriptions."})
        
        # Add user message
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            logger.info("Sending request to OpenAI API")
            completion = self.client.chat.completions.create(
                model="gpt-4o",
                temperature=0.7,
                messages=messages
            )
            
            result = completion.choices[0].message.content.strip()
            logger.info(f"Received response from OpenAI (length: {len(result)})")
            return result
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def test_generate(self, test_prompt: str) -> str:
        """
        Test method for generating text with OpenAI GPT.
        
        Args:
            test_prompt: The prompt to send to GPT
            
        Returns:
            The generated text response
        """
        logger.info("Using test_generate method with OpenAI")
        
        try:
            system_prompt = "You are an expert at creating video JSON structures. Always respond with valid JSON that includes audio filenames as keys and objects containing source_video, clip, and line fields as values."
            
            logger.info(f"Prompt length: {len(test_prompt)}")
            logger.debug(f"Prompt preview: {test_prompt[:200]}...")
            
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o model
                max_tokens=8000,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": test_prompt}
                ]
            )
            
            result = response.choices[0].message.content.strip()
            logger.info(f"Response received from OpenAI (length: {len(result)})")
            logger.debug(f"Response preview: {result[:200]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error in test_generate: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise


if __name__ == "__main__":
    # Configure logging for the test script
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Simple test script to verify GPT generation is working
    generator = GPTGenerate()
    test_prompt = "Write a short paragraph about artificial intelligence."
    
    print("Testing GPT generation...")
    print("-" * 50)
    print(f"Prompt: {test_prompt}")
    print("-" * 50)
    
    try:
        result = generator.test_generate(test_prompt)
        print("Result:")
        print(result)
    except Exception as e:
        print(f"Error during generation: {e}")
        import traceback
        traceback.print_exc()
