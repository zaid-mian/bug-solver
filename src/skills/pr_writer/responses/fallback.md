# fallback Tool responses

## executed_fallback_command

Successfully executed the escape hatch/fallback command tool, to resolve a more complicated problem outside the scope of the rest of the git tools.

The command arguments:
`{args_str}`

The command result:
`{raw_data}`

## forbidden_args

When an escape hatch/fallback command tool was attempted it failed due to the inclusion of forbidden arguments (those that expose security risks).

The command arguments:
`{args_str}`

The error details:
raw_data: `{raw_data}`
error_details: `{error_details}`

## timeout

When an escape hatch/fallback command tool was attempted it failed due to a timeout for any interactive commands that need a response or input back.

Error details:
`{error_details}`

## subprocess_error

Ran into a CalledProcessError when attempting to run escape hatch/fallback command tool.

The command arguments:
`{args_str}`

The error details:
raw_data: `{raw_data}`
error_details: `{error_details}`
