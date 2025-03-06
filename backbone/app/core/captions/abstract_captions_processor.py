# core/captions/base_caption_processor.py
from abc import ABC, abstractmethod
from typing import List, Tuple

class BaseCaptionProcessor(ABC):
    @abstractmethod
    def split_caption(self, full_caption: str, duration: float) -> List[str]:
        """
        Splits the full caption into a list of caption segments based on duration.
        """
        pass

    @abstractmethod
    def overlay_captions(self, video_path: str, caption_segments: List[str], timings: List[Tuple[float, float]]) -> str:
        """
        Overlays the provided caption segments onto the video clip.
        Returns the path to the video with captions.
        """
        pass