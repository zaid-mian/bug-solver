# status Tool responses

## git_status

Successfully ran the git_status command.

Status result:
`{raw_data}`

## merge_conflict

When checking the status Git determined there would be a merge conflict due to unmerged files.

Error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

_Action Required: Most likely will need to deal with unmerged files, so may need to stage additional files._

## subprocess_error

Ran into a CalledProcessError when attempting to run git status.

The error details:
raw_data: `{raw_data}`
error_details: `{error_details}`
