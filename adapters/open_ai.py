import openai
from adapters.adapter import LanguageModelAdapter

class OpenAIAdapter(LanguageModelAdapter):
    
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.response = ""
    
    def send_message(self, prompt: str) -> str:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        content = response.choices[0].message.content
        return content.strip() if content is not None else ""
