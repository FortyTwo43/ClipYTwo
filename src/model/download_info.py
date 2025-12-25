"""
DownloadInfo model to store download status information
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DownloadStatus(Enum):
    """Enumeration for download status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class DownloadInfo:
    """Model class to store download progress information"""
    status: DownloadStatus
    progress: float = 0.0  # Percentage from 0 to 100
    message: str = ""
    error: Optional[str] = None
    
    def __post_init__(self):
        if not self.message:
            if self.status == DownloadStatus.PENDING:
                self.message = "Esperando descarga..."
            elif self.status == DownloadStatus.IN_PROGRESS:
                self.message = "Descarga en progreso..."
            elif self.status == DownloadStatus.COMPLETED:
                self.message = "Descarga finalizada"
            elif self.status == DownloadStatus.ERROR:
                self.message = "Ha ocurrido un error desconocido"

