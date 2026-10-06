# ----------------------------------
#  Prompt Loader Utility
# ----------------------------------

from pathlib import Path


def load_skill_prompt(node_name: str) -> str:
    """Retrieves the SKILL.md prompt for node, with given name node_name"""
    file_path = Path(__file__).resolve().parent.parent / "skills" / node_name / "SKILL.md"

    if not file_path.exists():
        # Fallback to working directory relative path
        file_path = Path(f"src/skills/{node_name}/SKILL.md")

    if not file_path.exists():
        return "{raw_results}"

    return file_path.read_text(encoding="utf-8")
