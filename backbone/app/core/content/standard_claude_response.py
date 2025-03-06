from app.core.content.abstract_llm_response import AbstractLLMResponse
from app.infrastructure.ai_services.claude_thinking_generate import ClaudeThinkingGenerate
from app.common.config import ConfigService, get_config_service

class StandardClaudeResponse(AbstractLLMResponse):
    """Implementation of AbstractLLMResponse using Claude without thinking enabled"""
    
    def __init__(self, config_service: ConfigService = None):
        self.config_service = config_service or get_config_service()
        self.claude_service = ClaudeThinkingGenerate(config_service=self.config_service)
    
    def generate_response(self, user_prompt: str) -> str:
        """
        Generate a response to a prompt using Claude without thinking enabled.
        Uses the test_generate method which doesn't have thinking enabled.
        
        Args:
            user_prompt: The prompt to send to Claude
            
        Returns:
            The generated response from Claude
        """
        return self.claude_service.test_generate(user_prompt) 