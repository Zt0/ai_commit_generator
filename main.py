import os
from typing import Optional

from commit_message_generator import CommitMessageGenerator
from language_model_factory import LanguageModelFactory
from dotenv import load_dotenv
import subprocess

load_dotenv()

def get_diff():
    # Get the diff of the current changes
    diff = subprocess.check_output(['git', 'diff', '--cached'], text=True)
    return diff

def generate_commit_message(
    diff: str, 
    branch_name: Optional[str] = None,
    ticket_number: Optional[str] = None
) -> str:
    adapter = LanguageModelFactory.create_adapter('cohere', os.getenv('LANGUAGE_MODEL_API_KEY'))
    generator = CommitMessageGenerator(adapter)
    commit_message = generator.generate_commit_message(diff, branch_name, ticket_number)
    print(commit_message)
    return commit_message

def set_commit_message(message):
    # Set the commit message
    subprocess.run(['git', 'commit', '-m', message])

def main():
    diff = get_diff()
    commit_message = generate_commit_message(diff)
    set_commit_message(commit_message)

if __name__ == "__main__":
    main()
