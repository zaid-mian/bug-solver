# Bug Solver Agent — Roadmap & Progress

A living status of what's implemented and what remains. This is a planning
document only — it describes intent and state, not implementation.

Legend: ✅ done · 🟡 partial / in progress · ⬜ not started

---

## 1. Graph & Orchestration

| Component | Status | Notes |
| --- | --- | --- |
| Graph topology (nodes, edges, conditional routing) | ✅ | Planner → Coder → Test Runner → Evaluator → {PR Writer, Coder, Planner} |
| `State` schema | ✅ | Issue id/description, repo path, relevant files, plan, patch, test output, retry count, status |
| `Context` / runtime config schema | 🟡 | Placeholder `my_configurable_param` still from the template |
| `check_status` conditional router | 🟡 | Logic sketched; relies on `Status` values and `MAX_RETRIES` |
| Node functions (planner, coder, test_runner, evaluator, pr_writer) | ⬜ | All return `"Placeholder"` — no real logic yet |

### Necessary steps
- Replace the placeholder `Context` param with real per-run configuration (model, execution mode, adapters).
- Decide how adapters/managers reach the nodes (via `Context`/`RunnableConfig` vs. tool binding).
- Implement each node to call its skill prompt + bound tools and update `State`.
- Firm up `check_status` return values and confirm they match the conditional-edge mapping.

---

## 2. Adapters

### 2.1 Git (`adapters/git/`)

| Piece | Status | Notes |
| --- | --- | --- |
| `BaseGitRepo` interface | ✅ | `list_local_branches`, `checkout_branch`, `apply_patch_or_commit`, `push`, `pull`, `git_status`, `search_repo_text`, `run_git_command` |
| `GitResult` / `GitOpStatus` typed results | ✅ | Per-outcome statuses; `GitResult` carries `raw_data`, `error_details`, and staging detail lists |
| `SubprocessGitManager` | 🟡 | Most operations implemented via the `git` CLI with granular error mapping |
| `security.sanitize_and_tokenize` (escape-hatch guard) | ✅ | `shlex` tokenize + banned flags/subcommands |
| `GitPythonManager` | ⬜ | Stubbed only — every method returns a placeholder |

### Necessary steps
- Implement `GitPythonManager` (or formally drop it in favor of the subprocess impl).
- Confirm `search_repo_text` pathspec/globbing works as intended across repos.
- Review substring branch-name matching in `checkout_branch` (partial-name collisions).
- Add unit tests for each `GitOpStatus` branch.

### 2.2 Filesystem (`adapters/filesystem/`)

| Piece | Status | Notes |
| --- | --- | --- |
| `BaseFileSystemTools` interface | ✅ | `read_file`, `write_files`, `find_files`, `list_dir` |
| `types.py` | ⬜ | Empty |
| Concrete implementation | ⬜ | None yet |

### Necessary steps
- Define filesystem result/error types.
- Implement a concrete filesystem adapter (used by the Coder to read/write patches).

### 2.3 Platform / GitHub (`adapters/platform/`)

| Piece | Status | Notes |
| --- | --- | --- |
| `BaseGitHubClient` interface | ✅ | `get_issue`, `create_pull_request`, `post_issue_comment` |
| `types.py` | ⬜ | Empty |
| Concrete implementation (e.g. PyGithub) | ⬜ | Referenced in `cli.py` as `PyGithubManager` but not implemented |

### Necessary steps
- Implement a concrete GitHub client and align its name with `cli.py`.
- Define platform result/error types.
- Wire issue fetching (Mode 1) and PR creation into the PR Writer node.

---

## 3. Tools (`tools/`)

| Tool module | Status | Notes |
| --- | --- | --- |
| `git_tools.py` factory | 🟡 | `list_local_branches`, `checkout_branch`, `stage_patch_and_commit`, `push`, `pull` wrapped |
| Git: `git_status`, `search_repo_text`, `run_git_command` tools | ⬜ | Adapter methods exist; not yet exposed as tools |
| `github_tools.py` | ⬜ | Empty |
| `workspace_tools.py` (filesystem) | ⬜ | Empty |

### Necessary steps
- Wrap the remaining git operations (status, grep, escape hatch) as tools.
- Build filesystem/workspace tools over `BaseFileSystemTools`.
- Build GitHub tools over `BaseGitHubClient`.
- Bind each tool set to the appropriate node.

---

## 4. Skills & Response Templates (`skills/`)

| Piece | Status | Notes |
| --- | --- | --- |
| Planner git response templates | ✅ | `branch_checkout`, `commit`, `push`, `pull`, `status`, `grep_repo`, `local_branches`, `fallback` |
| `template_loader.py` | ✅ | Extracts a `##` section by `GitOpStatus` value |
| `SKILL.md` prompts (all nodes) | ⬜ | Files exist but are empty |
| Coder / Evaluator / Test Runner / PR Writer response templates | ⬜ | Not started |

### Necessary steps
- Author the `SKILL.md` system prompt for each node.
- Add response templates for the non-git tool surfaces.
- Verify every `GitOpStatus` has a matching `##` section (and that template placeholders match what the tools pass in).

---

## 5. CLI (`cli.py`)

| Piece | Status | Notes |
| --- | --- | --- |
| Typer `run` command + options | ✅ | `--path`, `--new-branch`, `--pr`, `--local-only` |
| Target resolution (issue number vs. prose) | ✅ | |
| Repo root discovery | ✅ | |
| Manager wiring | 🟡 | Instantiates managers but imports/names need reconciliation |
| Graph invocation | ✅ | Builds `RunnableConfig` and calls `app.invoke` |

### Necessary steps
- Reconcile imports/names (`SubprocessGitManager`, GitHub manager) with the actual adapter modules.
- Ensure the execution-mode flags flow through to the nodes.

---

## 6. Testing

| Piece | Status | Notes |
| --- | --- | --- |
| Template unit tests (from LangGraph starter) | 🟡 | Configuration/graph tests still reference the template |
| Subprocess git exploration scripts | 🟡 | Scratch scripts under `tests/subprocess_git_tests/` |
| Adapter unit tests | ⬜ | |
| Tool-layer tests | ⬜ | |
| End-to-end graph run | ⬜ | |

### Necessary steps
- Add unit tests per adapter method / `GitOpStatus` branch.
- Add tool-layer tests asserting the right template renders per status.
- Stand up an end-to-end run against a throwaway repo once nodes are implemented.

---

## Near-term priority order

1. Implement the concrete **filesystem** and **GitHub** adapters (unblock Coder + PR Writer).
2. Finish the **tool** wrappers for all adapter surfaces.
3. Author the **`SKILL.md`** prompts.
4. Implement the **node functions** to tie prompts + tools + state together.
5. Reconcile **CLI** wiring and run the first **end-to-end** pass.
6. Backfill **tests**.
