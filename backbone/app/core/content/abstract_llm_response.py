from abc import ABC, abstractmethod

class AbstractLLMResponse(ABC):
    @abstractmethod
    def generate_response(self, user_prompt: str) -> str:
        """Generate a response to a prompt using the LLM"""
        pass
