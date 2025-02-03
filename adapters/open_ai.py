import openai
from adapters.adapter import LanguageModelAdapter

class OpenAIAdapter(LanguageModelAdapter):
    
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.response = ""
    
    def send_message(self, prompt: str) -> str:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )
        return response.choices[0].text.strip()
