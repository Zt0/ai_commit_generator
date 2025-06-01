from typing import Dict, List, TypedDict, Set

class FileChangeSummary(TypedDict):
    additions: int
    deletions: int
    file_type: str
    important_changes: List[str]


class ChangeSummary(TypedDict):
    total_files: int
    total_additions: int
    total_deletions: int
    file_types: Set[str]
    important_files: List[str]
    key_changes: Dict[str, List[str]]
