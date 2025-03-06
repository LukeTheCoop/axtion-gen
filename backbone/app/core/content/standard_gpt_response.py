from app.core.content.abstract_llm_response import AbstractLLMResponse
from app.common.config import ConfigService, get_config_service
from app.infrastructure.ai_services.gpt_generate import GPTGenerate
import logging

# Configure logging
logger = logging.getLogger(__name__)

class StandardGPTResponse(AbstractLLMResponse):
    """Implementation of AbstractLLMResponse using GPT"""
    
    def __init__(self, config_service: ConfigService = None):
        self.config_service = config_service or get_config_service()
        self.gpt_service = GPTGenerate()
    
    def generate_response(self, list_prompt: str, polish_output: str = None) -> str:
        """
        Generate a response to a prompt using GPT.
        Uses the generate_text method with list_prompt as system prompt and polish_output as user prompt.
        
        Args:
            list_prompt: Instructions and format requirements to use as system prompt
            polish_output: Content to transform, used as the user prompt
            
        Returns:
            The generated response from GPT
        """
        logger.info("Generating response with GPT")
        
        # Use list_prompt as the system prompt
        system_prompt = list_prompt
        logger.info(f"System prompt length: {len(system_prompt)}")
        
        # Use polish_output as the user prompt, or a simple request if None
        if polish_output:
            user_prompt = polish_output
            logger.info(f"User prompt length: {len(user_prompt)}")
        else:
            user_prompt = "Please generate a properly formatted JSON response according to the instructions."
            logger.info("Using default user prompt")
        
        try:
            result = self.gpt_service.generate_text(user_prompt=user_prompt, system_prompt=system_prompt)
            logger.info(f"GPT response received, length: {len(result) if result else 0}")
            return result
        except Exception as e:
            logger.error(f"Error generating GPT response: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise 