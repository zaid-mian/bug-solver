# ------------------------------------
#  This is the Abrstact Interface for
#   Local Git operations
# ------------------------------------

from abc import ABC, abstractmethod

class BaseGitRepo(ABC):
    @abstractmethod
    def checkout_branch(self, branch_name: str, create_new: bool = True) -> str:
        """ Switches or creates a new branch."""
        pass

    @abstractmethod
    def apply_patch_or_commit(self, messages: str, files: list[str] = None) -> str:
        """Stages changes and creates a commit."""
        pass

    @abstractmethod
    def push(self, branch_name: str, remote: str = "origin") -> str:
        """Pushes current branch to remote."""
        pass

    @abstractmethod
    def search_repo_text(self, text_pattern: str) -> str:
        """Performs semantic keyword, symbol, or error string searches"""
        pass
