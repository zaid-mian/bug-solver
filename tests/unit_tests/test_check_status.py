"""Unit tests for the graph's conditional router (fixed in the completion work)."""

from agent.graph import check_status
from constants import MAX_RETRIES, Status


def _state(status, retry_count=0):
    return {"status": status, "retry_count": retry_count}


def test_failed_routes_back_to_coder():
    assert check_status(_state(Status.FAILED)) == 1


def test_success_routes_to_pr_writer():
    assert check_status(_state(Status.SUCCESS)) == 0


def test_in_progress_with_retries_left_routes_to_coder():
    # This was the original bug: the old code always returned 2 here.
    assert check_status(_state(Status.IN_PROGRESS, 0)) == 1
    assert check_status(_state(Status.IN_PROGRESS, MAX_RETRIES)) == 1


def test_in_progress_with_retries_exhausted_routes_to_planner():
    assert check_status(_state(Status.IN_PROGRESS, MAX_RETRIES + 1)) == 2
