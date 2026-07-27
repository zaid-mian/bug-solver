# -----------------------------------
#  Template Loader Utility
# -----------------------------------

from pathlib import Path


def load_response_tempate(skill: str, tool_name: str, section: str) -> str:
    """Reads a response template markdown file and extracts a specific ## section."""
    file_path = Path(f"src/skills/{skill}/responses/{tool_name}.md")

    if not file_path.exists():
        # Fallback if markdown file doesn't exist yet
        return "{raw_results}"

    # get content
    content = file_path.read_text()

    # split markdown by '## ' headers
    sections = {}
    current_section = None
    lines = content.splitlines()

    for line in lines:
        if line.startswith("## "):
            # start of new section
            current_section = line.replace("## ", "").strip()
            sections[current_section] = []
        elif current_section:
            # add to the current_section
            sections[current_section].append(line)

    # retrieve the section template/response prompt
    if section in sections:
        return "\n".join(sections[section]).strip()

    # else raise an error since the section is not found in the md
    raise ValueError(f"Section '## {section}' not found in {file_path}")
