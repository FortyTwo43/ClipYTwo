"""
Command pattern implementation for download commands
"""
from abc import ABC, abstractmethod
from ..model.video_info import VideoInfo
from ..patterns.strategy import DownloadStrategy
from ..patterns.observer import Observable


class Command(ABC):
    """Command interface"""
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the command"""
        pass


class DownloadCommand(Command):
    """Command to execute a download operation"""
    
    def __init__(
        self,
        strategy: DownloadStrategy,
        video_info: VideoInfo,
        quality: str,
        output_path: str,
        observable: Observable = None
    ):
        self.strategy = strategy
        self.video_info = video_info
        self.quality = quality
        self.output_path = output_path
        self.observable = observable or Observable()
    
    def execute(self) -> bool:
        """Execute the download command"""
        try:
            # Attach observer to strategy if not already attached
            if self.observable and self.strategy.observable:
                for observer in self.observable._observers:
                    self.strategy.observable.attach(observer)
            
            return self.strategy.download(self.video_info, self.quality, self.output_path)
        except Exception as e:
            error_msg = f"Error al ejecutar descarga: {str(e)}"
            self.observable.notify(error_msg, 0, "error")
            return False

