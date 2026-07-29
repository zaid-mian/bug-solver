# push Tool responses

## pushed_to_remote_branch

Successfully pushed to the remote `{remote}` in branch `{branch_name}`

Push result:
`{raw_data}`

## behind_branch

The remote `{remote}` repository in branch `{branch_name}` contains newer commits that do not exist locally. Git rejects the push to prevent overwriting someone else's work.

Error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

_Action Required: You may need to pull from the remote branch, handle rebasing, or stash changes before attempting the push._

## non_fast_forward

The remote `{remote}` repository in branch `{branch_name}` contains newer commits that do not exist locally. Git rejects the push to prevent overwriting someone else's work.

Error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

_Action Required: You may need to pull from the remote branch, handle rebasing, or stash changes before attempting the push._

## upstream_branch

The branch `{branch_name}` that we are trying to push did not specify to Git what remote (label `{remote}`) branch it should track. A push -u to origin for the branch `{branch_name}` was run, so that should have solved the issue.

Push result:
`{raw_data}`

Original error output:
`{error_details}`

_Action Required: The upstream branch error should be fixed, but just be aware that this occurred._

## failed_upstream_push

Had an upstream branch error for branch `{branch_name}` in remote `{remote}`, and attempted to fix it with push -u but it still failed.

Error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

_Action Required: Try to diagnose via the error details and raw data, attempt again with maybe other remote target labels, etc._

## repository_not_found

The current working directory that was attempted to be staged in was not in a git repository OR the remote target `{remote}` is not defined in the configuration.

Error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

_Action Required: Switch to a git directory, mabye go down levels and/or get a list of the directory. OR if the problem is the remote target then try other labels._

## subprocess_error

Ran into a CalledProcessError when attempting to push to remote `{remote}` branch `{branch_name}`.

The error details:
raw_data: `{raw_data}`
error_details: `{error_details}`
