"""
Design patterns package
"""
from .observer import Observer, Observable
from .strategy import DownloadStrategy
from .factory import StrategyFactory
from .template_method import AbstractDownloadStrategy
from .adapter import DownloadAdapter
from .command import DownloadCommand
from .facade import DownloadFacade

__all__ = [
    'Observer',
    'Observable',
    'DownloadStrategy',
    'StrategyFactory',
    'AbstractDownloadStrategy',
    'DownloadAdapter',
    'DownloadCommand',
    'DownloadFacade'
]

