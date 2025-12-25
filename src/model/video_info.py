"""
VideoInfo model to store video information
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class VideoInfo:
    """Model class to store video metadata"""
    url: str
    title: str
    duration: Optional[int] = None
    formats: List[dict] = None
    
    def __post_init__(self):
        if self.formats is None:
            self.formats = []

