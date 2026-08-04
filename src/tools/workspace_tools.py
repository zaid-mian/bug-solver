"""
src/tools/workspace_tools.py

Bridge layer exposing Filesystem operations to the LLM.
Translates adapter responses/outcomes into Markdown response templates.
"""

# -----------------------------------------
#  Necessary Standard & LangChain Imports
# -----------------------------------------
import os
from pathlib import Path
from typing import List, Callable, Dict
from langchain_core.tools import tool, BaseTool

# -----------------------------------------
#  Abstract Interface & Result Types
# -----------------------------------------
from adapters.filesystem.base import BaseFileSystemTools
from adapters.filesystem.types import FileSystemResult, FileOpStatus

# -----------------------------------------
#  Helper / Prompt Engineering Utility
# -----------------------------------------
from utils.template_loader import load_response_tempate


# -----------------------------------------
#  Factory Function (Dependency Injection)
# -----------------------------------------
def workspace_tools(filesystem_adapter: BaseFileSystemTools) -> List[BaseTool]:
    """
    Factory that binds an adapter implementation to LangChain @tools decorators.
    Using parse_docstring to give more argument context to the LLM.
    Returns a list of tools to be bound to a LangGraph node(s).
    """

    # -----------------------------------------
    #  Tool 1: Read Files Tool
    # -----------------------------------------
    @tool(parse_docstring=True)
    def read_files(file_paths: list[str | os.PathLike | Path]) -> str:
        """
        Reads files from the repository, from a list of path that the LLM decides it needs to read.

        Args:
            file_paths: Takes a list of file paths, can take string, os type, or pathlib Path.
        """

        # Execute via abstract adapter
        result: FileSystemResult = filesystem_adapter.read_files(file_paths=file_paths)

        # Then load the markdown response template
        template: str = load_response_tempate(
            skill="planner", tool_name="read_files", section=result.status.value
        )

        # Format template placeholders with tool inputs and adapter results
        return template.format(
            read_file_contents=result.read_file_contents,
            unread_file_contents=result.unread_file_content,
        )

    # ----------------------------------------
    #  Tool 2: Write Files Tool
    # ----------------------------------------
    @tool(parse_docstring=True)
    def write_files(
        file_paths_and_edits: Dict[str | os.PathLike | Path, str],
    ) -> str:
        """
        Writes to files in the repository, from a list of path that the LLM decides it needs to write to for content edits.

        Args:
            file_paths_and_edits: Takes a dict of file paths, can take string, os type, or pathlib Path, and the edited or new content for a file.
        """

        # Execute via abstract adapter
        result: FileSystemResult = filesystem_adapter.write_files(
            file_paths_and_edits=file_paths_and_edits
        )

        # Then load the markdown response template
        template: str = load_response_tempate(
            skill="coder", tool_name="write_files", section=result.status.value
        )

        # Format template placeholders with tool inputs and adapter results
        return template.format(
            written_files=result.written_files,
            unwritten_files=result.unwritten_files,
            file_paths_and_edits=file_paths_and_edits,
        )

    # -----------------------------------------
    #  Tool 3: Find Files Tool
    # -----------------------------------------
    @tool(parse_docstring=True)
    def find_files(text_pattern: str) -> str:
        """
        Run a grep onto the entire repository directly for a pattern, text_pattern.

        Args:
            text_pattern: The text pattern or piece of code that is being searched for to get the files that need to modified, to fix the bug/issue.
        """

        # Execute via abstract adapter
        result: FileSystemResult = filesystem_adapter.find_files(
            text_pattern=text_pattern
        )

        # Then load the markdown response template
        template: str = load_response_tempate(
            skill="planner", tool_name="find_files", section=result.status.value
        )

        # Format template placeholders with tool inputs and adapter results
        return template.format(
            text_pattern=text_pattern,
            files=result.files,
            matched_files=result.matched_files,
            unreadable_files=result.unreadable_files,
            raw_data=result.raw_data,
            error_details=result.error_details,
        )

    # -------------------------------------
    #  Tool 4: List Directory Tool
    # -------------------------------------
    @tool(parse_docstring=True)
    def list_dir(
        dir: str | os.PathLike | Path = None, recursive_search: bool = True
    ) -> str:
        """
        Run through the directory structure, either recursively or not (recursive_search boolean), then returns visual representation and path representation of the structure, along a list of the files and directories found.

        Args:
            dir: Optional path of a directory that the LLM decides it needs to search through and/or under, default if this is not given is the root of the directory
            recursive_search: Optional boolean for whether a recursive search from dir (or root) is executed, default is true
        """

        # Execute via abstract adapter
        result: FileSystemResult = filesystem_adapter.list_dir(
            dir=dir, recursive_search=recursive_search
        )

        # Then load the markdown response template
        template: str = load_response_tempate(
            skill="planner", tool_name="list_dir", section=result.status.value
        )

        # Format template placeholders with tool inputs and adapter results
        return template.format(
            dir=dir,
            visual_repo_structure=result.visual_repo_structure,
            path_repo_structure=result.path_repo_structure,
            files=result.files,
            dirs=result.dirs,
            raw_data=result.raw_data,
        )

    return [read_files, write_files, find_files, list_dir]
