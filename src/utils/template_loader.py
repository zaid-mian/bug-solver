# -----------------------------------
#  Template Loader Utility
# -----------------------------------

from pathlib import Path


def load_response_tempate(skill: str, tool_name: str, section: str) -> str:
    """Reads a response template markdown file and extracts a specific ## section."""
    file_path = (
        Path(__file__).resolve().parent.parent
        / "skills"
        / skill
        / "responses"
        / f"{tool_name}.md"
    )

    if not file_path.exists():
        # Fallback to working directory relative path
        file_path = Path(f"src/skills/{skill}/responses/{tool_name}.md")

    if not file_path.exists():
        # Fallback if markdown file doesn't exist yet
        return "{raw_data}\n{error_details}"

    # get content
    content = file_path.read_text(encoding="utf-8")

    # split markdown by '## ' headers
    sections = {}
    current_section = None
    lines = content.splitlines()

    for line in lines:
        if line.startswith("## "):
            # start of new section
            current_section = line.replace("## ", "").strip().lower()
            sections[current_section] = []
        elif current_section:
            # add to the current_section
            sections[current_section].append(line)

    # retrieve the section template/response prompt (case-insensitive)
    normalized_section = section.strip().lower()
    if normalized_section in sections:
        return "\n".join(sections[normalized_section]).strip()

    # Fallback if specific section is missing
    return "{raw_data}\n{error_details}"


# Alias for proper spelling
load_response_template = load_response_tempate
