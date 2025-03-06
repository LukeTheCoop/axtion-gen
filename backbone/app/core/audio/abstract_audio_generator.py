from abc import ABC, abstractmethod

class AbstractAudioGenerator(ABC):
    @abstractmethod
    def generate_audio(self, text: str) -> str:
        #from text to audio
        pass
