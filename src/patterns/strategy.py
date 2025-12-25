"""
Strategy pattern implementation for download strategies
"""
from abc import ABC, abstractmethod
from typing import List, Dict
from ..model.video_info import VideoInfo
from ..patterns.observer import Observable


class DownloadStrategy(ABC):
    """Strategy interface for downloading content"""
    
    def __init__(self, observable: Observable = None):
        self.observable = observable or Observable()
    
    @abstractmethod
    def get_available_qualities(self, video_info: VideoInfo) -> List[str]:
        """Get list of available quality options for this strategy"""
        pass
    
    @abstractmethod
    def download(self, video_info: VideoInfo, quality: str, output_path: str) -> bool:
        """Execute the download with the specified quality"""
        pass

