# -------------------------------------
#  Concrete Extension of
#  BaseFileSystemTools Abstract Class
# -------------------------------------

import os
from pathlib import Path
from typing import Dict

from .base import BaseFileSystemTools
from .types import FileSystemResult, FileOpStatus


class PATHLIBPythonManager(BaseFileSystemTools):
    def __init__(self, root: Path):
        self.root = root

    def read_files(
        self, file_paths: list[str | os.PathLike | Path]
    ) -> FileSystemResult:
        """Reads file from local filesystem"""

        read_file_content = {}
        unreadable_files = {}

        # iterate through the files and read_text
        for file in file_paths:
            # convert to Path if not already
            file = Path(file)

            try:
                content = file.read_text(encoding="utf-8")

                # then add content to dict
                read_file_content[file] = content

            except FileNotFoundError:
                unreadable_files[file] = f"Error: The file at {file} does not exist."

            except IsADirectoryError:
                unreadable_files[file] = f"Error: {file} is a directory, not a file."

            except PermissionError:
                unreadable_files[file] = f"Error: Missing read permissions for {file}."

            except UnicodeDecodeError as e:
                unreadable_files[file] = (
                    f"Error: Failed to decode file using UTF-8. Details: {e}"
                )

            except OSError as e:
                unreadable_files[file] = (
                    f"System Error: A broader operating system error occurred: {e}"
                )

        # then return the successfully read files and their content, and the unsuccessfully read files
        return FileSystemResult(
            status=FileOpStatus.SUCCESSFULLY_READ_SOME_FILES,
            read_file_contents=read_file_content,
            unread_file_content=unreadable_files,
        )

    def write_files(
        self,
        file_paths_and_edits: list[str | os.PathLike | Path, str],
    ) -> FileSystemResult:
        """Writes file to local filesystem"""

        written_files = []
        unwritten_files = {}

        # iterate through the files and write_text
        # this assumes that the content that is being added/modified still gives the entirety of the file contents with the modifications within it.
        for file in file_paths_and_edits:
            # convert to Path if not already, and convert in content_edits too
            original_path = file
            file = Path(file)

            # ensure the parent directory exists first
            file.parent.mkdir(parents=True, exist_ok=True)

            # then write to file using write_text
            try:
                file.write_text(file_paths_and_edits[original_path], encoding="utf-8")

            except FileNotFoundError:
                unwritten_files[file] = (
                    f"Error: The directory structure for {file} does not exist."
                )

            except PermissionError:
                unwritten_files[file] = (
                    f"Error: Do not have permission to write to {file}."
                )

            except OSError as e:
                unwritten_files[file] = f"System error writing to {file}: {e}"

        # then return the successfully written files and unwritten/Error files
        return FileSystemResult(
            status=FileOpStatus.SUCCESSFULLY_WROTE_SOME_FILES,
            written_files=written_files,
            unwritten_files=unwritten_files,
        )

    def find_files(self, text_pattern: str) -> FileSystemResult:
        """Finds files by glop text patterns"""
        matches = []
        unreadable = []

        # first get files, so call list_dir from the root
        recursive_result: FileSystemResult = self.list_dir()
        files = recursive_result.files

        match_count = 0
        for file in files:
            try:
                if text_pattern in file.read_text(encoding="utf-8"):
                    matches.append(file)
                    match_count += 1
            except Exception:
                # skip files that cannot be read
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
            raw_data=f"Matches that were found: '{match_count}'.",
        )

    def list_dir(
        self, dir: str | os.PathLike | Path = None, recursive_search: bool = True
    ) -> FileSystemResult:
        """Gives a list of the directory/repoistory files/structure."""

        # the given directory, if it was given, may not be the root directory which is set at init
        # so check for the dir variable if it is given, if so use that.
        if dir:
            dir = Path(dir)
        else:
            dir = self.root

        # check if the dir actually exists
        if not dir.exists():
            return FileSystemResult(
                status=FileOpStatus.DIR_NON_EXISTENT,
                error_details=f"Error: the path of directory '{dir}' does not exist.",
            )

        # check if the given path for dir is actually a directory
        if not dir.is_dir():
            return FileSystemResult(
                status=FileOpStatus.NOT_DIR,
                error_details=f"Error: the path of 'directory' given '{dir}' is not actually a directory.",
            )

        # begin exploring from the directory path (root or not/given)
        dir.resolve()

        # track discovery counts
        file_count = 0
        dir_count = 0

        # check if we are doing a recursive search in the directory into its subdirectories or only surface level
        if not recursive_search:
            # list of everything in the directory dir
            all_entries = list(dir.iterdir())

            # then get the files and subdirectories specifically and their count
            files = [item for item in dir.iterdir() if item.is_file()]
            dirs = [item for item in dir.iterdir() if item.is_dir()]

            file_count = len(files)
            dir_count = len(dirs)

            # then return them
            raw_data = f"Retreived {file_count} of files and {dir_count} of subdirectories within the directory {dir}."
            return FileSystemResult(
                status=FileOpStatus.SEARCHED_SHALLOW_SUCCESS,
                files=files,
                dirs=dirs,
                raw_data=raw_data,
            )

        # Otherwise do a deep dive recursive search
        visual_repo_structure = ""
        path_repo_structure = []
        files = []
        dirs = []
        for path in sorted(dir.rglob("*")):
            # Calculate visual indentation depth based on structure
            depth = len(path.relative_to(dir).parts) - 1
            indent = " " * depth

            if path.is_dir():
                dir_count += 1

                visual_repo_structure.append(f"{indent}📁 {path.name}/\n")
                path_repo_structure.append(path)
                dirs.append(path)
            elif path.is_file():
                file_count += 1

                visual_repo_structure.append(f"{indent}📄 {path.name} ({path.suffix})")
                path_repo_structure.append(path)
                files.append(path)

        raw_data = f"Retreived {file_count} of files and {dir_count} of subdirectories within the entirety of the directory {dir} and its subdirectories."

        # then return the final result of recursive search
        return FileSystemResult(
            status=FileOpStatus.SEARCHED_RECURSIVELY_SUCCESS,
            visual_repo_structure=visual_repo_structure,
            path_repo_structure=path_repo_structure,
            raw_data=raw_data,
        )
