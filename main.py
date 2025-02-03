import os
import git
from commit_message_generator import CommitMessageGenerator
from language_model_factory import LanguageModelFactory
from dotenv import load_dotenv

load_dotenv()

repo = git.Repo(search_parent_directories=True)
diff = repo.git.diff('--staged')


adapter = LanguageModelFactory.create_adapter('cohere', os.getenv('LANGUAGE_MODEL_API_KEY'))
generator = CommitMessageGenerator(adapter)


prompt = f"""
provide git commit message based on conventinal commit, based on the changes ${diff}, return just the message
${diff}
"""
commit_message = generator.generate_commit_message(prompt)
print(commit_message)
