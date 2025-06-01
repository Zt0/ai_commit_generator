import os
import sys
import subprocess
from typing import Optional
from commit_message_generator import CommitMessageGenerator
from language_model_factory import LanguageModelFactory
from dotenv import load_dotenv

load_dotenv()

def get_diff() -> str:
    """Get the staged diff for commit message generation."""
    try:
        diff = subprocess.check_output(['git', 'diff', '--cached'], text=True).strip()
        if not diff:
            print("Error: No staged changes detected. Please stage files before committing.", file=sys.stderr)
            sys.exit(1)
        return diff
    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Git is not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)


def get_branch_name() -> Optional[str]:
    """Get the current branch name."""
    try:
        branch = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()
        return branch if branch else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_gitignore_content() -> Optional[str]:
    """Get the content of .gitignore file if it exists."""
    try:
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r', encoding='utf-8') as f:
                return f.read()
    except (IOError, UnicodeDecodeError):
        pass
    return None


def extract_ticket_number(branch_name: Optional[str]) -> Optional[str]:
    """Extract ticket number from branch name if it follows common patterns."""
    if not branch_name:
        return None
    
    # Common patterns: feature/TICKET-123, TICKET-123-description, etc.
    import re
    patterns = [
        r'([A-Z]+-\d+)',  # JIRA-style: ABC-123
        r'#(\d+)',        # GitHub-style: #123
        r'(\d+)',         # Simple number: 123
    ]
    
    for pattern in patterns:
        match = re.search(pattern, branch_name)
        if match:
            return match.group(1)
    
    return None


def generate_commit_message(diff: str, branch_name: Optional[str] = None, ticket_number: Optional[str] = None, gitignore_content: Optional[str] = None) -> str:
    """Generate a commit message using an AI model."""
    api_key = os.getenv('LANGUAGE_MODEL_API_KEY')
    if not api_key:
        print("Error: LANGUAGE_MODEL_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    
    try:
        adapter = LanguageModelFactory.create_adapter('cohere', api_key)
        generator = CommitMessageGenerator(adapter)
        return generator.generate_commit_message(diff, branch_name, ticket_number, gitignore_content)
    except Exception as e:
        print(f"Error creating language model adapter: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to generate and write the commit message."""
    if len(sys.argv) < 2:
        print("Error: Commit message file path is missing.", file=sys.stderr)
        sys.exit(1)

    commit_msg_filepath = sys.argv[1]
    print(f"Writing commit message to {commit_msg_filepath}")
    
    try:
        # Get all necessary information
        diff = get_diff()
        branch_name = get_branch_name()
        ticket_number = extract_ticket_number(branch_name)
        gitignore_content = get_gitignore_content()
        
        # Generate commit message
        commit_message = generate_commit_message(diff, branch_name, ticket_number, gitignore_content)

        # Write the commit message to the file
        with open(commit_msg_filepath, 'w', encoding='utf-8') as f:
            f.write(commit_message)
            
        print("Commit message generated successfully!")

    except Exception as e:
        error_msg = f"Error generating commit message: {str(e)}"
        
        # Log error to file if possible
        try:
            os.makedirs(".git/hooks", exist_ok=True)
            with open(".git/hooks/error.log", "a", encoding='utf-8') as log_file:
                log_file.write(error_msg + "\n")
        except Exception:
            pass  # If we can't log, don't fail completely
            
        print(error_msg, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
