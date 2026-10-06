from adapters.platform.PyGithubManager import PyGithubManager
from adapters.platform.types import GitHubOpStatus


def test_pygithub_manager_init_handling():
    # Instantiation should never raise TypeError: __init__() should return None
    manager = PyGithubManager(token="dummy_token_123", repo_name="owner/nonexistent-repo-999")
    assert hasattr(manager, "status")
    # Because token is dummy/invalid, it should record an auth/api/not_found error, not crash
    assert manager.status in {
        GitHubOpStatus.BAD_CREDENTIALS,
        GitHubOpStatus.REPO_NOT_FOUND,
        GitHubOpStatus.API_ERROR,
        GitHubOpStatus.GENERAL_EXCEPTION,
        GitHubOpStatus.INIT_GITHUB_CLIENT,
    }

    # Calls when repo is not loaded should safely return error results
    res = manager.get_issue(1)
    assert res.status in {
        GitHubOpStatus.BAD_CREDENTIALS,
        GitHubOpStatus.REPO_NOT_FOUND,
        GitHubOpStatus.API_ERROR,
        GitHubOpStatus.GENERAL_EXCEPTION,
        GitHubOpStatus.ISSUE_NOT_FOUND,
    }
