# commit Tool responses

## staged_and_committed

Staged and committed the patched code and bug fixes.

Commit message:
`{messages}`

Committed files:
{files}

Commit result:
`{commit_result}`

# gitignore_error

Some of the files that were staged are explicitly ignored content in .gitignore.

Files that .gitignored:
{ignored_files}

All files:
{files}

Error details:
raw_data: {raw_data}
error_details: {error_details}

_Action Required: Remove the gitignored files from the patch code fix._

# pathspec_error

Some of the files' pathspec did not match any files in the current working directory or subdirectories when a stage command was run.

Files that are unmatched:
{unmatched_files}

All files:
{files}

Staged files:
{committed_files}

Error details:
raw_data: {raw_data}
error_details: {error_details}

_Action Required: Make sure to write the unmatched files into the filesystem/repo first, then attempt again for the unmatched files._

# gitrepo_error

The current working directory that was attempted to be staged in was not in a git repository.

All files attempted:
{files}

Error details:
raw_data: {raw_data}
error_details: {error_details}

_Action Required: Switched to a git directory, mabye go down levels and/or get a list of the directory._

# missing_commit_message

The commit command is missing a commit message.

Error details:
raw_data: {raw_data}
error_details: {error_details}

_Action Required: Create a commit message, then attempt to stage and commit again._

# clean_tree

There have been no modified or staged (using git add) files prior to this commit command.

Error details:
raw_data: {raw_data}
error_details: {error_details}

_Action Required: Since the logic guarantees that a git add is run before the commit command in the tooling, it must mean that there have been no changes made. Therefore, go back to planning and coding the bug fix._

# subprocess_error

Ran into a CalledProcessError when attempting to stage and commit code, using subprocess.

Files attempted to be staged or committed:
{files}

The error details:
raw_data: {raw_data}
error_details: {error_details}
