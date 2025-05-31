import os
import sys
import subprocess
from typing import Optional
from commit_message_generator import CommitMessageGenerator
from language_model_factory import LanguageModelFactory
from dotenv import load_dotenv

load_dotenv()

def get_diff():
    """Get the staged diff for commit message generation."""
    diff = subprocess.check_output(['git', 'diff', '--cached'], text=True).strip()
    if not diff:
        print("Error: No staged changes detected. Please stage files before committing.", file=sys.stderr)
        sys.exit(1)
    return diff

def generate_commit_message(diff: str, branch_name: Optional[str] = None, ticket_number: Optional[str] = None) -> str:
    """Generate a commit message using an AI model."""
    api_key = os.getenv('LANGUAGE_MODEL_API_KEY')
    if not api_key:
        print("Error: LANGUAGE_MODEL_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    adapter = LanguageModelFactory.create_adapter('cohere', api_key)
    generator = CommitMessageGenerator(adapter)
    return generator.generate_commit_message(diff, branch_name, ticket_number)

def main():
    """Main function to generate and write the commit message."""
    if len(sys.argv) < 2:
        print("Error: Commit message file path is missing.", file=sys.stderr)
        sys.exit(1)

    commit_msg_filepath = sys.argv[1]
    print(f"Writing commit message to {commit_msg_filepath}")
    try:
        diff = get_diff()
        commit_message = generate_commit_message(diff)

        # Write the commit message to the file
        with open(commit_msg_filepath, 'w') as f:
            f.write(commit_message)

    except Exception as e:
        error_msg = f"Error generating commit message: {str(e)}"
        with open(".git/hooks/error.log", "a") as log_file:
            log_file.write(error_msg + "\n")
        print(error_msg, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
