from pathlib import Path

import pytest

from adapters.filesystem.PATHLIBPythonManager import PATHLIBPythonManager
from adapters.filesystem.types import FileOpStatus
from tools.workspace_tools import workspace_tools


@pytest.fixture
def temp_workspace(tmp_path: Path):
    sample = tmp_path / "sample.py"
    sample.write_text("def hello():\n    return 'old_value'\n", encoding="utf-8")
    return tmp_path


def test_patch_file_success(temp_workspace: Path):
    manager = PATHLIBPythonManager(root=temp_workspace)
    res = manager.patch_file(
        file_path=temp_workspace / "sample.py",
        old_str="return 'old_value'",
        new_str="return 'new_value'",
    )
    assert res.status == FileOpStatus.PATCH_APPLIED
    updated_content = (temp_workspace / "sample.py").read_text(encoding="utf-8")
    assert "return 'new_value'" in updated_content
    assert "return 'old_value'" not in updated_content


def test_patch_file_target_not_found(temp_workspace: Path):
    manager = PATHLIBPythonManager(root=temp_workspace)
    res = manager.patch_file(
        file_path=temp_workspace / "sample.py",
        old_str="non_existent_code_block",
        new_str="replacement",
    )
    assert res.status == FileOpStatus.PATCH_FAILED
    assert "Target snippet not found" in res.error_details


def test_patch_file_nonexistent_file(temp_workspace: Path):
    manager = PATHLIBPythonManager(root=temp_workspace)
    res = manager.patch_file(
        file_path=temp_workspace / "ghost.py",
        old_str="anything",
        new_str="anything",
    )
    assert res.status == FileOpStatus.PATCH_FAILED


def test_workspace_patch_tool_invocation(temp_workspace: Path):
    manager = PATHLIBPythonManager(root=temp_workspace)
    tools = workspace_tools(manager)
    patch_tool = next(t for t in tools if t.name == "patch_file")

    result = patch_tool.invoke({
        "file_path": str(temp_workspace / "sample.py"),
        "old_str": "return 'old_value'",
        "new_str": "return 'patched_via_tool'",
    })
    assert "Successfully patched" in result
    content = (temp_workspace / "sample.py").read_text(encoding="utf-8")
    assert "patched_via_tool" in content
