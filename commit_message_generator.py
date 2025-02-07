import re
from typing import Dict, List, Optional
from adapters.adapter import LanguageModelAdapter
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

class CommitMessageGenerator:
    
    def __init__(self, adapter: LanguageModelAdapter):
        self.adapter = adapter

    def _format_key_changes(self, key_changes: Dict[str, List[str]]) -> str:
        """Format key changes for the prompt."""
        result = []
        for filename, changes in key_changes.items():
            if changes:
                result.append(f"\n{filename}:")
                result.extend(f"  - {change}" for change in changes[:5])  # Limit to 5 changes per file
        return '\n'.join(result)

    def summarize_diff(self, diff: str) -> Dict:
        """Create a summary of changes by file and type."""
        files_changed = {}
        current_file = None
        
        for line in diff.split('\n'):
            if line.startswith('diff --git'):
                current_file = line.split()[-1].lstrip('b/')
                files_changed[current_file] = {
                    'additions': 0,
                    'deletions': 0,
                    'file_type': current_file.split('.')[-1] if '.' in current_file else 'unknown',
                    'important_changes': []
                }
            elif current_file and line.startswith('+') and not line.startswith('+++'):
                files_changed[current_file]['additions'] += 1
                # Store important changes like function definitions, class declarations, etc.
                if re.match(r'^\+\s*(def|class|import|from|const|let|var|function|interface|type)', line):
                    files_changed[current_file]['important_changes'].append(line.lstrip('+'))
            elif current_file and line.startswith('-') and not line.startswith('---'):
                files_changed[current_file]['deletions'] += 1

        return files_changed

    def get_gitignore_spec(self, gitignore_content: str) -> PathSpec:
        """Create a PathSpec from gitignore patterns."""
        return PathSpec.from_lines(GitWildMatchPattern, gitignore_content.splitlines())

    def is_important_file(self, filename: str, gitignore_spec: Optional[PathSpec] = None) -> bool:
        """Determine if a file is important based on type and gitignore."""
        if gitignore_spec and gitignore_spec.match_file(filename):
            return False
            
        # Files to ignore
        ignore_patterns = [
            r'\.lock$', r'\.log$', r'\.map$', r'\.min\.',
            r'package-lock\.json$', r'yarn\.lock$',
            r'\.git/', r'node_modules/', r'vendor/',
        ]
        
        if any(re.search(pattern, filename) for pattern in ignore_patterns):
            return False
            
        return True

    def clean_diff(self, diff: str) -> str:
        """Remove binary files and large diffs to stay within token limits."""
        # Remove binary file changes
        diff = re.sub(r'diff --git.*\nBinary files.*\n', '', diff)
    
        # Keep only the first 100 lines of large diffs to avoid token limits
        lines = diff.split('\n')
        if len(lines) > 100:
            return '\n'.join(lines[:100]) + "\n... (truncated)"
        return diff

    def generate_commit_message(self, diff: str, branch_name: str, ticket_number: str, gitignore_content: Optional[str] = None) -> str:
        cleaned_diff = self.clean_diff(diff)
        changes = self.summarize_diff(diff)
        # Create gitignore spec if provided
        gitignore_spec = None
        if gitignore_content:
            gitignore_spec = self.get_gitignore_spec(gitignore_content)
        
        # Filter important files
        important_changes = {
            filename: info 
            for filename, info in changes.items() 
            if self.is_important_file(filename, gitignore_spec)
        }
        
        # Prepare summary for AI
        summary = {
            'total_files': len(changes),
            'total_additions': sum(f['additions'] for f in changes.values()),
            'total_deletions': sum(f['deletions'] for f in changes.values()),
            'file_types': set(f['file_type'] for f in changes.values()),
            'important_files': list(important_changes.keys()),
            'key_changes': {
                filename: info['important_changes']
                for filename, info in important_changes.items()
                if info['important_changes']
            }
        }

        # context = f"""Generate a comprehensive commit message for a large change set.
        # Branch: {branch_name}
        # Ticket: {ticket_number}

        # Change Summary:
        # - Total Files Changed: {summary['total_files']}
        # - Additions: {summary['total_additions']}
        # - Deletions: {summary['total_deletions']}
        # - File Types: {', '.join(summary['file_types'])}

        # Key Changes:
        # {self._format_key_changes(summary['key_changes'])}

        # Rules:
        # 1. Use conventional commits format
        # 2. Start with the most significant change type
        # 3. Include scope if changes are focused
        # 4. Add detailed body explaining major changes
        # 5. List breaking changes if any
        # 6. Reference ticket number
        # 7. Do not include sensitive information
        # """
        context = f"""Analyze the following code changes and generate a Git commit message that follows the conventional commits specification. The changes include file modifications, additions, and deletions with the following context:
Branch: {branch_name}
Ticket: {ticket_number}
Summary of Changes:

Files Changed: {summary['total_files']}
Lines Added: {summary['total_additions']}
Lines Deleted: {summary['total_deletions']}
File Types Modified: {summary['file_types']}

Key Changes by File:
{summary['key_changes']}
Requirements:

1. Follow this exact format:
type(optional_scope): concise description

[body]

[footer]
2. Type must be one of:

feat: New feature or significant enhancement
fix: Bug fixes
refactor: Code changes that neither fix bugs nor add features
test: Adding or modifying tests
docs: Documentation changes
chore: Maintenance tasks
style: Code style/formatting changes
perf: Performance improvements


3. Description Guidelines:

Must be imperative mood ("add" not "added")
Maximum 50 characters
No period at the end
Should complete the sentence "If applied, this commit will..."


4. Body Guidelines:

Wrap at 72 characters
Explain the WHAT and WHY, not the HOW
Include context about the changes
Describe technical details for complex changes
List any breaking changes or deprecations


5. Footer Guidelines:

Reference the ticket number using "Refs: #{ticket_number}"
List any breaking changes with "BREAKING CHANGE:"
Mention related issues/PRs if applicable



Additional Rules:

Focus on the most significant changes first
Exclude any sensitive information, credentials, or internal identifiers
For large changes, group related modifications under a common theme
If changes span multiple concerns, focus on the primary purpose
Include migration notes if changes require updates to existing code"""
        return self.adapter.send_message(context)

