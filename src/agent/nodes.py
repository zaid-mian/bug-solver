import json

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import ToolNode

from .state import State

# from .graph import Context

from utils.prompt_loader import load_skill_prompt
from tools.git_tools import git_tools
from tools.workspace_tools import workspace_tools
from tools.github_tools import github_tools
from tools.testing_tools import testing_tools


# ------------------------
#  Planner Node Function
# ------------------------
async def planner(state: State, config: RunnableConfig):
    """Worker node responsible for analyzing and fixing bugs in code."""

    # 1. Dynamically load the skill prompt from src/skills/planner/SKILL.md
    system_prompt_text = load_skill_prompt("planner")

    # 2. Get bound tools for this specific domain node
    adapters = config["configurable"]["adapters"]
    bound_git_tools = git_tools(adapters["git_manager"])
    bound_workspace_tools = workspace_tools(adapters["workspace_manager"])
    bound_github_tools = github_tools(adapters["github_manager"])

    tools = bound_git_tools + bound_workspace_tools + bound_github_tools

    # extract tools by name for the ReACT loop
    tools_by_name = {t.name: t for t in tools}

    # 3. Bind tools to model and invoke with system prompt + conversation history
    llm_with_tools = config["configurable"]["model"].bind_tools(tools)

    # seed the conversation
    messages = [SystemMessage(content=system_prompt_text), *state["messages"]]

    # -----------------------
    #  ReACT loop
    # -----------------------
    while True:
        response = await llm_with_tools.ainvoke(messages)

        messages.append(response)

        if not response.tool_calls:
            break  # The LLM is done calling tools (no tool_calls)

        for tool_call in response.tool_calls:
            result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])
            messages.append(
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            )

    # Then extract the structured state from the final message (or a follow-up call)
    content = response.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    final_data = json.loads(content.strip())

    return {
        "relevant_files": final_data["relevant_files"],
        "fix_plan": final_data["fix_plan"],
        "messages": messages,
    }


# ----------------------
#  Coder Node Function
# ----------------------
async def coder(state: State, config: RunnableConfig):
    """Coder node responsible for acting on the fix plan and coding the fixes."""

    # 1. Dynamically load the skill prompt from src/skills/coder/SKILL.md
    system_prompt_text = load_skill_prompt("coder")

    # 2. Get bound tools for this specific domain node
    adapters = config["configurable"]["adapters"]
    bound_git_tools = git_tools(adapters["git_manager"])
    bound_workspace_tools = workspace_tools(adapters["workspace_manager"])
    bound_github_tools = github_tools(adapters["github_manager"])

    tools = bound_git_tools + bound_workspace_tools + bound_github_tools

    # extract tools by name for the ReACT loop
    tools_by_name = {t.name: t for t in tools}

    # 3. Bind tools to model and invoke with system prompt + conversation history
    llm_with_tools = config["configurable"]["model"].bind_tools(tools)

    # seed the conversation
    messages = [SystemMessage(content=system_prompt_text), *state["messages"]]

    # -----------------------
    #  ReACT loop
    # -----------------------
    while True:
        response = await llm_with_tools.ainvoke(messages)

        messages.append(response)

        if not response.tool_calls:
            break  # The LLM is done calling tools (no tool_calls)

        for tool_call in response.tool_calls:
            result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])
            messages.append(
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            )

    # Then extract the structured state from the final message (or a follow-up call)
    content = response.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    final_data = json.loads(content.strip())

    return {
        "patch_code": final_data["patch_code"],
        "messages": messages,
    }


# ----------------------------
#  Test Runner Node Function
# ----------------------------
async def test_runner(state: State, config: RunnableConfig):
    """Test Runner node: discovers the test setup, executes the tests
    against the Coder's patch, and records the full output."""

    # 1. Dynamically load the skill prompt from src/skills/test_runner/SKILL.md
    system_prompt_text = load_skill_prompt("test_runner")

    # 2. Get bound tools for this specific domain node
    adapters = config["configurable"]["adapters"]
    bound_testing_tools = testing_tools(adapters["test_manager"])
    bound_workspace_tools = workspace_tools(adapters["workspace_manager"])
    bound_git_tools = git_tools(adapters["git_manager"])

    tools = bound_testing_tools + bound_workspace_tools + bound_git_tools

    # extract tools by name for the ReACT loop
    tools_by_name = {t.name: t for t in tools}

    # 3. Bind tools to model and invoke with system prompt + conversation history
    llm_with_tools = config["configurable"]["model"].bind_tools(tools)

    # seed the conversation with runtime context the prompt expects
    context_seed = (
        f"repo_path: {state.get('repo_path')}\n"
        f"patch_code: {state.get('patch_code')}\n"
        f"relevant_files: {state.get('relevant_files')}\n"
    )
    messages = [
        SystemMessage(content=system_prompt_text + "\n\n" + context_seed),
        *state["messages"],
    ]

    # -----------------------
    #  ReACT loop
    # -----------------------
    while True:
        response = await llm_with_tools.ainvoke(messages)

        messages.append(response)

        if not response.tool_calls:
            break  # The LLM is done calling tools (no tool_calls)

        for tool_call in response.tool_calls:
            result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])
            messages.append(
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            )

    # Then extract the structured state from the final message (or a follow-up call)
    content = response.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    final_data = json.loads(content.strip())

    return {
        "test_output": final_data["test_output"],
        "messages": messages,
    }


# ---------------------------
#  Evaluator Node Function
# ---------------------------
async def evaluator(state: State, config: RunnableConfig):
    """Evaluator node: interprets the test output and decides the next step.

    Sets status to SUCCESS (route to PR Writer) or FAILED (route back to the
    Coder with a diagnostic). Bumps retry_count on failure so the graph can
    re-plan once MAX_RETRIES is exhausted.
    """

    # 1. Dynamically load the skill prompt from src/skills/evaluator/SKILL.md
    system_prompt_text = load_skill_prompt("evaluator")

    # 2. Get bound tools for this specific domain node (read-only inspection)
    adapters = config["configurable"]["adapters"]
    bound_workspace_tools = workspace_tools(adapters["workspace_manager"])
    bound_git_tools = git_tools(adapters["git_manager"])

    tools = bound_workspace_tools + bound_git_tools

    # extract tools by name for the ReACT loop
    tools_by_name = {t.name: t for t in tools}

    # 3. Bind tools to model and invoke with system prompt + conversation history
    llm_with_tools = config["configurable"]["model"].bind_tools(tools)

    # seed the conversation with runtime context the prompt expects
    context_seed = (
        f"test_output: {state.get('test_output')}\n"
        f"patch_code: {state.get('patch_code')}\n"
        f"fix_plan: {state.get('fix_plan')}\n"
        f"retry_count: {state.get('retry_count')}\n"
    )
    messages = [
        SystemMessage(content=system_prompt_text + "\n\n" + context_seed),
        *state["messages"],
    ]

    # -----------------------
    #  ReACT loop
    # -----------------------
    # The model may emit a diagnostic message before its final JSON verdict;
    # everything it says stays in the history for the Coder's next attempt.
    verdict = None
    while True:
        response = await llm_with_tools.ainvoke(messages)

        messages.append(response)

        if response.tool_calls:
            for tool_call in response.tool_calls:
                result = await tools_by_name[tool_call["name"]].ainvoke(
                    tool_call["args"]
                )
                messages.append(
                    ToolMessage(content=str(result), tool_call_id=tool_call["id"])
                )
            continue

        # No tool calls: try to parse a verdict, otherwise keep listening
        # (the model may be writing its diagnostic first).
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        try:
            verdict = json.loads(content.strip())
            if isinstance(verdict, dict) and "status" in verdict:
                break
        except (json.JSONDecodeError, AttributeError, IndexError):
            pass

        # Not a verdict yet — nudge it to conclude.
        messages.append(
            SystemMessage(
                content=(
                    "You have given your analysis. Now emit your final verdict as "
                    "a single raw JSON object: "
                    '{"status": "SUCCESS" or "FAILED", "retry_count": <int>}.'
                )
            )
        )

    status = verdict["status"]
    retry_count = int(verdict.get("retry_count", state.get("retry_count", 0)))
    if status == "FAILED" and retry_count <= state.get("retry_count", 0):
        # guarantee forward progress on the retry counter
        retry_count = state.get("retry_count", 0) + 1

    return {
        "status": status,
        "retry_count": retry_count,
        "messages": messages,
    }


# ---------------------------
#  PR Writer Node Function
# ---------------------------
async def pr_writer(state: State, config: RunnableConfig):
    """PR Writer node: commits the verified fix, pushes the fix branch, and
    opens a Pull Request (unless running in local-only mode)."""

    # 1. Dynamically load the skill prompt from src/skills/pr_writer/SKILL.md
    system_prompt_text = load_skill_prompt("pr_writer")

    # 2. Get bound tools for this specific domain node
    adapters = config["configurable"]["adapters"]
    bound_git_tools = git_tools(adapters["git_manager"])
    tools = bound_git_tools

    github_manager = adapters.get("github_manager")
    if github_manager is not None:
        bound_github_tools = github_tools(github_manager)
        tools = tools + bound_github_tools

    # extract tools by name for the ReACT loop
    tools_by_name = {t.name: t for t in tools}

    # 3. Bind tools to model and invoke with system prompt + conversation history
    llm_with_tools = config["configurable"]["model"].bind_tools(tools)

    # seed the conversation with runtime context the prompt expects
    execution_mode = config["configurable"].get("execution_mode", {})
    context_seed = (
        f"relevant_files: {state.get('relevant_files')}\n"
        f"patch_code: {state.get('patch_code')}\n"
        f"fix_plan: {state.get('fix_plan')}\n"
        f"issue_id: {state.get('issue_id')}\n"
        f"repo_name: {state.get('repo_name')}\n"
        f"execution_mode.local_only: {execution_mode.get('local_only')}\n"
        f"execution_mode.auto_pr: {execution_mode.get('auto_pr')}\n"
        f"github_available: {github_manager is not None}\n"
    )
    if github_manager is None:
        context_seed += (
            "\nNOTE: No GitHub client is configured (missing GITHUB_TOKEN). "
            "Commit the fix locally and skip push / pull-request / issue-comment steps.\n"
        )
    messages = [
        SystemMessage(content=system_prompt_text + "\n\n" + context_seed),
        *state["messages"],
    ]

    # -----------------------
    #  ReACT loop
    # -----------------------
    while True:
        response = await llm_with_tools.ainvoke(messages)

        messages.append(response)

        if not response.tool_calls:
            break  # The LLM is done calling tools (no tool_calls)

        for tool_call in response.tool_calls:
            result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])
            messages.append(
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            )

    # Then extract the structured state from the final message (or a follow-up call)
    content = response.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    final_data = json.loads(content.strip())

    return {
        "status": final_data["status"],
        "messages": messages,
    }
