#!/usr/bin/env python3
"""
Fix-rate benchmark for bug-solver.

Runs the agent over a list of tasks and scores it: success rate, attempts,
and wall-clock time per task. This is the reproducible evaluation artifact
behind any fix-rate numbers quoted in the README.

Usage:
    python benchmarks/run_benchmark.py benchmarks/tasks.example.json --output benchmarks/results/

tasks.json format:
    [
      {
        "name": "example-null-guard",
        "repo_path": "/path/to/target/repo",
        "bug": "Fix the None guard in parser.py: parse() crashes on empty input.",
        "notes": "optional free text"
      }
    ]

Environment:
    BUGSOLVER_MODEL  Ollama model to use (default: qwen2.5-coder:7b)
    OLLAMA_HOST      Ollama base URL (default: http://localhost:11434)

Benchmarks always run in local-only mode: the agent may commit on its fix
branch, but it will never push or open PRs.
"""

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from langchain_ollama import ChatOllama  # noqa: E402

from constants import Status  # noqa: E402
from agent.graph import app  # noqa: E402
from adapters.git.SubprocessGitManager import SubprocessGitManager  # noqa: E402
from adapters.filesystem.PATHLIBPythonManager import PATHLIBPythonManager  # noqa: E402
from adapters.testing.SubprocessPytestManager import SubprocessPytestManager  # noqa: E402


def run_task(task: dict) -> dict:
    repo_path = Path(task["repo_path"]).resolve()
    target = task["bug"]

    model = ChatOllama(
        model=os.environ.get("BUGSOLVER_MODEL", "qwen2.5-coder:7b"),
        base_url=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
    )
    config = {
        "configurable": {
            "model": model,
            "adapters": {
                "git_manager": SubprocessGitManager(repo_path=repo_path),
                "workspace_manager": PATHLIBPythonManager(root=repo_path),
                "github_manager": None,
                "test_manager": SubprocessPytestManager(repo_path=repo_path),
            },
            "execution_mode": {
                "auto_pr": False,
                "new_branch": False,
                "local_only": True,
                "is_remote_issue": False,
            },
        }
    }
    initial_state = {
        "issue_id": None,
        "issue_description": target,
        "repo_name": repo_path.name,
        "repo_path": str(repo_path),
        "status": Status.IN_PROGRESS,
        "relevant_files": [],
        "retry_count": 0,
        "messages": [],
    }

    started = time.time()
    outcome = {
        "name": task["name"],
        "status": "ERROR",
        "retry_count": None,
        "duration_s": None,
        "error": None,
    }
    try:
        result = app.invoke(initial_state, config=config)
        outcome["status"] = str(result.get("status"))
        outcome["retry_count"] = result.get("retry_count")
    except Exception as e:  # noqa: BLE001 - benchmark must not die on one task
        outcome["error"] = f"{type(e).__name__}: {e}\n{traceback.format_exc()[-2000:]}"
    finally:
        outcome["duration_s"] = round(time.time() - started, 1)
    return outcome


def write_scorecard(results: list, out_dir: Path) -> None:
    successes = sum(1 for r in results if r["status"] == "SUCCESS")
    total = len(results)
    lines = [
        "# bug-solver benchmark scorecard",
        "",
        f"_Generated {datetime.now(timezone.utc).isoformat()} · "
        f"model `{os.environ.get('BUGSOLVER_MODEL', 'qwen2.5-coder:7b')}`_",
        "",
        f"**Fix rate: {successes}/{total} ({100.0 * successes / total if total else 0:.0f}%)**",
        "",
        "| Task | Status | Attempts | Duration (s) |",
        "| --- | --- | --- | --- |",
    ]
    for r in results:
        lines.append(
            f"| {r['name']} | {r['status']} | {r['retry_count']} | {r['duration_s']} |"
        )
    lines += ["", "## Errors", ""]
    for r in results:
        if r["error"]:
            lines += [f"### {r['name']}", "", "```", r["error"][-1500:], "```", ""]
    (out_dir / "scorecard.md").write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark bug-solver fix rate.")
    parser.add_argument("tasks", help="Path to tasks JSON file.")
    parser.add_argument(
        "--output", default="benchmarks/results", help="Directory for results."
    )
    args = parser.parse_args()

    tasks = json.loads(Path(args.tasks).read_text())
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for i, task in enumerate(tasks, 1):
        print(f"[{i}/{len(tasks)}] {task['name']} ...", flush=True)
        results.append(run_task(task))
        print(f"    -> {results[-1]['status']} "
              f"({results[-1]['retry_count']} attempts, "
              f"{results[-1]['duration_s']}s)", flush=True)

    (out_dir / "results.json").write_text(json.dumps(results, indent=2))
    write_scorecard(results, out_dir)
    print(f"\nWrote {out_dir / 'results.json'} and {out_dir / 'scorecard.md'}")


if __name__ == "__main__":
    main()
