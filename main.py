import os
import re
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

def clean_diff(diff: str) -> str:
    """Remove binary files and large diffs to stay within token limits."""
    # Remove binary file changes
    diff = re.sub(r'diff --git.*\nBinary files.*\n', '', diff)
  
    # Keep only the first 100 lines of large diffs to avoid token limits
    lines = diff.split('\n')
    if len(lines) > 100:
        return '\n'.join(lines[:100]) + "\n... (truncated)"
    return diff

def generate_commit_message(
    diff: str, 
    branch_name: Optional[str] = None,
    ticket_number: Optional[str] = None
) -> str:
    adapter = LanguageModelFactory.create_adapter('cohere', os.getenv('LANGUAGE_MODEL_API_KEY'))
    generator = CommitMessageGenerator(adapter)

    cleaned_diff = clean_diff(diff)
    context = f"""Generate a concise and descriptive commit message for the following git diff.
        Follow these rules:
        1. Use conventional commits format (type(scope): description)
        2. Keep the first line under 72 characters
        3. Add detailed description if needed
        4. Mention ticket number {ticket_number} if provided
        5. Focus on WHAT changed and WHY, not HOW
        6. Identify breaking changes and mark with BREAKING CHANGE:
        7. Consider the branch name: {branch_name} for context

        Here's the diff:
        {cleaned_diff}
        """

    commit_message = generator.generate_commit_message(context)
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
