# run_test_command Tool responses

## executed_fallback_command

Successfully executed a fallback test command.
Argument str: `{args_str}`

raw_data: {raw_data}

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
