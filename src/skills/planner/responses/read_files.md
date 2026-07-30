# read_files Tool responses

## successfully_read_some_files

Read some files of the repository. However, there may have been some unreadable files. Below the dictionary of successfully read files and their content, and we have a dictionary of the unwritten files and their errors.

Read files:
{read_file_contents}

Unreadable files:
{unread_file_content}

_Action Required: Diagnose any of the unreadable files, based off their errors. Possible errors include a FileNotFoundError for directory structure or file, PermissionErrors, IsADicrectoryError, UnicodeDecodeError, or OSErrors._
