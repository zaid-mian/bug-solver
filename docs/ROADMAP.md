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
| `Context` / runtime config schema | 🟡 | `Context` class is commented out; adapters and execution_mode pass via `config["configurable"]` |
| `check_status` conditional router | 🟡 | Logic present but returns `None` implicitly when `IN_PROGRESS` and retries not exceeded |
| Node functions (planner, coder, test_runner, evaluator, pr_writer) | 🟡 | `nodes.py` created; Planner has implementation structure; Coder, Test Runner, Evaluator, PR Writer still placeholder |
| `SKILL.md` system prompts (all nodes) | ✅ | All five nodes have prompts covering tools, responsibilities, and constraints |

### Necessary steps
- Fix `check_status`: add a `return 1` (send to Coder) when `IN_PROGRESS` and `retry_count <= MAX_RETRIES`, so the function never returns `None`.
- Fix variable shadowing in `nodes.py` lines 25–28: `git_tools = git_tools(...)` overwrites the imported factory. Rename local variables (e.g., `bound_git_tools`).
- Fix tools list in `nodes.py` line 29: `[git_tools, workspace_tools, github_tools]` is a list of lists. Flatten with `[*git_tools, *workspace_tools, *github_tools]` or `git_tools + workspace_tools + github_tools`.
- Implement Coder, Test Runner, Evaluator, and PR Writer node functions using the `SKILL.md` prompts as a guide.
- Pass `execution_mode` flags into the node context (either inject them into the initial messages or include them in the system prompt at node invocation time).
- Initialize `messages` and `retry_count` in the initial state in `cli.py`.

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
| `BaseFileSystemTools` interface | ✅ | `read_files`, `write_files`, `find_files`, `list_dir` |
| `types.py` (`FileSystemResult` / `FileOpStatus`) | ✅ | Defined and imported in `cli.py` |
| `PATHLIBPythonManager` | ✅ | Concrete impl via `pathlib` |

### Necessary steps
- Add unit tests per adapter method / `FileOpStatus` branch.

### 2.3 Platform / GitHub (`adapters/platform/`)

| Piece | Status | Notes |
| --- | --- | --- |
| `BaseGitHubClient` interface | ✅ | `get_issue`, `create_pull_request`, `get_default_branch`, `post_issue_comment` |
| `types.py` (`GitHubClientResult` / `GitHubOpStatus`) | ✅ | Defined and imported in `cli.py` |
| `PyGithubManager` | ✅ | Concrete impl via PyGithub; all four operations implemented |

### Necessary steps
- Fix `cli.py` GitHub init check: `github_manager` can be `None` (no token), so the `github_manager.status` access will raise `AttributeError`. Guard with `if github_manager is not None and ...`.
- Fix `cli.py` type annotations: `git_manager: GitResult` and `workspace_manager: FileSystemResult` should be `BaseGitRepo` and `BaseFileSystemTools` respectively.
- Add unit tests for each `GitHubOpStatus` branch.

---

## 3. Tools (`tools/`)

| Tool module | Status | Notes |
| --- | --- | --- |
| `git_tools.py` factory | ✅ | 8 tools: `list_local_branches`, `checkout_branch`, `stage_patch_and_commit`, `push`, `pull`, `git_grep`, `git_status`, `git_fallback` |
| `github_tools.py` factory | ✅ | 4 tools: `get_issue`, `create_pull_request`, `get_default_branch`, `post_issue_comment` |
| `workspace_tools.py` factory | ✅ | 4 tools: `read_files`, `write_files`, `find_files`, `list_dir` |

### Necessary steps
- Fix `github_tools.py` `post_issue_comment`: the function incorrectly declares `self` as its first parameter; remove it.
- Fix `github_tools.py` template name: `get_issue` tool calls `load_response_tempate(..., tool_name="get_issues")` (plural) but the file is `get_issue.md` (singular).
- Bind the correct tool subsets to each node (currently all nodes receive all tools; tighten per the `SKILL.md` tool-reference tables).
- Add tool-layer tests asserting the correct template renders per `GitOpStatus`.

---

## 4. Skills & Response Templates (`skills/`)

| Piece | Status | Notes |
| --- | --- | --- |
| `SKILL.md` prompts (all nodes) | ✅ | Planner, Coder, Evaluator, Test Runner, PR Writer |
| `prompt_loader.py` | ✅ | Loads `SKILL.md` for a given node name |
| `template_loader.py` | ✅ | Extracts a `##` section by `GitOpStatus` / `FileOpStatus` / `GitHubOpStatus` value |
| Planner response templates | ✅ | `branch_checkout`, `grep_repo`, `status`, `local_branches`, `list_dir`, `find_files`, `read_files`, `get_issue` |
| PR Writer response templates | ✅ | `commit`, `push`, `pull`, `fallback`, `create_pull_request`, `get_default_branch`, `post_issue_comment` |
| Coder response templates | 🟡 | `write_files` only |
| Evaluator response templates | ⬜ | None — Evaluator is primarily a reasoning node |
| Test Runner response templates | ⬜ | None yet |

### Necessary steps
- Verify every `GitOpStatus`, `FileOpStatus`, and `GitHubOpStatus` value has a matching `##` section in the relevant template file.
- Add any missing Coder templates (e.g., for `read_files` and `find_files` when called from the Coder).
- Consider adding Evaluator/Test Runner templates if those nodes grow tool use.
- Fix `constants.py` typo: `IN_PROGESS = "IN_PROGRESS"` — the enum member key is misspelled (`IN_PROGESS` vs `IN_PROGRESS`). Update all references.

---

## 5. CLI (`cli.py`)

| Piece | Status | Notes |
| --- | --- | --- |
| Typer `run` command + options | ✅ | `--path`, `--new-branch`, `--pr/--no-pr`, `--local-only` |
| `repo_name` argument | ✅ | Required positional argument added |
| Target resolution (issue number vs. prose) | ✅ | |
| Repo root discovery | ✅ | |
| Manager wiring (Git, Filesystem, GitHub) | ✅ | All three adapters instantiated and injected via `config["configurable"]` |
| `execution_mode` flags in config | ✅ | `auto_pr`, `new_branch`, `local_only`, `is_remote_issue` |
| Initial state construction | 🟡 | Missing `messages`, `retry_count`, `relevant_files`, and other required `State` fields |
| Graph invocation | ✅ | Builds `RunnableConfig` and calls `app.invoke` |

### Necessary steps
- Add missing initial state fields: `messages=[]`, `retry_count=0`, `relevant_files=[]`, `fix_plan=None`, `patch_code=None`, `test_output=None`.
- Fix `issue_description` initialization: it is set to `None` for remote issues, but `State` does not mark it `Optional`.
- Fix the `github_manager` status check (see §2.3 above).
- Fix the type annotations for `git_manager` and `workspace_manager`.

---

## 6. Testing

| Piece | Status | Notes |
| --- | --- | --- |
| Template unit tests (from LangGraph starter) | 🟡 | Configuration/graph tests still reference the template |
| Subprocess git exploration scripts | 🟡 | Scratch scripts under `tests/subprocess_git_tests/` |
| Adapter unit tests | ⬜ | |
| Tool-layer tests | ⬜ | |
| End-to-end graph run | ⬜ | Blocked until node functions are implemented and a shell-execution tool exists |

### Necessary steps
- Add unit tests per adapter method / status branch.
- Add tool-layer tests asserting the correct template renders per status.
- Implement a shell-execution tool (or use `subprocess` in the Test Runner node directly) so the Test Runner can actually run `pytest` / `npm test` / etc.
- Stand up an end-to-end run against a throwaway repo once node functions are implemented.

---

## Near-term priority order

1. Fix the bugs in `nodes.py` (variable shadowing, tools list flattening) and `cli.py` (missing state fields, type annotations, GitHub init guard).
2. Fix `constants.py` typo (`IN_PROGESS`).
3. Fix `github_tools.py` bugs (`self` param, `get_issues` template name).
4. Implement the remaining **node functions** (Coder, Test Runner, Evaluator, PR Writer) using the `SKILL.md` prompts.
5. Implement a **shell-execution tool** so the Test Runner can run actual test commands.
6. Decide on / implement `GitPythonManager` (or drop it).
7. Backfill **tests** (adapter, tool-layer, end-to-end).
