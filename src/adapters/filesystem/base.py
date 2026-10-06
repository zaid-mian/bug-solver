# ------------------------------------
#  This is the Abstract Interface for
#   Local filesystem operations
# ------------------------------------

import os
from abc import ABC, abstractmethod
from pathlib import Path

from .types import FileSystemResult


class BaseFileSystemTools(ABC):
    @abstractmethod
    def read_files(
        self, file_paths: list[str | os.PathLike | Path]
    ) -> FileSystemResult:
        """Reads file from local filesystem"""
        pass

    @abstractmethod
    def write_files(
        self,
        file_paths_and_edits: dict[str | os.PathLike | Path, str],
    ) -> FileSystemResult:
        """Writes file to local filesystem"""
        pass

    @abstractmethod
    def find_files(self, text_pattern: str) -> FileSystemResult:
        """Finds files by glop text patterns"""
        pass

    @abstractmethod
    def list_dir(
        self, dir: str | os.PathLike | Path = None, recursive_search: bool = True
    ) -> FileSystemResult:
        """Gives a list of the directory/repoistory files/structure."""
        pass

    def patch_file(
        self, file_path: str | os.PathLike | Path, old_str: str, new_str: str
    ) -> FileSystemResult:
        """Applies a targeted search-and-replace edit to a file."""
        from .types import FileOpStatus

        read_res = self.read_files([file_path])
        if not read_res.read_file_contents:
            return FileSystemResult(
                status=FileOpStatus.PATCH_FAILED,
                error_details=f"Could not read file {file_path}",
            )

        path_obj = next(iter(read_res.read_file_contents.keys()))
        content = read_res.read_file_contents[path_obj]
        if old_str not in content:
            return FileSystemResult(
                status=FileOpStatus.PATCH_FAILED,
                error_details=f"Target snippet not found in {file_path}",
            )

        new_content = content.replace(old_str, new_str, 1)
        write_res = self.write_files({file_path: new_content})
        if write_res.written_files:
            return FileSystemResult(
                status=FileOpStatus.PATCH_APPLIED,
                written_files=[path_obj],
                raw_data=f"Replaced target snippet in {file_path}",
            )
        return FileSystemResult(
            status=FileOpStatus.PATCH_FAILED,
            error_details=write_res.error_details or "Failed to write patched file",
        )

