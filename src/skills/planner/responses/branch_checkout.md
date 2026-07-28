# branch_checkout Tool responses

## switched_to_existing

Did not create a new branch. Switched to an existing local branch with name: `{branch_name}`.

## already_on_branch

Did not create a new branch. Was already on an existing local branch with name: `{branch_name}`.

## branch_exists_remotely

Failed to switch to an existing local branch with name `{branch_name}` because a branch with that name exists remotely. Therefore, it probably belonged to another developer and would not be good practice to commit to it.

Existing branches in the remote repository:
{all_branches}

_Action Required: Choose a unique branch name (e.g., `{branch_name}-v2`), etc._

## branch_already_exists

Failed to create branch `{branch_name}` because a branch with that name already exists.

Existing branches in this repository:
{existing_branches}

_Action Required: Choose a unique branch name (e.g., `{branch_name}-v2`), etc._

## branch_created

Created and switched to a new branch `{branch_name}`.

# subprocess_error

Ran into a CalledProcessError when attempting to switch or creating a new branch, with branch name `{branch_name}`, using subprocess.

The error details:
raw_data: `{raw_data}`
error_details: `{error_details}`
