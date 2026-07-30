# -------------------------------------
#  Adapter Type: Filesystem Operations
# -------------------------------------

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, Dict
from pathlib import Path


class FileOpStatus(Enum):
    # -------------------------
    #  For read_files
    # -------------------------
    SUCCESSFULLY_READ_SOME_FILES = "successfully_read_some_files"

    # -------------------------
    #  For write_files
    # -------------------------
    SUCCESSFULLY_WROTE_SOME_FILES = "successfully_wrote_some_files"

    # -------------------------
    #  For find_files
    # -------------------------
    FOUND_MATCHES = "found_matches"

    # errors
    NO_MATCHES = "no_matches"

    # -------------------------
    #  For list_dir
    # -------------------------
    SEARCHED_RECURSIVELY_SUCCESS = "searched_recursively_success"
    SEARCHED_SHALLOW_SUCCESS = "searched_shallow_success"

    # errors
    DIR_NON_EXISTENT = "dir_non_existent"
    NOT_DIR = "not_dir"


@dataclass
class FileSystemResult:
    status: FileOpStatus

    # for read_files
    read_file_contents: Optional[Dict[Path, str]] = None
    unread_file_content: Optional[Dict[Path, str]] = None

    # for write_files
    written_files: Optional[list[Path]] = None
    unwritten_files: Optional[Dict[Path, str]] = None

    # for find_files
    matched_files: Optional[list[Path]] = None
    unreadable_files: Optional[list[Path]] = None  # also for read_files

    # for list_dir
    files: Optional[list[Path]] = None  # also for find_files
    dirs: Optional[list[Path]] = None
    visual_repo_structure: Optional[str] = None
    path_repo_structure: Optional[list[Path]] = None

    raw_data: Any = None
    error_details: Optional[str] = None
