# Bug Solver Agent

A CLI-driven, autonomous **bug-fixing agent** built on [LangGraph](https://github.com/langchain-ai/langgraph). Point it at a local repository (or a GitHub issue), and it plans a fix, writes the code, runs the tests, evaluates the result, and — optionally — commits, pushes, and opens a Pull Request.

> ⚠️ **Work in progress.** The graph topology, CLI, adapter interfaces, and state schema are in place. Several node implementations, tool wrappers, and skill prompts are still scaffolding/placeholders.

## How it works

The agent is a LangGraph state machine with five nodes and a feedback loop:

```
START → Planner → Coder → Test Runner → Evaluator ─┬─ (success) ──→ PR Writer → END
                    ▲                               ├─ (failed)  ──→ Coder
                    │                               └─ (retries  ──→ Planner
                    └───────────────────────────────   exceeded)
```

- **Planner** — analyzes the issue/bug description and locates relevant files, producing a fix plan.
- **Coder** — generates the code patch for the plan.
- **Test Runner** — runs the test suite and captures output.
- **Evaluator** — inspects test results and decides the next step via `check_status`:
  - `SUCCESS` → move on to **PR Writer**
  - `FAILED` → loop back to **Coder** to try again
  - retry count exceeds `MAX_RETRIES` → loop back to **Planner** to re-plan
- **PR Writer** — commits, pushes, and opens the Pull Request (when not in local-only mode).

The graph is defined in [src/agent/graph.py](src/agent/graph.py). Shared constants (`MAX_RETRIES`, the `Status` enum) live in [src/constants.py](src/constants.py).

### State

The workflow state ([`State`](src/agent/graph.py)) tracks the issue id/description, repo path, relevant files, the fix plan, the generated patch, test output, a retry counter, and the current `Status`.

## Architecture

The agent talks to the outside world (Git, the filesystem, GitHub) through **adapter interfaces**, so the underlying implementation can be swapped without touching node logic.

```
src/
├── agent/
│   └── graph.py            # LangGraph nodes, edges, and conditional routing
├── adapters/               # Pluggable interfaces to the outside world
│   ├── git/                # Local Git operations
│   │   ├── base.py         #   BaseGitRepo abstract interface
│   │   ├── types.py        #   GitResult / GitOpStatus typed results
│   │   ├── security.py     #   arg sanitizer for the escape-hatch tool
│   │   ├── SubprocessGitManager.py   # concrete impl via `subprocess`
│   │   └── GitPythonManager.py       # concrete impl via GitPython
│   ├── filesystem/         # Local filesystem operations (read/write/find/list)
│   │   └── base.py         #   BaseFileSystemTools abstract interface
│   └── platform/           # Web platform (GitHub) operations
│       └── base.py         #   BaseGitHubClient abstract interface
├── skills/                 # Per-node prompts and templated tool responses
│   ├── planner/            #   SKILL.md + responses/*.md templates
│   ├── coder/
│   ├── evaluator/
│   ├── test_runner/
│   └── pr_writer/
├── tools/                  # LangChain tool wrappers over the adapters
├── utils/
│   └── template_loader.py  # loads a `##` section from a skill response .md
├── constants.py
└── cli.py                  # Typer CLI entrypoint
```

### Adapters

Each adapter domain exposes an abstract base class that the graph depends on:

- **`BaseGitRepo`** — `checkout_branch`, `apply_patch_or_commit`, `push`, `pull`, `git_status`, `search_repo_text`, plus `run_git_command` (a security-gated **escape hatch** for complex situations the standard tools don't cover). Every operation returns a typed `GitResult(status: GitOpStatus, raw_data, error_details)` so nodes can branch on rich, structured outcomes — the `GitOpStatus` enum enumerates a distinct status per known failure mode (e.g. `BRANCH_EXISTS_REMOTELY`, `GITIGNORE_ERROR`, `NON_FAST_FORWARD`, `MERGE_CONFICT`, `FORBIDDEN_ARGS`), each mapped to an actionable response template. `SubprocessGitManager` implements the full interface with the `git` CLI; `GitPythonManager` is a GitPython-based alternative (still stubbed). The escape hatch runs `git` with `shell=False` and passes args through [`security.sanitize_and_tokenize`](src/adapters/git/security.py), which `shlex`-tokenizes the input and blocks dangerous flags (`-c`, `--exec`, `--upload-pack`, …) and subcommands (`config`, `bisect`, …).
- **`BaseFileSystemTools`** — `read_file`, `write_files`, `find_files`, `list_dir`.
- **`BaseGitHubClient`** — `get_issue`, `create_pull_request`, `post_issue_comment`.

### Skills & templated responses

Each node has a `skills/<node>/SKILL.md` prompt. Tools can return human/agent-readable responses rendered from markdown templates under `skills/<node>/responses/`. [template_loader.py](src/utils/template_loader.py) extracts a named `##` section from those files — for example, [planner/responses/branch_checkout.md](src/skills/planner/responses/branch_checkout.md) maps each `GitOpStatus` to an explanatory message the agent can act on.

## CLI

The entrypoint is a [Typer](https://typer.tiangolo.com/) app in [src/cli.py](src/cli.py). The `run` command takes a **target** — either a numeric GitHub issue number or a prose bug description — resolves the repository, wires up the Git/GitHub managers, and invokes the graph.

```bash
# Mode 1: Fetch issue #142 from GitHub, fix locally, push & open a PR
bugsolver run 142 --pr

# Mode 2: Fix a local bug described in prose, local-only (no push/PR)
bugsolver run "Fix memory leak in parser" --local-only

# Mode 3: Keep changes local without pushing
bugsolver run 142 --local-only
```

Options:

| Option | Default | Description |
| --- | --- | --- |
| `--path`, `-p` | current repo root | Path to the local repository. |
| `--new-branch / --no-new-branch` | `--new-branch` | Create a new branch vs. use the current one. |
| `--pr / --no-pr` | `--pr` | Automatically open a Pull Request on GitHub. |
| `--local-only` | `False` | Keep changes local (no push/PR). |

The GitHub client is only wired up when a `GITHUB_TOKEN` environment variable is present.

## Getting started

1. Install dependencies, along with the [LangGraph CLI](https://langchain-ai.github.io/langgraph/concepts/langgraph_cli/):

```bash
cd path/to/bug-solver
pip install -e . "langgraph-cli[inmem]"
```

2. Create a `.env` file for secrets:

```bash
cp .env.example .env
```

```text
# .env
GITHUB_TOKEN=ghp_...          # required for issue fetching / PR creation
LANGSMITH_API_KEY=lsv2...     # optional, enables LangSmith tracing
```

3. Iterate on the graph in [LangGraph Studio](https://langchain-ai.github.io/langgraph/concepts/langgraph_studio/):

```bash
langgraph dev
```

## Development

While iterating in LangGraph Studio, you can edit past state and re-run from previous states to debug specific nodes; local changes hot-reload. For more, see the [LangGraph documentation](https://langchain-ai.github.io/langgraph/).
