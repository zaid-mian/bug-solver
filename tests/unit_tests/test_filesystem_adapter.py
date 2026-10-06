from pathlib import Path

from adapters.filesystem.PATHLIBPythonManager import PATHLIBPythonManager
from adapters.filesystem.types import FileOpStatus


def test_filesystem_adapter_crud(tmp_path: Path):
    manager = PATHLIBPythonManager(root=tmp_path)

    # 1. Write file
    write_res = manager.write_files({"src/sub/hello.txt": "Hello World\nLine 2"})
    assert write_res.status == FileOpStatus.SUCCESSFULLY_WROTE_SOME_FILES
    assert len(write_res.written_files) == 1
    assert (tmp_path / "src" / "sub" / "hello.txt").exists()

    # 2. Read file
    read_res = manager.read_files(["src/sub/hello.txt"])
    assert read_res.status == FileOpStatus.SUCCESSFULLY_READ_SOME_FILES
    assert "Hello World" in list(read_res.read_file_contents.values())[0]

    # 3. List dir recursive
    list_res = manager.list_dir(recursive_search=True)
    assert list_res.status == FileOpStatus.SEARCHED_RECURSIVELY_SUCCESS
    assert list_res.files is not None
    assert len(list_res.files) >= 1
    assert "hello.txt" in list_res.visual_repo_structure

    # 4. Find files
    find_glob = manager.find_files("*.txt")
    assert find_glob.status == FileOpStatus.FOUND_MATCHES
    assert len(find_glob.matched_files) == 1

    find_content = manager.find_files("Line 2")
    assert find_content.status == FileOpStatus.FOUND_MATCHES
    assert len(find_content.matched_files) == 1

    find_miss = manager.find_files("NonExistentString12345")
    assert find_miss.status == FileOpStatus.NO_MATCHES
