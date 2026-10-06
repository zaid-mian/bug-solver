import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.paginator import paginate


def test_first_page():
    data = [1, 2, 3, 4, 5]
    assert paginate(data, page=1, page_size=2) == [1, 2]

def test_second_page():
    data = [1, 2, 3, 4, 5]
    assert paginate(data, page=2, page_size=2) == [3, 4]
