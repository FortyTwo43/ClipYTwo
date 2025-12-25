"""
Adapter pattern implementation to abstract external library APIs
"""
import os
import yt_dlp
from typing import List, Dict
from ..model.video_info import VideoInfo
from ..patterns.observer import Observable


class DownloadAdapter:
    """
    Adapter to abstract yt-dlp API.
    This allows the application to be independent of the specific library implementation.
    """
    
    def __init__(self, observable: Observable = None):
        self.observable = observable or Observable()
        self.ffmpeg_path = self._get_ffmpeg_path()
    
    def _get_ffmpeg_path(self) -> str:
        """Get ffmpeg executable path"""
        import sys
        
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_dir = sys._MEIPASS
        else:
            # Running as script
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        ffmpeg_path = os.path.join(base_dir, "utils", "ffmpeg.exe")
        return ffmpeg_path if os.path.exists(ffmpeg_path) else "ffmpeg"
    
    def get_video_info(self, url: str) -> VideoInfo:
        """Get video information from URL"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                video_info = VideoInfo(
                    url=url,
                    title=info.get('title', 'Unknown'),
                    duration=info.get('duration', None),
                    formats=info.get('formats', [])
                )
                
                return video_info
        except Exception as e:
            raise Exception(f"Error al obtener información del video: {str(e)}")
    
    def get_available_qualities(self, video_info: VideoInfo, quality_type: str) -> List[str]:
        """
        Get available quality options for video or audio.
        Always returns the best quality first.
        
        Args:
            video_info: VideoInfo object with format information
            quality_type: 'video' or 'audio'
        """
        qualities = set()
        
        if quality_type == 'video':
            # Extract video qualities
            for fmt in video_info.formats:
                height = fmt.get('height')
                if height:
                    qualities.add(f"{height}p")
                elif fmt.get('format_id'):
                    # Fallback to format_id if height not available
                    qualities.add(fmt.get('format_id'))
            # Always add "best" option for video
            qualities.add("best")
        
        elif quality_type == 'audio':
            # Extract audio qualities/bitrates
            for fmt in video_info.formats:
                abr = fmt.get('abr')  # Audio bitrate
                acodec = fmt.get('acodec')
                if acodec and acodec != 'none' and abr:
                    qualities.add(f"{int(abr)}kbps")
                elif acodec and acodec != 'none':
                    qualities.add("best")
            # Always add "best" option for audio if not already present
            if "best" not in qualities:
                qualities.add("best")
        
        # Sort qualities intelligently - best quality first
        # With reverse=True, higher tuple values come first
        sorted_qualities = sorted(qualities, key=self._quality_sort_key, reverse=True)
        
        return list(sorted_qualities) if sorted_qualities else ["best"]
    
    def _quality_sort_key(self, quality: str) -> tuple:
        """
        Helper to sort quality strings.
        Returns tuple for sorting with reverse=True.
        Higher tuple values = higher priority (will be first with reverse=True).
        Best quality should have highest priority (highest tuple value).
        """
        try:
            quality_lower = quality.lower()
            if 'best' in quality_lower:
                # "best" has highest priority - highest tuple value
                return (3, 999999)
            elif 'p' in quality_lower:
                # Video qualities: higher resolution = higher priority
                # Use priority 2 so it comes after "best" but before audio
                return (2, int(quality_lower.replace('p', '')))
            elif 'kbps' in quality_lower:
                # Audio qualities: higher bitrate = higher priority
                # Use priority 1 so it comes after video qualities
                return (1, int(quality_lower.replace('kbps', '')))
            else:
                # Unknown format - lowest priority
                return (0, 0)
        except:
            return (0, 0)
    
    def download_video(self, video_info: VideoInfo, quality: str, output_path: str, progress_callback=None) -> str:
        """Download video with specified quality"""
        try:
            # Determine format selector based on quality
            format_selector = self._get_video_format_selector(quality)
            
            # Extract directory and filename
            output_dir = os.path.dirname(output_path)
            filename = os.path.basename(output_path)
            # Remove extension for template (yt-dlp will add appropriate extension)
            filename_without_ext = os.path.splitext(filename)[0]
            outtmpl = os.path.join(output_dir, filename_without_ext + '.%(ext)s')
            
            ydl_opts = {
                'format': format_selector,
                'outtmpl': outtmpl,
                'ffmpeg_location': self.ffmpeg_path,
                'progress_hooks': [progress_callback] if progress_callback else [],
                'quiet': False,
                'no_warnings': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_info.url])
            
            # Return the actual file path (yt-dlp might have created a file with different extension)
            # Try to find the actual file created
            base_path = os.path.join(output_dir, filename_without_ext)
            for ext in ['.mp4', '.webm', '.mkv', '.m4a']:
                potential_path = base_path + ext
                if os.path.exists(potential_path):
                    # Rename to desired output path if different
                    if potential_path != output_path and os.path.exists(output_path) is False:
                        try:
                            os.rename(potential_path, output_path)
                            return output_path
                        except Exception:
                            return potential_path
                    return potential_path if not os.path.exists(output_path) else output_path
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Error al descargar video: {str(e)}")
    
    def download_audio(self, video_info: VideoInfo, quality: str, output_path: str, progress_callback=None) -> str:
        """Download audio and convert to mp3"""
        try:
            # Determine audio format selector
            format_selector = self._get_audio_format_selector(quality)
            
            # Ensure output path has .mp3 extension
            if not output_path.endswith('.mp3'):
                output_path = os.path.splitext(output_path)[0] + '.mp3'
            
            # Extract directory and filename
            output_dir = os.path.dirname(output_path)
            filename_without_ext = os.path.splitext(os.path.basename(output_path))[0]
            outtmpl = os.path.join(output_dir, filename_without_ext + '.%(ext)s')
            
            ydl_opts = {
                'format': format_selector,
                'outtmpl': outtmpl,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': self._extract_bitrate(quality),
                }],
                'ffmpeg_location': self.ffmpeg_path,
                'progress_hooks': [progress_callback] if progress_callback else [],
                'quiet': False,
                'no_warnings': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_info.url])
            
            # yt-dlp creates .mp3 file after post-processing
            # Return the actual path
            if os.path.exists(output_path):
                return output_path
            # If file exists with different name, return it
            potential_path = os.path.join(output_dir, filename_without_ext + '.mp3')
            if os.path.exists(potential_path):
                return potential_path
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Error al descargar audio: {str(e)}")
    
    def _get_video_format_selector(self, quality: str) -> str:
        """Get format selector string for video quality"""
        if quality == "best":
            return "bestvideo+bestaudio/best"
        elif quality.endswith("p"):
            height = quality.replace("p", "")
            return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
        else:
            return "bestvideo+bestaudio/best"
    
    def _get_audio_format_selector(self, quality: str) -> str:
        """Get format selector string for audio quality"""
        if quality == "best":
            return "bestaudio/best"
        else:
            return "bestaudio/best"
    
    def _extract_bitrate(self, quality: str) -> str:
        """Extract bitrate number from quality string"""
        try:
            if "kbps" in quality.lower():
                return quality.lower().replace("kbps", "")
            return "192"  # Default bitrate
        except:
            return "192"

