import shlex
from typing import List, Tuple

# Flags and options that allow running external executables or changing git configs
BANNED_FLAGS = {
    "-c",  # Git inline config override
    "--config",  # The same override
    "--exec",  # Git rebase shell execution
    "--upload-pack",  # Specifies custom executable for fetch/push
    "--reieve-pack",  # Specifies custom exectuable for push
    "--ext-diff",  # Runs external diff executable
    "--output-indicator-new",  # Can be abused in certain git drivers
}

# Subcommands that are unsafe for an agent
BANNED_SUBCOMMANDS = {
    "bisect",  # Interactive / stateful debugging
    "config",  # Prevents agent from permanently modifying global/local .gitconfig
    "gitk",
    "gui",  # GUI triggers
}


def sanitize_and_tokenize(args_str: str) -> Tuple[bool, List[str], str]:
    """
    Parses an un-sanitized string into CLI arguments.
    Returns: (is_safe: bool, tokens: List[str], error_reason: str)
    """

    try:
        # Tokenize argument string sefely handling quotes
        tokens = shlex.split(args_str)
    except ValueError as e:
        return False, [], f"Invalid shell syntax or unclosed quote: {str(e)}."

    if not tokens:
        return False, [], "No Git arguments provided."

    subcommand = tokens[0].lower()
    if subcommand in BANNED_SUBCOMMANDS:
        return False, [], f"The Git subcommand '{subcommand}' is prohibited."

    # Inspect tokens for banned flags
    for token in tokens:
        violations = []
        # Check exact matches or flags starting with banned prefixes (e.g. -c core.pager=...)
        for banned in BANNED_FLAGS:
            if (
                token == banned
                or token.startswith(f"{banned}=")
                or token.startswith(f"{banned}:")
            ):
                violations.append(banned)

        return False, [], f"Security policy blocked arguments/flags: '{violations}'"

    return True, tokens, ""
