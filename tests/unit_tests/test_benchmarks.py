import json
from pathlib import Path

from benchmarks.run_benchmark import write_scorecard


def test_write_scorecard(tmp_path: Path):
    mock_results = [
        {
            "name": "task-1",
            "status": "SUCCESS",
            "retry_count": 0,
            "duration_s": 2.5,
            "error": None,
        },
        {
            "name": "task-2",
            "status": "FAILED",
            "retry_count": 2,
            "duration_s": 5.1,
            "error": "AssertionError in tests",
        },
    ]
    out_dir = tmp_path / "results"
    out_dir.mkdir()
    write_scorecard(mock_results, out_dir)

    scorecard_path = out_dir / "scorecard.md"
    assert scorecard_path.exists()
    content = scorecard_path.read_text(encoding="utf-8")
    assert "Fix rate: 1/2 (50%)" in content
    assert "task-1" in content
    assert "task-2" in content
    assert "AssertionError in tests" in content


def test_tasks_json_validity():
    tasks_file = Path(__file__).resolve().parent.parent.parent / "benchmarks" / "tasks.json"
    assert tasks_file.exists()
    tasks = json.loads(tasks_file.read_text(encoding="utf-8"))
    assert len(tasks) == 3
    for task in tasks:
        assert "name" in task
        assert "repo_path" in task
        assert "bug" in task
