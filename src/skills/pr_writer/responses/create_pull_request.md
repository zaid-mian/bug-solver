# create_pull_request Tool response

## pr_made

The Pull Request with title `{title}` was made from branch `{head_branch}` to base branch `{base_branch}`.

PR details:
`{raw_data}`

## unprocessable

The PR with title `{title}` already exists, or the head and base branches are identical. Check the below error details for the message "A pull request already exists for...".

Error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

_Action Required: You might need to make a new PR with another title, or make sure the branch's for head and base are different._

## repo_or_branch_not_found

Either the GitHub repository or the branch is not found.

Error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

_Action Required: You may need to change the base or head branch, or ensure that the repository is correct._

## general_exception

General error was encountered, below are the error details.

Error details:
raw_data: `{raw_data}`
error_details: `{error_details}`
