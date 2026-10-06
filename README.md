# Bug Solver Agent

A CLI-driven, autonomous **bug-fixing agent** built on [LangGraph](https://github.com/langchain-ai/langgraph). Point it at a local repository (or a GitHub issue), and it plans a fix, writes the code, runs the tests, evaluates the result, and — optionally — commits, pushes, and opens a Pull Request. Runs on local models via [Ollama](https://ollama.com): **no API keys needed.**

> **Attribution:** this project was originally scaffolded by [Sawyer Anderson](https://github.com/sawyer-anderson1/bug-solver) (MIT) — the graph topology, adapters, tool bridges, and skill prompts. It was stalled with the core agent logic unimplemented. I completed and productionized it: implemented the three stub nodes, added the missing test-execution tooling, fixed packaging and routing bugs, and added tests, benchmarks, and Docker support. The original [LICENSE](LICENSE) is preserved.

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
- **Test Runner** — discovers the test setup, executes the tests in a sandbox, and records the full output.
- **Evaluator** — judges the test output: `SUCCESS` → PR Writer, `FAILED` → back to Coder with a diagnostic. After `MAX_RETRIES`, routes back to Planner for a fresh plan.
- **PR Writer** — commits on a dedicated `bugsolver/fix-*` branch, pushes, opens a Pull Request, and comments on the issue (skipped in `--local-only` mode).

### Safety design

The agent runs tests and git commands, so it is sandboxed by construction:

- Test commands run with `cwd` scoped to the target repo, `shell=False`, a timeout, and an argument sanitizer (shell metacharacters and interactive flags like `--pdb` are rejected).
- Git operations go through an adapter with `shlex` tokenization and banned flags/subcommands (`--exec`, `config`, `bisect`, …).
- The agent works on a dedicated fix branch — your current branch is never touched.

## Setup

```bash
# 1. Install Ollama and pull a code model (CPU-friendly default)
ollama pull qwen2.5-coder:7b

# 2. Install the agent
pip install .

# 3. (Optional) for GitHub issue mode + PR creation
export GITHUB_TOKEN=ghp_...
```

## Usage

```bash
# Fix a GitHub issue end-to-end (branch, fix, test, PR)
bugsolver run 142 --name owner/repo --pr

# Fix a locally-described bug, keep everything local
bugsolver run "Fix memory leak in parser" --name owner/repo --local-only

# Point at a different repo than the current directory
bugsolver run 142 --name owner/repo --path /path/to/repo --pr
```

Environment overrides: `BUGSOLVER_MODEL` (default `qwen2.5-coder:7b`), `OLLAMA_HOST` (default `http://localhost:11434`).

## What was completed (vs. the original scaffold)

| Component | Original state | Completed |
|---|---|---|
| Test Runner node | `return "Placeholder"` stub | Real ReACT node: discovers, runs, and records tests |
| Evaluator node | `return "Placeholder"` stub | Real judgment node with retry accounting |
| PR Writer node | `return "Placeholder"` stub | Commit → push → PR → issue comment, mode-aware |
| Test execution tool | Not implemented (README said so) | Sandboxed `run_tests` / `collect_tests` / `run_test_command` tools |
| `check_status` router | Always routed to Planner on retry (bug) | Correct SUCCESS → PR, FAILED → Coder, exhausted → Planner |
| Model wiring | `config["configurable"]["model"]` never provided (would crash) | Ollama wired in, zero API keys |
| Packaging | Broken template `pyproject.toml` (wouldn't install) | Real metadata, deps, `bugsolver` entry point |
| Tests | ~41 lines, effectively empty | Unit tests: router, sanitizer, tool factory e2e |
| Evaluation | None | `benchmarks/run_benchmark.py` → fix-rate scorecard |
| Deployment | None | Dockerfile |

## Benchmark

```bash
python benchmarks/run_benchmark.py benchmarks/tasks.example.json --output benchmarks/results/
# writes results.json + scorecard.md (fix rate, attempts, duration per task)
```

Benchmarks always run in `--local-only` mode: the agent may commit on its fix branch but never pushes or opens PRs.

## Docker

```bash
docker build -t bug-solver .
docker run --rm -e OLLAMA_HOST=host.docker.internal \
  -v /path/to/target/repo:/target -w /target bug-solver \
  run "Fix the null guard in parser" --name owner/repo --local-only
```

## Architecture

```
src/
├── agent/
│   ├── graph.py            # LangGraph state, nodes, edges, conditional routing
│   └── nodes.py            # Node implementations (planner, coder, test_runner, evaluator, pr_writer)
├── adapters/               # Pluggable interfaces to the outside world
│   ├── git/                # Local Git operations (subprocess impl + security sanitizer)
│   ├── filesystem/         # Local filesystem operations (pathlib impl)
│   ├── platform/           # GitHub operations (PyGithub impl)
│   └── testing/            # Test execution (sandboxed pytest runner)
├── skills/                 # Per-node system prompts and templated tool responses
├── tools/                  # LangChain tool factories over the adapters
├── utils/                  # Prompt/template loaders
├── constants.py            # MAX_RETRIES, Status enum
└── cli.py                  # Typer CLI entrypoint
```

See [docs/ROADMAP.md](docs/ROADMAP.md) for the original author's component status (note: some items are now done — the table above is the current truth).
