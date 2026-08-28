# collect_tests Tool responses

## all_collected_tests

All tests collected successfully.
Keyword that may have been provided: `{keyword}`

Test file paths:
`{paths}`

raw_data: {tests_result}
passed: {passed}

## collection_level_errors

## some_tests_not_collected

Some tests collected successfully, and others failed.
Keyword that may have been provided: `{keyword}`

Test file paths:
`{paths}`

raw_data: {raw_data}
passed: {passed}
failed: {failed}

_Action Required: Give the raw data and failed tests to be collected back to the planner._

## no_tests_collected

Tests were not able to be collected, they may not exist in the repository.
Keyword that may have been provided: `{keyword}`

Test file paths:
`{paths}`

raw_data: `{raw_data}`
error_details: `{error_details}`
passed: {passed}
failed: {failed}

_Action Required: Should try not to use the tests that were specified in the given paths. If no tests exist in the repository, then the agent should make some test files._

## interrupted

Tried to collect tests but the process was interrupted.
Keyword that may have been provided: `{keyword}`

Test file paths:
`{paths}`

raw_data: `{raw_data}`
error_details: `{error_details}`
passed: {passed}
failed: {failed}
