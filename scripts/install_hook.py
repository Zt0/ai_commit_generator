#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

def install_pre_commit_hook():
    """Install the pre-commit hook configuration."""
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("Error: Not in a git repository")
        sys.exit(1)
    
    # Create .pre-commit-config.yaml
    config_content = """repos:
-   repo: local
    hooks:
    -   id: ai-commit-generator
        name: Generate AI Commit Message
        entry: ai-commit-generator
        language: system
        stages: [prepare-commit-msg]
        pass_filenames: false
        always_run: true
"""
    
    config_path = Path('.pre-commit-config.yaml')
    
    if config_path.exists():
        response = input(".pre-commit-config.yaml already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Installation cancelled.")
            return
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print("✓ Created .pre-commit-config.yaml")
    
    # Install pre-commit hooks
    try:
        subprocess.run(['pre-commit', 'install', '--hook-type', 'prepare-commit-msg'], 
                      check=True, capture_output=True)
        print("✓ Installed pre-commit hooks")
    except subprocess.CalledProcessError:
        print("Error: Failed to install pre-commit hooks")
        print("Make sure pre-commit is installed: pip install pre-commit")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: pre-commit not found")
        print("Install it with: pip install pre-commit")
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    env_path = Path('.env')
    if not env_path.exists():
        env_content = """# AI Commit Generator Configuration
LANGUAGE_MODEL_API_KEY=your_api_key_here
# Uncomment and modify if needed:
# LANGUAGE_MODEL_PROVIDER=cohere
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✓ Created .env file - please add your API key")
    
    print("\nSetup complete! Don't forget to:")
    print("1. Add your API key to the .env file")
    print("2. Run 'git add .' and 'git commit' to test")

if __name__ == "__main__":
    install_pre_commit_hook()
