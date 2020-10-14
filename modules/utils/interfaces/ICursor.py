from abc import ABC, abstractmethod

class ICursor(ABC):
    
    @abstractmethod
    def getCursor(self):
        pass

    @abstractmethod
    def getScale(self):
        pass

    @abstractmethod
    def getImagePath(self):
        pass