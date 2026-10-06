/**
 * BugSolver Web DAG Visualizer & Stateflow Simulator
 */

document.addEventListener("DOMContentLoaded", () => {
  // Nodes data model
  const NODES_DATA = {
    "planner": {
      name: "Planner Node",
      icon: "🧠",
      type: "LangGraph Worker Node",
      color: "cyan",
      desc: "Responsible for analyzing the repository, identifying root cause of the bug report, and formulating an ordered, minimal fix plan. Does not write code directly.",
      channels: ["messages (read/write)", "relevant_files (write)", "fix_plan (write)"],
      tools: [
        "read_files(file_paths) — Inspect workspace sources",
        "find_files(text_pattern) — Fast grep across codebase",
        "list_dir(dir, recursive) — Map repository structure",
        "git_grep(pattern) — Ripgrep across git index"
      ],
      prompt: `# Planner System Prompt
Analyze the bug description, read the relevant files, formulate the root cause,
and construct a minimal, non-invasive fix plan. Do NOT implement the code yourself.`
    },
    "coder": {
      name: "Coder Node",
      icon: "💻",
      type: "LangGraph Worker Node",
      color: "yellow",
      desc: "Implements the Planner's fix plan methodically. Reads source files, synthesizes minimal code edits, and applies surgical patches to the workspace.",
      channels: ["fix_plan (read)", "relevant_files (read)", "patch_code (write)", "messages (read/write)"],
      tools: [
        "patch_file(file_path, old_str, new_str) — Surgical search & replace",
        "write_files(file_paths_and_edits) — Full file rewrite",
        "read_files(file_paths) — Source review before editing",
        "git_status() — Inspect modified files"
      ],
      prompt: `# Coder System Prompt
Implement the fix described in the Planner's fix plan. Apply the smallest correct
change that resolves the bug. Preserve existing code style and formatting.`
    },
    "testrunner": {
      name: "Test Runner Node",
      icon: "🧪",
      type: "LangGraph Worker Node",
      color: "magenta",
      desc: "Executes the test suite inside an isolated subprocess sandbox. Scoped strictly to the target repository so test commands never escape into agent host workspace.",
      channels: ["repo_path (read)", "test_output (write)", "messages (read/write)"],
      tools: [
        "run_tests(test_files) — Executes pytest in isolated subprocess sandbox"
      ],
      prompt: `# Test Runner System Prompt
Execute the repository test suite to observe test outcomes following code modifications.
Return exact stdout/stderr for Evaluator assessment.`
    },
    "evaluator": {
      name: "Evaluator Node",
      icon: "⚖️",
      type: "LangGraph Decision Node",
      color: "green",
      desc: "Interprets test output and makes the routing decision. Verdicts: 0 -> PR Writer (SUCCESS), 1 -> Coder (RETRY if <= 3 attempts), 2 -> Planner (EXHAUSTED re-plan).",
      channels: ["test_output (read)", "status (write)", "retry_count (read/write)"],
      tools: [
        "read_files(file_paths) — Post-execution inspection",
        "git_status() — Verify workspace state"
      ],
      prompt: `# Evaluator System Prompt
Analyze the test output. If all tests pass, output {"status": "SUCCESS"}.
If any test failed, diagnose the failure and increment retry_count.`
    },
    "prwriter": {
      name: "PR Writer Node",
      icon: "🚀",
      type: "LangGraph Worker Node",
      color: "blue",
      desc: "Finalizes the verified patch. Creates dedicated fix branch (e.g. bugsolver/fix-142), commits surgical changes, pushes to remote, and opens GitHub Pull Request.",
      channels: ["patch_code (read)", "fix_plan (read)", "status (write)"],
      tools: [
        "stage_patch_and_commit(message) — Git commit patch",
        "push(branch_name) — Push to remote repository",
        "create_pull_request(title, body) — Open GitHub PR"
      ],
      prompt: `# PR Writer System Prompt
Commit the verified fix with a descriptive conventional commit message.
Open a clean GitHub Pull Request referencing the original issue.`
    }
  };

  // DOM Elements
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");
  const svgNodes = document.querySelectorAll(".graph-node");
  const btnSimulate = document.getElementById("btn-simulate");
  const btnReset = document.getElementById("btn-reset");
  const btnExport = document.getElementById("btn-export");
  const feedBody = document.getElementById("feed-body");
  const feedStatus = document.getElementById("feed-status");

  // Inspector Elements
  const inspectorIcon = document.getElementById("node-inspector-icon");
  const inspectorName = document.getElementById("node-inspector-name");
  const inspectorType = document.getElementById("node-inspector-type");
  const inspectorDesc = document.getElementById("node-inspector-desc");
  const inspectorChannels = document.getElementById("node-channels");
  const inspectorTools = document.getElementById("node-tools");
  const inspectorPrompt = document.getElementById("node-prompt-snippet");

  // Tab switching
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      tabButtons.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`tab-${targetTab}`).classList.add("active");
    });
  });

  function switchTab(tabId) {
    tabButtons.forEach(b => b.classList.toggle("active", b.getAttribute("data-tab") === tabId));
    tabContents.forEach(c => c.classList.toggle("active", c.id === `tab-${tabId}`));
  }

  // Update Inspector with Node Data
  function selectNode(nodeKey) {
    const data = NODES_DATA[nodeKey];
    if (!data) return;

    inspectorIcon.textContent = data.icon;
    inspectorName.textContent = data.name;
    inspectorType.textContent = data.type;
    inspectorDesc.textContent = data.desc;

    // Channels
    inspectorChannels.innerHTML = "";
    data.channels.forEach(ch => {
      const span = document.createElement("span");
      span.className = "tag tag-cyan";
      span.textContent = ch;
      inspectorChannels.appendChild(span);
    });

    // Tools
    inspectorTools.innerHTML = "";
    data.tools.forEach(t => {
      const li = document.createElement("li");
      const parts = t.split(" — ");
      li.innerHTML = `<code>${parts[0]}</code> — ${parts[1] || ""}`;
      inspectorTools.appendChild(li);
    });

    // Prompt
    inspectorPrompt.textContent = data.prompt;
    switchTab("node-details");
  }

  // Node Click Handlers
  svgNodes.forEach(node => {
    node.addEventListener("click", () => {
      const id = node.id.replace("node-", "");
      if (NODES_DATA[id]) {
        svgNodes.forEach(n => n.classList.remove("active-node"));
        node.classList.add("active-node");
        selectNode(id);
      }
    });
  });

  // Logging utility
  function addLog(msg, type = "normal") {
    const now = new Date();
    const timeStr = now.toTimeString().split(" ")[0];
    const entry = document.createElement("div");
    entry.className = `log-entry ${type}`;
    entry.innerHTML = `<span class="log-time">${timeStr}</span><span class="log-msg">${msg}</span>`;
    feedBody.appendChild(entry);
    feedBody.scrollTop = feedBody.scrollHeight;
  }

  // Highlight Edge & Node
  function highlightStep(nodeId, edgeId) {
    svgNodes.forEach(n => n.classList.remove("active-node"));
    document.querySelectorAll(".edge-path").forEach(e => e.classList.remove("active"));

    if (nodeId) {
      const el = document.getElementById(nodeId);
      if (el) el.classList.add("active-node");
    }
    if (edgeId) {
      const el = document.getElementById(edgeId);
      if (el) el.classList.add("active");
    }
  }

  // Simulation Sequence
  let isSimulating = false;
  async function runSimulation() {
    if (isSimulating) return;
    isSimulating = true;
    btnSimulate.disabled = true;
    feedStatus.textContent = "Running SWE-bench Repair Loop...";

    addLog("⚡ Starting Autonomous Bug Solver execution on benchmarks/fixtures/null_guard", "system");

    // 1. START -> Planner
    highlightStep("node-planner", "edge-start-planner");
    selectNode("planner");
    addLog("[Planner] Loading skills and analyzing bug: 'TypeError on None in parse_and_sum'", "node-log");
    await sleep(1500);

    // 2. Planner -> Coder
    highlightStep("node-coder", "edge-planner-coder");
    selectNode("coder");
    addLog("[Coder] Reviewing plan. Synthesizing surgical patch with patch_file()...", "node-log");
    await sleep(1500);
    switchTab("diff-viewer");
    addLog("[Coder] Patch applied: 'if v is not None: total += v' inserted in src/calculator.py", "node-log");
    await sleep(1800);

    // 3. Coder -> Test Runner
    highlightStep("node-testrunner", "edge-coder-tester");
    selectNode("testrunner");
    switchTab("test-terminal");
    addLog("[Test Runner] Spawning SubprocessPytestManager sandbox...", "node-log");
    await sleep(1500);
    addLog("[Test Runner] Output: 2 passed in 0.08s (100% test pass rate)", "success");
    await sleep(1400);

    // 4. Test Runner -> Evaluator
    highlightStep("node-evaluator", "edge-tester-evaluator");
    selectNode("evaluator");
    addLog("[Evaluator] Inspecting sandbox test outcomes. Route evaluation triggered.", "node-log");
    await sleep(1300);
    addLog("[Evaluator] Verdict: SUCCESS (Condition 0 triggered -> route to PR Writer)", "success");
    await sleep(1400);

    // 5. Evaluator -> PR Writer
    highlightStep("node-prwriter", "edge-eval-pr");
    selectNode("prwriter");
    addLog("[PR Writer] Checking out branch 'bugsolver/fix-null-guard-171800'...", "node-log");
    await sleep(1200);
    addLog("[PR Writer] Staged patch & committed: 'fix(calc): guard against NoneType in sum'", "node-log");
    addLog("[PR Writer] Simulated GitHub Pull Request #42 opened successfully!", "success");
    await sleep(1200);

    // 6. PR Writer -> END
    highlightStep("node-end", "edge-pr-end");
    addLog("🏁 Autonomous Repair Loop Completed with Status: SUCCESS", "success");
    feedStatus.textContent = "Finished (SUCCESS)";

    isSimulating = false;
    btnSimulate.disabled = false;
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  btnSimulate.addEventListener("click", runSimulation);

  btnReset.addEventListener("click", () => {
    svgNodes.forEach(n => n.classList.remove("active-node"));
    document.querySelectorAll(".edge-path").forEach(e => e.classList.remove("active"));
    feedBody.innerHTML = `
      <div class="log-entry system">
        <span class="log-time">00:00:00</span>
        <span class="log-msg">Simulation reset. Ready for new execution.</span>
      </div>
    `;
    feedStatus.textContent = "Ready";
    selectNode("planner");
  });

  btnExport.addEventListener("click", () => {
    const schema = {
      name: "BugSolver LangGraph Architecture",
      version: "0.1.0",
      entry_point: "START",
      end_point: "END",
      nodes: Object.keys(NODES_DATA).map(k => ({
        id: k,
        name: NODES_DATA[k].name,
        type: NODES_DATA[k].type,
        channels: NODES_DATA[k].channels,
        tools: NODES_DATA[k].tools
      })),
      conditional_edges: [
        { from: "evaluator", router: "check_status", routes: { 0: "prwriter", 1: "coder", 2: "planner" } }
      ]
    };
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(schema, null, 2));
    const dl = document.createElement("a");
    dl.setAttribute("href", dataStr);
    dl.setAttribute("download", "bugsolver_graph_schema.json");
    dl.click();
  });
});
