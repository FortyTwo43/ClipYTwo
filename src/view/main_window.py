"""
Main window view using customtkinter
"""
import customtkinter as ctk
from typing import Optional
from ..patterns.observer import Observer
from ..model.video_info import VideoInfo


class MainWindow(ctk.CTk, Observer):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.video_info: Optional[VideoInfo] = None
        self.controller = None
        
        # Configure window
        self.title("Youtube Video Downloader")
        self.geometry("800x500")
        
        # Try to set icon
        try:
            import os
            import sys
            
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                base_dir = sys._MEIPASS
            else:
                # Running as script
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            icon_path = os.path.join(base_dir, "public", "icon", "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create UI components
        self._create_widgets()
        
        # Initial state: only show URL input
        self._show_initial_state()
    
    def set_controller(self, controller):
        """Set the controller reference"""
        self.controller = controller
    
    def _create_widgets(self):
        """Create all UI widgets"""
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # URL input frame
        self.url_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.url_frame.pack(pady=50)
        
        # URL entry
        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="Ingrese la URL...",
            width=500,
            height=35, # antes 40
            font=ctk.CTkFont(size=15)
        )
        self.url_entry.pack(side="left", padx=(0, 10))
        
        # Submit button (arrow)
        self.submit_btn = ctk.CTkButton(
            self.url_frame,
            text="→",
            width=50,
            height=35, # antes 40
            command=self._on_submit_clicked,
            font=ctk.CTkFont(size=15)
        )
        self.submit_btn.pack(side="left")
        
        # Download options frame (initially hidden)
        self.options_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        # Will be packed when needed
        
        # Quality selection frame
        self.quality_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        
        # Video quality dropdown
        self.video_quality_label = ctk.CTkLabel(
            self.quality_frame,
            text="Calidad de Video:",
            font=ctk.CTkFont(size=15)
        )
        self.video_quality_label.pack(side="left", padx=(0, 10))
        
        self.video_quality_combo = ctk.CTkComboBox(
            self.quality_frame,
            values=["best"],
            width=150,
            font=ctk.CTkFont(size=15)
        )
        self.video_quality_combo.pack(side="left", padx=(0, 20))
        
        # Audio quality dropdown
        self.audio_quality_label = ctk.CTkLabel(
            self.quality_frame,
            text="Calidad de Audio:",
            font=ctk.CTkFont(size=15)
        )
        self.audio_quality_label.pack(side="left", padx=(0, 10))
        
        self.audio_quality_combo = ctk.CTkComboBox(
            self.quality_frame,
            values=["best"],
            width=150,
            font=ctk.CTkFont(size=15)
        )
        self.audio_quality_combo.pack(side="left")
        
        # Download buttons frame
        self.download_buttons_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        
        # Download video button
        self.download_video_btn = ctk.CTkButton(
            self.download_buttons_frame,
            text="Descargar Video",
            width=200,
            height=40,
            command=self._on_download_video_clicked,
            font=ctk.CTkFont(size=15)
        )
        self.download_video_btn.pack(side="left", padx=(0, 20))
        
        # Download audio button
        self.download_audio_btn = ctk.CTkButton(
            self.download_buttons_frame,
            text="Descargar Audio",
            width=200,
            height=40,
            command=self._on_download_audio_clicked,
            font=ctk.CTkFont(size=15)
        )
        self.download_audio_btn.pack(side="left")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=17),
            text_color="gray"
        )
        self.status_label.pack(pady=10)
        
        # Progress bar (initially hidden)
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=500)
        self.progress_bar.set(0)
        # Will be packed when needed
    
    def _show_initial_state(self):
        """Show only URL input (initial state)"""
        self.options_frame.pack_forget()
        self.progress_bar.pack_forget()
        self.status_label.configure(text="")
        self.url_entry.delete(0, "end")
    
    def _show_download_options(self, video_info: VideoInfo):
        """Show download options after URL is processed"""
        self.video_info = video_info
        
        # Update quality options
        if self.controller:
            video_qualities = self.controller.get_video_qualities(video_info)
            audio_qualities = self.controller.get_audio_qualities(video_info)
            
            self.video_quality_combo.configure(values=video_qualities)
            if video_qualities:
                self.video_quality_combo.set(video_qualities[0])
            
            self.audio_quality_combo.configure(values=audio_qualities)
            if audio_qualities:
                self.audio_quality_combo.set(audio_qualities[0])
        
        # Show options frame
        self.quality_frame.pack(pady=20)
        self.download_buttons_frame.pack(pady=20)
        self.options_frame.pack(pady=20)
    
    def _hide_download_options(self):
        """Hide download options and return to initial state"""
        self.options_frame.pack_forget()
        self.progress_bar.pack_forget()
        self._show_initial_state()
    
    def _on_submit_clicked(self):
        """Handle submit button click"""
        url = self.url_entry.get().strip()
        if url and self.controller:
            self.status_label.configure(text="Obteniendo información del video...", text_color="white")
            self.submit_btn.configure(state="disabled")
            self.controller.process_url(url)
    
    def _on_download_video_clicked(self):
        """Handle download video button click"""
        if self.video_info and self.controller:
            quality = self.video_quality_combo.get()
            self._start_download()
            self.controller.download_video(self.video_info, quality)
    
    def _on_download_audio_clicked(self):
        """Handle download audio button click"""
        if self.video_info and self.controller:
            quality = self.audio_quality_combo.get()
            self._start_download()
            self.controller.download_audio(self.video_info, quality)
    
    def _start_download(self):
        """Prepare UI for download"""
        self.download_video_btn.configure(state="disabled")
        self.download_audio_btn.configure(state="disabled")
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0)
    
    def _end_download(self):
        """Restore UI after download"""
        self.download_video_btn.configure(state="normal")
        self.download_audio_btn.configure(state="normal")
        self.progress_bar.pack_forget()
    
    # Observer implementation
    def update(self, message: str, progress: float = None, status: str = None):
        """Update UI based on observer notifications"""
        self.status_label.configure(text=message)
        
        if progress is not None:
            self.progress_bar.set(progress / 100.0)
        
        if status == "completed":
            self.status_label.configure(text_color="green")
            self.after(2000, self._hide_download_options)  # Hide options after 2 seconds
            self.submit_btn.configure(state="normal")
            self._end_download()
        elif status == "error":
            self.status_label.configure(text_color="red")
            self.submit_btn.configure(state="normal")
            self._end_download()
        elif status == "in_progress":
            self.status_label.configure(text_color="white")
        else:
            self.status_label.configure(text_color="gray")
    
    def show_video_info_loaded(self):
        """Called when video info is successfully loaded"""
        if self.video_info:
            self._show_download_options(self.video_info)
            self.status_label.configure(text=f"Video: {self.video_info.title}", text_color="green")
        self.submit_btn.configure(state="normal")
    
    def show_video_info_error(self, error_message: str):
        """Called when there's an error loading video info"""
        self.status_label.configure(text=error_message, text_color="red")
        self.submit_btn.configure(state="normal")

