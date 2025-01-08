# observer.py
from __future__ import annotations
from abc import ABC, abstractmethod

class Observer(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the observer."""
        pass

    @abstractmethod
    def update(self, notification: str):
        """Receive a notification."""
        pass

class Subject(ABC):
    @abstractmethod
    def attach(self, observer: Observer):
        """Attach an observer."""
        pass

    @abstractmethod
    def detach(self, observer: Observer):
        """Detach an observer."""
        pass

    @abstractmethod
    def notifyObservers(self, notification: str):
        """Notify all attached observers."""
        pass

class Iterator(ABC):
    @abstractmethod
    def hasNext(self) -> bool:
        """Check if there are more items."""
        pass

    @abstractmethod
    def next(self) -> Book:
        """Return the next item."""
        pass
