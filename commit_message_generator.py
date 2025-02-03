from adapters.adapter import LanguageModelAdapter


class CommitMessageGenerator:
    
    def __init__(self, adapter: LanguageModelAdapter):
        self.adapter = adapter
    
    def generate_commit_message(self, prompt: str) -> str:
        """Generate a commit message based on the prompt"""
        return self.adapter.send_message(prompt)
