# run_tests Tool responses

## all_tests_passed

All tests ran successfully.
Keyword that may have been provided: `{keyword}`

Test file paths:
`{paths}`

raw_data: {tests_result}
passed: {passed}

## some_tests_failed

Some tests ran successfully, and others failed.
Keyword that may have been provided: `{keyword}`

Test file paths:
`{paths}`

raw_data: {raw_data}
passed: {passed}
failed: {failed}

_Action Required: Give the raw data and failed tests back to the planner._

## interrupted

Tried to run tests but the process was interrupted.
Keyword that may have been provided: `{keyword}`

Test file paths:
`{paths}`

raw_data: `{raw_data}`
error_details: `{error_details}`
passed: {passed}
failed: {failed}

## internal_error

When attempting to run tests there were an internal error.
Keyword that may have been provided: `{keyword}`

Test file paths:
`{paths}`

raw_data: `{raw_data}`
error_details: `{error_details}`
passed: {passed}
failed: {failed}

## usage_error

There was a usage error, so something about the command was wrong.
Keyword that may have been provided: `{keyword}`

Test file paths:
`{paths}`

raw_data: `{raw_data}`
error_details: `{error_details}`
passed: {passed}
failed: {failed}

_Action Required: The paths or keywords are probably what is causing this problem._

## no_tests_found

At least some of the test file paths provided could not be found.
Keyword that may have been provided: `{keyword}`

Test file paths:
`{paths}`

raw_data: `{raw_data}`
error_details: `{error_details}`
passed: {passed}
failed: {failed}

_Action Required: Should collect tests first. Make sure the all the paths provided exist and are tests._
