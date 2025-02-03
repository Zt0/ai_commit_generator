from abc import ABC, abstractmethod

class LanguageModelAdapter(ABC):
    
    @abstractmethod
    def send_message(self, prompt: str) -> str:
        """Send a message to the language model and get a response"""
        pass

