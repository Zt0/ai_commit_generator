from adapters.adapter import LanguageModelAdapter
import cohere

class CohereAdapter(LanguageModelAdapter):
    
    def __init__(self, api_key: str):
        print('api_key', api_key)
        self.client = cohere.Client(api_key)
        self.response = ""
    
    def send_message(self, prompt: str) -> str:
        response = self.client.generate(
            model="command-r-plus",
            prompt=prompt,
            max_tokens=100
        )
        return response.generations[0].text.strip()
