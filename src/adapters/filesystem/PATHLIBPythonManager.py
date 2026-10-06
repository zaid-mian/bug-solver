# -------------------------------------
#  Concrete Extension of
#  BaseFileSystemTools Abstract Class
# -------------------------------------

import os
from pathlib import Path

from .base import BaseFileSystemTools
from .types import FileOpStatus, FileSystemResult


class PATHLIBPythonManager(BaseFileSystemTools):
    def __init__(self, root: Path):
        self.root = Path(root).resolve()

    def _resolve(self, path: str | os.PathLike | Path) -> Path:
        p = Path(path)
        return p if p.is_absolute() else (self.root / p).resolve()

    def read_files(
        self, file_paths: list[str | os.PathLike | Path]
    ) -> FileSystemResult:
        """Reads file from local filesystem"""
        read_file_content = {}
        unreadable_files = {}

        for file in file_paths:
            resolved = self._resolve(file)
            try:
                content = resolved.read_text(encoding="utf-8")
                read_file_content[Path(file)] = content
            except FileNotFoundError:
                unreadable_files[Path(file)] = f"Error: The file at {file} does not exist."
            except IsADirectoryError:
                unreadable_files[Path(file)] = f"Error: {file} is a directory, not a file."
            except PermissionError:
                unreadable_files[Path(file)] = f"Error: Missing read permissions for {file}."
            except UnicodeDecodeError as e:
                unreadable_files[Path(file)] = f"Error: Failed to decode file using UTF-8. Details: {e}"
            except OSError as e:
                unreadable_files[Path(file)] = f"System Error: A broader operating system error occurred: {e}"

        return FileSystemResult(
            status=FileOpStatus.SUCCESSFULLY_READ_SOME_FILES,
            read_file_contents=read_file_content,
            unread_file_content=unreadable_files,
        )

    def write_files(
        self,
        file_paths_and_edits: dict[str | os.PathLike | Path, str],
    ) -> FileSystemResult:
        """Writes file to local filesystem"""
        written_files = []
        unwritten_files = {}

        for file, content in file_paths_and_edits.items():
            resolved = self._resolve(file)
            try:
                resolved.parent.mkdir(parents=True, exist_ok=True)
                resolved.write_text(content, encoding="utf-8")
                written_files.append(Path(file))
            except FileNotFoundError:
                unwritten_files[Path(file)] = f"Error: The directory structure for {file} does not exist."
            except PermissionError:
                unwritten_files[Path(file)] = f"Error: Do not have permission to write to {file}."
            except OSError as e:
                unwritten_files[Path(file)] = f"System error writing to {file}: {e}"

        return FileSystemResult(
            status=FileOpStatus.SUCCESSFULLY_WROTE_SOME_FILES,
            written_files=written_files,
            unwritten_files=unwritten_files,
        )

    def find_files(self, text_pattern: str) -> FileSystemResult:
        """Finds files matching a glob pattern or containing text."""
        matches = []
        unreadable = []

        recursive_result: FileSystemResult = self.list_dir(recursive_search=True)
        files = recursive_result.files or []

        for file in files:
            # Check pattern match against file name or path
            if file.match(text_pattern) or text_pattern in file.name:
                matches.append(file)
                continue

            # Also check content if text_pattern is inside file
            try:
                if text_pattern in file.read_text(encoding="utf-8"):
                    matches.append(file)
            except Exception:
                unreadable.append(file)

        if not matches:
            return FileSystemResult(
                status=FileOpStatus.NO_MATCHES,
                files=files,
                unreadable_files=unreadable,
                error_details=f"No matched files were found for pattern '{text_pattern}'.",
            )

        return FileSystemResult(
            status=FileOpStatus.FOUND_MATCHES,
            files=files,
            matched_files=matches,
            unreadable_files=unreadable,
            raw_data=f"Matches that were found: '{len(matches)}'.",
        )

    def list_dir(
        self, dir: str | os.PathLike | Path = None, recursive_search: bool = True
    ) -> FileSystemResult:
        """Gives a list of the directory/repository files/structure."""
        target_dir = self._resolve(dir) if dir else self.root

        if not target_dir.exists():
            return FileSystemResult(
                status=FileOpStatus.DIR_NON_EXISTENT,
                error_details=f"Error: the path of directory '{target_dir}' does not exist.",
            )

        if not target_dir.is_dir():
            return FileSystemResult(
                status=FileOpStatus.NOT_DIR,
                error_details=f"Error: the path of 'directory' given '{target_dir}' is not actually a directory.",
            )

        if not recursive_search:
            files = [item for item in target_dir.iterdir() if item.is_file()]
            dirs = [item for item in target_dir.iterdir() if item.is_dir()]
            raw_data = f"Retrieved {len(files)} files and {len(dirs)} subdirectories within {target_dir}."
            return FileSystemResult(
                status=FileOpStatus.SEARCHED_SHALLOW_SUCCESS,
                files=files,
                dirs=dirs,
                raw_data=raw_data,
            )

        visual_entries = []
        path_repo_structure = []
        files = []
        dirs = []
        for path in sorted(target_dir.rglob("*")):
            depth = len(path.relative_to(target_dir).parts) - 1
            indent = "  " * depth

            if path.is_dir():
                visual_entries.append(f"{indent}📁 {path.name}/\n")
                dirs.append(path)
            elif path.is_file():
                visual_entries.append(f"{indent}📄 {path.name} ({path.suffix})\n")
                files.append(path)
            path_repo_structure.append(path)

        visual_repo_structure = "".join(visual_entries)
        raw_data = f"Retrieved {len(files)} files and {len(dirs)} subdirectories within {target_dir}."

        return FileSystemResult(
            status=FileOpStatus.SEARCHED_RECURSIVELY_SUCCESS,
            files=files,
            dirs=dirs,
            visual_repo_structure=visual_repo_structure,
            path_repo_structure=path_repo_structure,
            raw_data=raw_data,
        )
