"""Unit tests for the pytest argument sanitizer (the sandbox guard)."""

from adapters.testing.SubprocessPytestManager import sanitize_pytest_args


def test_normal_args_pass():
    ok, tokens, _ = sanitize_pytest_args("tests/test_api.py -x -q")
    assert ok
    assert tokens == ["tests/test_api.py", "-x", "-q"]


def test_quoted_k_expression_passes():
    ok, tokens, _ = sanitize_pytest_args('tests/ -k "test_login or test_signup"')
    assert ok
    assert "-k" in tokens


def test_shell_metachars_rejected():
    for bad in [
        "tests/; rm -rf /",
        "tests/ | cat /etc/passwd",
        "tests/ && echo pwned",
        "tests/ $(whoami)",
        "tests/ `whoami`",
        "tests/ > /tmp/out",
    ]:
        ok, _, reason = sanitize_pytest_args(bad)
        assert not ok, f"should have blocked: {bad}"
        assert reason


def test_interactive_flags_rejected():
    for bad in ["tests/ --pdb", "--pdbcls tests/"]:
        ok, _, _ = sanitize_pytest_args(bad)
        assert not ok, f"should have blocked: {bad}"


def test_empty_and_broken_input_rejected():
    ok, _, _ = sanitize_pytest_args("")
    assert not ok
    ok, _, _ = sanitize_pytest_args('tests/ "unclosed')
    assert not ok
