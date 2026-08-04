# get_issue Tool responses

## retrieved_issue

The issue `{issue_number}` was retrieved, with its title, description, and state.

Issue Title: `{issue_title}`
Issue Description: `{issue_description}`
Issue State: `{issue_state}`

issue_dict:
{issue_dict}

Comments:
{comments}

raw_data:
`{raw_data}`

## issue_not_found

The issue `{issue_number}` was not able to be found or retrieved.

The error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

_Action Required: The issue number is not correct, so other issue numbers might need to be choosen instead._

## api_error

Could not retrieve the issue `{issue_number}` via the GitHub API.

The error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

## general_exception

There is some other reason, such as connectivity problems, for the error when trying to retrieve the issue `{issue_number}`.
