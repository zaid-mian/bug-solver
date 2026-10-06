import subprocess
from pathlib import Path

from adapters.git.SubprocessGitManager import SubprocessGitManager
from adapters.git.types import GitOpStatus


def test_subprocess_git_manager(tmp_path: Path):
    # Initialize a temporary git repository
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True, capture_output=True)

    git_manager = SubprocessGitManager(repo_path=tmp_path)

    # Create and commit an initial file
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello world')", encoding="utf-8")

    commit_res = git_manager.apply_patch_or_commit(messages="Initial commit", files=["test.py"])
    assert commit_res.status == GitOpStatus.STAGED_AND_COMMITTED

    # Check status
    status_res = git_manager.git_status()
    assert status_res.status == GitOpStatus.GIT_STATUS

    # Check branches
    branches_res = git_manager.list_local_branches()
    assert branches_res.status == GitOpStatus.LISTED_BRANCHES

    # Checkout new branch
    checkout_res = git_manager.checkout_branch("feature/test-branch", create_new=True)
    assert checkout_res.status == GitOpStatus.BRANCH_CREATED

    # Search repo text
    search_res = git_manager.search_repo_text("hello")
    assert search_res.status == GitOpStatus.FOUND_MATCHES
