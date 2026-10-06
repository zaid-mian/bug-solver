"""benchmarks/setup_fixtures.py

Sets up standalone, reproducible benchmark fixtures with git repos and failing tests.
"""

import subprocess
from pathlib import Path


def init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "BenchmarkRunner"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "benchmark@bugsolver.dev"], cwd=path, check=True)
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit with failing test"], cwd=path, check=True)


def setup_all_fixtures() -> None:
    fixtures_dir = Path(__file__).resolve().parent / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    # Fixture 1: null_guard
    f1 = fixtures_dir / "null_guard"
    f1.mkdir(parents=True, exist_ok=True)
    (f1 / "src").mkdir(exist_ok=True)
    (f1 / "tests").mkdir(exist_ok=True)
    (f1 / "src" / "calculator.py").write_text(
        "def parse_and_sum(values: list[int | None]) -> int:\n"
        "    total = 0\n"
        "    for v in values:\n"
        "        total += v  # Bug: NoneType not filtered\n"
        "    return total\n",
        encoding="utf-8",
    )
    (f1 / "tests" / "test_calculator.py").write_text(
        "import pytest\n"
        "import sys\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parent.parent))\n"
        "from src.calculator import parse_and_sum\n\n"
        "def test_sum_integers():\n"
        "    assert parse_and_sum([1, 2, 3]) == 6\n\n"
        "def test_sum_with_none_values():\n"
        "    assert parse_and_sum([1, None, 3, None]) == 4\n",
        encoding="utf-8",
    )
    if not (f1 / ".git").exists():
        init_git_repo(f1)

    # Fixture 2: off_by_one
    f2 = fixtures_dir / "off_by_one"
    f2.mkdir(parents=True, exist_ok=True)
    (f2 / "src").mkdir(exist_ok=True)
    (f2 / "tests").mkdir(exist_ok=True)
    (f2 / "src" / "paginator.py").write_text(
        "def paginate(items: list, page: int, page_size: int) -> list:\n"
        "    # Bug: 1-indexed page arithmetic off by one\n"
        "    start = page * page_size\n"
        "    end = start + page_size\n"
        "    return items[start:end]\n",
        encoding="utf-8",
    )
    (f2 / "tests" / "test_paginator.py").write_text(
        "import sys\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parent.parent))\n"
        "from src.paginator import paginate\n\n"
        "def test_first_page():\n"
        "    data = [1, 2, 3, 4, 5]\n"
        "    assert paginate(data, page=1, page_size=2) == [1, 2]\n\n"
        "def test_second_page():\n"
        "    data = [1, 2, 3, 4, 5]\n"
        "    assert paginate(data, page=2, page_size=2) == [3, 4]\n",
        encoding="utf-8",
    )
    if not (f2 / ".git").exists():
        init_git_repo(f2)

    # Fixture 3: missing_key
    f3 = fixtures_dir / "missing_key"
    f3.mkdir(parents=True, exist_ok=True)
    (f3 / "src").mkdir(exist_ok=True)
    (f3 / "tests").mkdir(exist_ok=True)
    (f3 / "src" / "config_loader.py").write_text(
        "def get_database_url(config: dict) -> str:\n"
        "    # Bug: raises KeyError if host or port missing\n"
        "    host = config['host']\n"
        "    port = config['port']\n"
        "    user = config.get('user', 'root')\n"
        "    return f'postgres://{user}@{host}:{port}/db'\n",
        encoding="utf-8",
    )
    (f3 / "tests" / "test_config_loader.py").write_text(
        "import sys\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parent.parent))\n"
        "from src.config_loader import get_database_url\n\n"
        "def test_full_config():\n"
        "    assert get_database_url({'host': 'localhost', 'port': 5432, 'user': 'admin'}) == 'postgres://admin@localhost:5432/db'\n\n"
        "def test_default_port():\n"
        "    assert get_database_url({'host': 'localhost'}) == 'postgres://root@localhost:5432/db'\n",
        encoding="utf-8",
    )
    if not (f3 / ".git").exists():
        init_git_repo(f3)

    print("Successfully set up benchmark fixtures in:", fixtures_dir)


if __name__ == "__main__":
    setup_all_fixtures()
