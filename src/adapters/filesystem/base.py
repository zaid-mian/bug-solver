# ------------------------------------
#  This is the Abstract Interface for
#   Local filesystem operations
# ------------------------------------

from abc import ABC, abstractmethod
import os
from pathlib import Path
from typing import Dict

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
        file_paths_and_edits: Dict[str | os.PathLike | Path, str],
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
