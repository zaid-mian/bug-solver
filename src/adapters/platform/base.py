# ------------------------------------
#  This is the Abrstact Interface for
#   Web Platform GitHub operations
# ------------------------------------

from abc import ABC, abstractmethod

from .types import GitHubClientResult, GitHubOpStatus


class BaseGitHubClient(ABC):
    @abstractmethod
    def get_issue(self, issue_number: int) -> GitHubClientResult:
        """Fetches issue title, description, and comments."""
        pass

    @abstractmethod
    def create_pull_request(
        self, title: str, body: str, head_branch: str, base_branch: str = "main"
    ) -> GitHubClientResult:
        """Opens a Pull Request and returns the PR URL."""
        pass

    @abstractmethod
    def get_default_branch(self) -> GitHubClientResult:
        """Prevents PR creation tools from failing on repos using non-standard target branches."""
        pass

    @abstractmethod
    def post_issue_comment(self, issue_number: int, comment: str) -> GitHubClientResult:
        """Updates issue progress."""
        pass
