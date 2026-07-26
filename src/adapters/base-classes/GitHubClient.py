# ------------------------------------
#  This is the Abrstact Interface for
#   Web Platform GitHub operations
# ------------------------------------

from abc import ABC, abstractmethod

class BaseGitHubClient(ABC):
    @abstractmethod
    def get_issue(self, issue_number: int) -> dict:
        """Fetches issue title, description, and comments."""
        pass

    @abstractmethod
    def create_pull_request(
            self, title: str, body: str, head_branch: str, base_branch: str = "main"
    ) -> str:
        """Opens a Pull Request and returns the PR URL."""
        pass

    @abstractmethod
    def post_issue_comment(self, issue_number: int, comment: str) -> None:
        """Updates issue progress."""
        pass
