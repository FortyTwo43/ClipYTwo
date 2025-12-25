"""
Facade pattern implementation to simplify download operations
"""
import os
from typing import Optional
from ..model.video_info import VideoInfo
from ..patterns.adapter import DownloadAdapter
from ..patterns.factory import StrategyFactory
from ..patterns.command import DownloadCommand
from ..patterns.observer import Observable


class DownloadFacade:
    """
    Facade to simplify the download process.
    Provides a simple interface hiding the complexity of strategies, adapters, etc.
    """
    
    def __init__(self, observable: Observable = None):
        self.observable = observable or Observable()
        self.adapter = DownloadAdapter(self.observable)
        self.downloads_folder = self._get_downloads_folder()
    
    def _get_downloads_folder(self) -> str:
        """Get downloads folder path"""
        import sys
        
        if getattr(sys, 'frozen', False):
            # Running as compiled executable - use directory where exe is located
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        downloads_folder = os.path.join(base_dir, "downloads")
        os.makedirs(downloads_folder, exist_ok=True)
        return downloads_folder
    
    def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """
        Simplified method to get video information
        
        Args:
            url: YouTube video URL
        
        Returns:
            VideoInfo object or None if error
        """
        try:
            return self.adapter.get_video_info(url)
        except Exception as e:
            self.observable.notify(f"Error al obtener información: {str(e)}", 0, "error")
            return None
    
    def get_available_qualities(self, video_info: VideoInfo, download_type: str) -> list:
        """
        Get available quality options
        
        Args:
            video_info: VideoInfo object
            download_type: 'video' or 'audio'
        
        Returns:
            List of available quality strings
        """
        strategy = StrategyFactory.create_strategy(download_type, self.adapter, self.observable)
        if strategy:
            return strategy.get_available_qualities(video_info)
        return []
    
    def download(
        self,
        video_info: VideoInfo,
        download_type: str,
        quality: str,
        filename: Optional[str] = None
    ) -> bool:
        """
        Simplified method to download video or audio
        
        Args:
            video_info: VideoInfo object
            download_type: 'video' or 'audio'
            quality: Quality string (e.g., '720p', 'best', '192kbps')
            filename: Optional custom filename (without extension)
        
        Returns:
            True if download successful, False otherwise
        """
        try:
            # Create strategy
            strategy = StrategyFactory.create_strategy(download_type, self.adapter, self.observable)
            if not strategy:
                self.observable.notify(f"Tipo de descarga inválido: {download_type}", 0, "error")
                return False
            
            # Generate output path
            if filename:
                safe_filename = self._sanitize_filename(filename)
            else:
                safe_filename = self._sanitize_filename(video_info.title)
            
            extension = '.mp4' if download_type == 'video' else '.mp3'
            output_path = os.path.join(self.downloads_folder, safe_filename + extension)
            
            # Ensure unique filename
            counter = 1
            original_path = output_path
            while os.path.exists(output_path):
                name, ext = os.path.splitext(original_path)
                output_path = f"{name}_{counter}{ext}"
                counter += 1
            
            # Create and execute command
            command = DownloadCommand(strategy, video_info, quality, output_path, self.observable)
            return command.execute()
            
        except Exception as e:
            error_msg = f"Error en la descarga: {str(e)}"
            self.observable.notify(error_msg, 0, "error")
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """Remove invalid characters from filename"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        return filename.strip()

