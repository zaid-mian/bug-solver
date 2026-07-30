# -------------------------------------
#  Concrete Extension of
#  BaseFileSystemTools Abstract Class
# -------------------------------------

import os
from pathlib import Path
from typing import Dict

from .base import BaseFileSystemTools
from .types import FileSystemResult, FileOpStatus


class OSPythonManager(BaseFileSystemTools):
    def read_files(
        self, file_paths: list[str | os.PathLike | Path]
    ) -> FileSystemResult:
        """Reads file from local filesystem"""
        pass

    def write_files(
        self, file_paths_and_edits: Dict[str | os.PathLike | Path, str]
    ) -> FileSystemResult:
        """Writes file to local filesystem"""
        pass

    def find_files(self, text_pattern: str) -> FileSystemResult:
        """Finds files by glop text patterns"""
        pass

    def list_dir(
        self, dir: str | os.PathLike | Path = None, recursive_search: bool = True
    ) -> FileSystemResult:
        """Gives a list of the directory/repoistory files/structure."""
        pass
