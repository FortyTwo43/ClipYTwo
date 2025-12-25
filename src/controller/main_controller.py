"""
Main controller implementing MVC pattern
"""
import threading
from typing import Optional
from ..model.video_info import VideoInfo
from ..patterns.facade import DownloadFacade
from ..patterns.observer import Observable
from ..view.main_window import MainWindow


class MainController:
    """Main controller coordinating between model, view, and business logic"""
    
    def __init__(self, view: MainWindow):
        self.view = view
        self.observable = Observable()
        self.facade = DownloadFacade(self.observable)
        
        # Attach view as observer
        self.observable.attach(view)
        
        # Set controller reference in view
        view.set_controller(self)
    
    def process_url(self, url: str):
        """Process URL and get video information"""
        def worker():
            try:
                video_info = self.facade.get_video_info(url)
                if video_info:
                    self.view.video_info = video_info
                    self.view.after(0, self.view.show_video_info_loaded)
                else:
                    self.view.after(0, lambda: self.view.show_video_info_error("Error al obtener información del video"))
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                self.view.after(0, lambda: self.view.show_video_info_error(error_msg))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def get_video_qualities(self, video_info: VideoInfo) -> list:
        """Get available video qualities"""
        return self.facade.get_available_qualities(video_info, "video")
    
    def get_audio_qualities(self, video_info: VideoInfo) -> list:
        """Get available audio qualities"""
        return self.facade.get_available_qualities(video_info, "audio")
    
    def download_video(self, video_info: VideoInfo, quality: str):
        """Download video with specified quality"""
        def worker():
            success = self.facade.download(video_info, "video", quality)
            if success:
                self.observable.notify("Descarga de video finalizada", 100, "completed")
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def download_audio(self, video_info: VideoInfo, quality: str):
        """Download audio with specified quality"""
        def worker():
            success = self.facade.download(video_info, "audio", quality)
            if success:
                self.observable.notify("Descarga de audio finalizada", 100, "completed")
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

