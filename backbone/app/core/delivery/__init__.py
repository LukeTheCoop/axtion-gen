from abc import ABC, abstractmethod

class DeliveryMethod(ABC):
    @abstractmethod
    def deliver(self, video_path: str, caption_segments: List[str], timings: List[Tuple[float, float]]) -> str:
        pass