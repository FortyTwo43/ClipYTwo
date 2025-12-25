"""
Template Method pattern implementation
"""
from abc import ABC, abstractmethod
from typing import List
import os
from ..model.video_info import VideoInfo
from ..patterns.strategy import DownloadStrategy
from ..patterns.observer import Observable


class AbstractDownloadStrategy(DownloadStrategy):
    """
    Abstract base class implementing Template Method pattern.
    Defines the skeleton of the download algorithm.
    """
    
    def __init__(self, adapter, observable: Observable = None):
        super().__init__(observable)
        self.adapter = adapter
        self.ffmpeg_path = self._get_ffmpeg_path()
    
    def _get_ffmpeg_path(self) -> str:
        """Template method step: Get ffmpeg path"""
        import sys
        
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_dir = sys._MEIPASS
        else:
            # Running as script
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        ffmpeg_path = os.path.join(base_dir, "utils", "ffmpeg.exe")
        return ffmpeg_path if os.path.exists(ffmpeg_path) else "ffmpeg"
    
    def download(self, video_info: VideoInfo, quality: str, output_path: str) -> bool:
        """
        Template method: defines the skeleton of download algorithm.
        Steps are fixed but implementation can vary.
        """
        try:
            # Step 1: Validate inputs
            if not self._validate_inputs(video_info, quality, output_path):
                return False
            
            # Step 2: Prepare download
            self.observable.notify("Descarga iniciada", 0, "in_progress")
            download_params = self._prepare_download(video_info, quality, output_path)
            
            # Step 3: Execute download
            temp_file = self._execute_download(video_info, download_params)
            
            if not temp_file:
                return False
            
            # Step 4: Post-process (if needed)
            final_file = self._post_process(temp_file, output_path)
            
            # Step 5: Cleanup
            self._cleanup(temp_file, final_file)
            
            self.observable.notify("Descarga finalizada", 100, "completed")
            return True
            
        except Exception as e:
            error_msg = f"Ha ocurrido un error desconocido: {str(e)}"
            self.observable.notify(error_msg, 0, "error")
            return False
    
    # Template method steps - can be overridden
    def _validate_inputs(self, video_info: VideoInfo, quality: str, output_path: str) -> bool:
        """Template step: Validate inputs"""
        if not video_info or not video_info.url:
            self.observable.notify("URL inválida", 0, "error")
            return False
        if not quality:
            self.observable.notify("Calidad no especificada", 0, "error")
            return False
        if not output_path:
            self.observable.notify("Ruta de salida no especificada", 0, "error")
            return False
        return True
    
    @abstractmethod
    def _prepare_download(self, video_info: VideoInfo, quality: str, output_path: str) -> dict:
        """Template step: Prepare download parameters (varies by strategy)"""
        pass
    
    @abstractmethod
    def _execute_download(self, video_info: VideoInfo, download_params: dict) -> str:
        """Template step: Execute the actual download (varies by strategy)"""
        pass
    
    def _post_process(self, temp_file: str, output_path: str) -> str:
        """Template step: Post-process downloaded file (optional, can be overridden)"""
        return temp_file
    
    def _cleanup(self, temp_file: str, final_file: str):
        """Template step: Cleanup temporary files"""
        if temp_file != final_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
    
    @abstractmethod
    def _get_quality_type(self) -> str:
        """Template step: Get quality type ('video' or 'audio')"""
        pass
    
    def get_available_qualities(self, video_info: VideoInfo) -> List[str]:
        """Template step: Get available qualities (implemented in subclasses)"""
        return self.adapter.get_available_qualities(video_info, self._get_quality_type())

