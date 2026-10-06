import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.calculator import parse_and_sum


def test_sum_integers():
    assert parse_and_sum([1, 2, 3]) == 6

def test_sum_with_none_values():
    assert parse_and_sum([1, None, 3, None]) == 4
