import os
import git
from commit_message_generator import CommitMessageGenerator
from language_model_factory import LanguageModelFactory
from dotenv import load_dotenv
import subprocess

load_dotenv()

repo = git.Repo(search_parent_directories=True)
diff = repo.git.diff('--staged')

def get_diff():
    # Get the diff of the current changes
    diff = subprocess.check_output(['git', 'diff', '--cached'], text=True)
    return diff

def generate_commit_message(diff):
    adapter = LanguageModelFactory.create_adapter('cohere', os.getenv('LANGUAGE_MODEL_API_KEY'))
    generator = CommitMessageGenerator(adapter)


    prompt = f"""
    provide git commit message based on conventinal commit, based on the changes ${diff}, return just the commit message
    ${diff}
    """
    commit_message = generator.generate_commit_message(prompt)
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
