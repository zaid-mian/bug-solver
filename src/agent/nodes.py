import json

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import ToolNode

from .graph import State

# from .graph import Context

from utils.prompt_loader import load_skill_prompt
from tools.git_tools import git_tools
from tools.workspace_tools import workspace_tools
from tools.github_tools import github_tools


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
    return "Placeholder"


# ----------------------------
#  Test Runner Node Function
# ----------------------------
async def test_runner(state: State, config: RunnableConfig):
    return "Placeholder"


# ---------------------------
#  Coder Evaluator Function
# ---------------------------
async def evaluator(state: State, config: RunnableConfig):
    return "Placeholder"


# ---------------------------
#  Coder PR Writer Function
# ---------------------------
async def pr_writer(state: State, config: RunnableConfig):
    return "Placeholder"
