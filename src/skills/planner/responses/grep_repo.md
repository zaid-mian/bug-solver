# grep_repo Tool responses

## found_matches

Ran a git grep command and got matches for a given pattern in either python or markdown files within the src directory and all its subdirectories.

Text pattern:
`{text_pattern}`

Match string result:
`{raw_data}`

## no_matches

Ran a git grep command and got no matches for a given pattern in either python or markdown files within the src directory and all its subdirectories.

Text pattern:
`{text_pattern}`

The error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

_Action Required: Might need to change the text pattern(s)._

## subprocess_error

Ran into a CalledProcessError when attempting to run a git branch command to retrieve all local branches in repository.

The error details:
raw_data: `{raw_data}`
error_details: `{error_details}`
