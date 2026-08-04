# -------------------------------------
#  Concrete Extension of
#  BaseGitHubClient Abstract Class
# -------------------------------------

from github import Github, GithubException

from .base import BaseGitHubClient
from .types import GitHubClientResult, GitHubOpStatus


class PyGithubManager(BaseGitHubClient):
    def __init__(self, token, repo_name):
        self.token = token
        self.repo_name = repo_name

        # instantiate the Github with token
        self.github = Github(self.token)

        # get the reposistory with rull repo name (owner/repo)
        try:
            self.repo = self.github.get_repo(self.repo_name)
        except GithubException as e:
            # handle specific HTTP error status codes
            if e.status == 404:
                return GitHubClientResult(
                    status=GitHubOpStatus.REPO_NOT_FOUND,
                    raw_data=e,
                    error_details=f"Error: Repository {self.repo_name} not found.",
                )

            elif e.status == 401:
                return GitHubClientResult(
                    status=GitHubOpStatus.BAD_CREDENTIALS,
                    raw_data=e,
                    error_details=f"Error: Bad credentials or invalid token {self.token}.",
                )

            else:
                return GitHubClientResult(
                    status=GitHubOpStatus.API_ERROR,
                    raw_data=e,
                    error_details=f"GitHub API Error [{e.status}: {e.message}]",
                )

        return GitHubClientResult(
            status=GitHubOpStatus.INIT_GITHUB_CLIENT,
            raw_data=f"Initilized a GitHub Client with creds {self.token} on repo {self.repo_name}",
        )

    def get_issue(self, issue_number: int) -> GitHubClientResult:
        """Fetches issue title, description, and comments."""

        try:
            issue = self.repo.get_issue(number=issue_number)

            comments = []
            for comment in issue.get_comments():
                comments.append(comment)

        except GithubException as e:
            # handle specific HTTP error status codes
            if e.status == 404:
                return GitHubClientResult(
                    status=GitHubOpStatus.ISSUE_NOT_FOUND,
                    raw_data=e,
                    error_details=f"Error: Issue {issue_number} not found.",
                )
            else:
                return GitHubClientResult(
                    status=GitHubOpStatus.API_ERROR,
                    raw_data=e,
                    error_details=f"GitHub API Error [{e.status}: {e.message}]",
                )

        except Exception as e:
            # Handle general connection/network errors
            return GitHubClientResult(
                status=GitHubOpStatus.GENERAL_EXCEPTION,
                raw_data=e,
                error_details=f"An unexpected error occurred: {e}",
            )

        return GitHubClientResult(
            status=GitHubOpStatus.RETRIEVED_ISSUE,
            issue_dict={
                "Issue Number": issue_number,
                "Issue Title": issue.title,
                "Issue Description": issue.body,
                "State": issue.state,
            },
            comments=comments,
            raw_data=issue,
        )

    def create_pull_request(
        self, title: str, body: str, head_branch: str, base_branch: str = "main"
    ) -> GitHubClientResult:
        """Opens a Pull Request and returns the PR URL."""

        try:
            pr = self.repo.create_pull(
                title=title, body=body, head=head_branch, base=base_branch
            )

        except GithubException as e:
            if e.status == 422:
                return GitHubClientResult(
                    status=GitHubOpStatus.UNPROCESSABLE,
                    raw_data=e,
                    error_details=e.data["errors"],
                )

            elif e.status == 404:
                return GitHubClientResult(
                    status=GitHubOpStatus.REPO_OR_BRANCH_NOT_FOUND,
                    raw_data=e,
                    error_details=e.data["errors"],
                )

            else:
                return GitHubClientResult(
                    status=GitHubOpStatus.GENERAL_EXCEPTION,
                    raw_data=e,
                    error_details=e.data["errors"],
                )

        return GitHubClientResult(status=GitHubOpStatus.PR_MADE, raw_data=pr)

    def get_default_branch(self) -> GitHubClientResult:
        """Prevents PR creation tools from failing on repos using non-standard target branches."""

        try:
            default_branch = self.repo.default_branch

        except GithubException as e:
            return GitHubClientResult(
                status=GitHubOpStatus.API_ERROR,
                raw_data=e,
                error_details=e.data["errors"],
            )

        except Exception as e:
            return GitHubClientResult(
                status=GitHubOpStatus.GENERAL_EXCEPTION,
                raw_data=e,
                error_details=f"An unexpected error occurred: {str(e)}",
            )

        return GitHubClientResult(
            status=GitHubOpStatus.RETRIEVED_DEFAULT, default_branch=default_branch
        )

    def post_issue_comment(self, issue_number: int, comment: str) -> GitHubClientResult:
        """Updates issue progress."""

        try:
            issue = self.repo.get_issue(number=issue_number)

            # create the comment
            comment = issue.create_comment(comment)

        except GithubException as e:
            return GitHubClientResult(
                status=GitHubOpStatus.API_ERROR,
                raw_data=e,
                error_details=e.data["errors"],
            )

        except Exception as e:
            return GitHubClientResult(
                status=GitHubOpStatus.GENERAL_EXCEPTION,
                raw_data=e,
                error_details=f"An unexpected error occurred: {str(e)}",
            )

        return GitHubClientResult(
            status=GitHubOpStatus.COMMENT_MADE,
        )
