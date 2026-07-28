# pull Tool responses

## pulled_from_remote_branch

Successfully pulled from the remote `{remote}` in branch `{branch_name}`

Push result:
`{push_result}`

## merge_conflict

When attempting to pull from the remote `{remote}` branch `{branch_name}` Git determined there would be a merge conflict.

Error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

_Action Required: Will need to locate and understand any conflict markers in the repository, should use git status to find the conflicted files._

## subprocess_error

Ran into a CalledProcessError when attempting to push to remote `{remote}` branch `{branch_name}`, using subprocess.

The error details:
raw_data: `{raw_data}`
error_details: `{error_details}`
