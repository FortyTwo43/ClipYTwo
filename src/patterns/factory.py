"""
Factory pattern implementation to create download strategies
"""
from typing import Optional
from ..patterns.strategy import DownloadStrategy
from ..patterns.template_method import AbstractDownloadStrategy
from ..patterns.adapter import DownloadAdapter
from ..patterns.observer import Observable


class VideoDownloadStrategy(AbstractDownloadStrategy):
    """Concrete strategy for downloading video"""
    
    def __init__(self, adapter: DownloadAdapter, observable: Observable = None):
        super().__init__(adapter, observable)
    
    def _get_quality_type(self) -> str:
        return "video"
    
    def _prepare_download(self, video_info, quality: str, output_path: str) -> dict:
        """Prepare video download parameters"""
        # Ensure output path has video extension
        if not any(output_path.endswith(ext) for ext in ['.mp4', '.webm', '.mkv']):
            output_path = output_path + '.mp4'
        
        return {
            'type': 'video',
            'quality': quality,
            'output_path': output_path
        }
    
    def _execute_download(self, video_info, download_params: dict) -> str:
        """Execute video download"""
        def progress_hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    progress = (downloaded / total) * 100
                    self.observable.notify(f"Descargando: {downloaded}/{total} bytes", progress, "in_progress")
            elif d['status'] == 'finished':
                self.observable.notify("Video descargado, procesando...", 95, "in_progress")
        
        output_path = download_params['output_path']
        quality = download_params['quality']
        
        return self.adapter.download_video(
            video_info,
            quality,
            output_path,
            progress_callback=progress_hook
        )


class AudioDownloadStrategy(AbstractDownloadStrategy):
    """Concrete strategy for downloading audio"""
    
    def __init__(self, adapter: DownloadAdapter, observable: Observable = None):
        super().__init__(adapter, observable)
    
    def _get_quality_type(self) -> str:
        return "audio"
    
    def _prepare_download(self, video_info, quality: str, output_path: str) -> dict:
        """Prepare audio download parameters"""
        # Ensure output path has .mp3 extension
        if not output_path.endswith('.mp3'):
            output_path = output_path + '.mp3'
        
        return {
            'type': 'audio',
            'quality': quality,
            'output_path': output_path
        }
    
    def _execute_download(self, video_info, download_params: dict) -> str:
        """Execute audio download"""
        def progress_hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    progress = (downloaded / total) * 100
                    self.observable.notify(f"Descargando: {downloaded}/{total} bytes", progress, "in_progress")
            elif d['status'] == 'finished':
                self.observable.notify("Audio descargado, convirtiendo a MP3...", 90, "in_progress")
        
        output_path = download_params['output_path']
        quality = download_params['quality']
        
        return self.adapter.download_audio(
            video_info,
            quality,
            output_path,
            progress_callback=progress_hook
        )


class StrategyFactory:
    """Factory to create appropriate download strategy"""
    
    @staticmethod
    def create_strategy(
        download_type: str,
        adapter: DownloadAdapter,
        observable: Observable = None
    ) -> Optional[DownloadStrategy]:
        """
        Factory method to create download strategy
        
        Args:
            download_type: 'video' or 'audio'
            adapter: DownloadAdapter instance
            observable: Observable instance for notifications
        
        Returns:
            DownloadStrategy instance or None if type is invalid
        """
        if download_type.lower() == 'video':
            return VideoDownloadStrategy(adapter, observable)
        elif download_type.lower() == 'audio':
            return AudioDownloadStrategy(adapter, observable)
        else:
            return None

