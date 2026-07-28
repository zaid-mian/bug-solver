# ------------------------------------
#  This is the Abrstact Interface for
#   Local Git operations
# ------------------------------------

from abc import ABC, abstractmethod
from .types import GitResult


class BaseGitRepo(ABC):
    @abstractmethod
    def checkout_branch(self, branch_name: str, create_new: bool = True) -> GitResult:
        """Switches or creates a new branch."""
        pass

    @abstractmethod
    def apply_patch_or_commit(
        self, messages: str, files: list[str] = None
    ) -> GitResult:
        """Stages changes and creates a commit."""
        pass

    @abstractmethod
    def push(self, branch_name: str, remote: str = "origin") -> GitResult:
        """Pushes current branch to remote."""
        pass

    @abstractmethod
    def pull(self, branch_name: str, remote: str = "origin") -> GitResult:
        """Pulls remote branch to current branch."""
        pass

    @abstractmethod
    def search_repo_text(self, text_pattern: str) -> GitResult:
        """Performs semantic keyword, symbol, or error string searches"""
        pass

    @abstractmethod
    def git_status(self) -> GitResult:
        """Performs git status command to check staging and possible merging conflicts."""
        pass

    @abstractmethod
    def run_git_command(
        self, args_str: str, timeout_seconds: float = 30.0
    ) -> GitResult:
        """This is a Fallback or Escape Hatch Tool in case the standard tools are not sufficient for complex Git conflicts or issues."""
        pass
