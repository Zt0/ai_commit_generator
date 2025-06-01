import click
import os
import subprocess
import sys
from pathlib import Path
from .main import main as main_function

@click.group()
@click.version_option()
def cli():
    """AI-powered Git commit message generator."""
    pass

@cli.command()
@click.argument('commit_msg_file')
def generate(commit_msg_file: str):
    """Generate commit message (used by pre-commit hook)."""
    # This calls your existing main.py logic
    sys.argv = ['ai-commit-generator', commit_msg_file]
    try:
        main_function()
        click.echo("✓ Commit message generated successfully!")
    except SystemExit as e:
        if e.code != 0:
            click.echo("Error generating commit message", err=True)
            sys.exit(e.code)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def install():
    """Install pre-commit hook in current repository."""
    if not Path('.git').exists():
        click.echo("Error: Not in a git repository", err=True)
        sys.exit(1)

    # Create .pre-commit-config.yaml
    config_content = """repos:
-   repo: local
    hooks:
    -   id: ai-commit-generator
        name: Generate AI Commit Message
        entry: ai-commit-generator generate
        language: system
        stages: [prepare-commit-msg]
        pass_filenames: false
        always_run: true
"""

    config_path = Path('.pre-commit-config.yaml')
    if config_path.exists():
        if not click.confirm(".pre-commit-config.yaml exists. Overwrite?"):
            click.echo("Installation cancelled.")
            return

    with open(config_path, 'w') as f:
        f.write(config_content)
    click.echo("✓ Created .pre-commit-config.yaml")

    # Create .env if it doesn't exist
    env_path = Path('.env')
    if not env_path.exists():
        env_content = """# AI Commit Generator Configuration
LANGUAGE_MODEL_API_KEY=your_api_key_here
LANGUAGE_MODEL_PROVIDER=cohere
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        click.echo("✓ Created .env file")

    # Install pre-commit hooks
    try:
        subprocess.run(['pre-commit', 'install', '--hook-type', 'prepare-commit-msg'], 
                      check=True, capture_output=True)
        click.echo("✓ Installed pre-commit hooks")
    except FileNotFoundError:
        click.echo("⚠ pre-commit not found. Install with: pip install pre-commit")
        click.echo("Then run: pre-commit install --hook-type prepare-commit-msg")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error installing pre-commit hooks: {e}", err=True)

    click.echo("\n🎉 Setup complete!")
    click.echo("Don't forget to:")
    click.echo("1. Add your API key to .env")
    click.echo("2. Install pre-commit if needed: pip install pre-commit")
    click.echo("3. Test with: git add . && git commit")

@cli.command()
def config():
    """Show configuration and supported providers."""
    click.echo("AI Commit Generator Configuration")
    click.echo("================================")

    env_file = Path('.env')
    if env_file.exists():
        click.echo("✓ .env file found")
        api_key = os.getenv('LANGUAGE_MODEL_API_KEY')
        provider = os.getenv('LANGUAGE_MODEL_PROVIDER', 'cohere')

        if api_key:
            click.echo(f"✓ API key configured (***{api_key[-4:]})")
        else:
            click.echo("⚠ API key not set")

        click.echo(f"Provider: {provider}")
    else:
        click.echo("⚠ .env file not found")

    click.echo("\nSupported providers:")
    click.echo("- cohere (default)")
    click.echo("- openai") 
    click.echo("- anthropic")

@cli.command()
def test():
    """Test the commit message generator with current staged changes."""
    try:
        from .main import get_diff, get_branch_name, get_gitignore_content, extract_ticket_number, generate_commit_message

        diff = get_diff()
        branch_name = get_branch_name()
        ticket_number = extract_ticket_number(branch_name)
        gitignore_content = get_gitignore_content()

        click.echo("Generating commit message for current staged changes...")
        commit_message = generate_commit_message(diff, branch_name, ticket_number, gitignore_content)

        click.echo("\n" + "="*50)
        click.echo("Generated Commit Message:")
        click.echo("="*50)
        click.echo(commit_message)
        click.echo("="*50)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

def main():
    cli()

if __name__ == '__main__':
    main()
