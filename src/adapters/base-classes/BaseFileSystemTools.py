# ------------------------------------
#  This is the Abrstact Interface for
#   Local filesystem operations
# ------------------------------------

from abc import ABC, abstractmethod
import os
from pathlib import Path

class BaseFileSystemTools(ABC):
    @abstractmethod
    def read_file(self, file_path: str | os.PathLike | Path) -> str:
        """Reads file from local filesystem"""
        pass

    @abstractmethod
    def write_files(self, file_path: str | os.PathLike | Path, content_edit: str):
        """Writes file to local filesystem"""
        pass

    @abstractmethod
    def find_files(self, text_pattern: str) -> list[Path]:
        """Finds files by glop text patterns"""
        pass

    @abstractmethod
    def list_dir(self, root: str | os.PathLike | Path) -> list[Path]:
        """Gives a list of the directory/repoistory files/structure."""
        pass
