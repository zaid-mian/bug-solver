# pull Tool responses

## pulled_from_remote_branch

Successfully pulled from the remote `{remote}` in branch `{branch_name}`

Pull result:
`{raw_data}`

## merge_conflict

When attempting to pull from the remote `{remote}` branch `{branch_name}` Git determined there would be a merge conflict.

Error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

_Action Required: Will need to locate and understand any conflict markers in the repository, should use git status to find the conflicted files._

## local_changes_conflict

When attempting to pull from the remote `{remote}` branch `{branch_name}` Git determined it would overwrite local uncommitted changes.

Error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

_Action Required: Commit or stash local changes before pulling._

## no_upstream_set

The local branch `{branch_name}` has no tracking information set for a remote branch.

Error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

_Action Required: Set the upstream with `git branch --set-upstream-to={remote}/{branch_name}` or push with `-u` first._

## missing_branch_or_reference

Could not find the remote ref for branch `{branch_name}` on remote `{remote}`.

Error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

_Action Required: Verify the branch name exists on the remote and the remote label is correct._

## subprocess_error

Ran into a CalledProcessError when attempting to pull from remote `{remote}` branch `{branch_name}`.

The error details:
raw_data: `{raw_data}`
error_details: `{error_details}`
