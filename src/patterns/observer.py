"""
Observer pattern implementation
"""
from abc import ABC, abstractmethod
from typing import List


class Observer(ABC):
    """Observer interface for receiving updates"""
    
    @abstractmethod
    def update(self, message: str, progress: float = None, status: str = None):
        """Called when the observed object changes state"""
        pass


class Observable:
    """Observable class that notifies observers of state changes"""
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer):
        """Attach an observer to receive updates"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer):
        """Detach an observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, message: str, progress: float = None, status: str = None):
        """Notify all observers of a state change"""
        for observer in self._observers:
            observer.update(message, progress, status)

