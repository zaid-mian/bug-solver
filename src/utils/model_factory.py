"""
Model factory supporting multiple LLM providers:
- Ollama (default for local execution)
- Anthropic Claude
- OpenAI / OpenRouter
- Groq
"""

import os
from typing import Any


def get_model(
    provider: str | None = None,
    model_name: str | None = None,
    temperature: float = 0.0,
) -> Any:
    """Instantiate and return a chat model based on provider and environment."""
    provider = (
        provider
        or os.environ.get("BUGSOLVER_PROVIDER")
        or ("anthropic" if os.environ.get("ANTHROPIC_API_KEY") else None)
        or ("openai" if os.environ.get("OPENAI_API_KEY") else None)
        or "ollama"
    ).lower()

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model_name=model_name or os.environ.get("BUGSOLVER_MODEL", "claude-3-5-sonnet-latest"),
            temperature=temperature,
        )

    if provider in {"openai", "openrouter"}:
        from langchain_openai import ChatOpenAI

        base_url = (
            "https://openrouter.ai/api/v1"
            if provider == "openrouter"
            else os.environ.get("OPENAI_BASE_URL")
        )
        return ChatOpenAI(
            model=model_name or os.environ.get("BUGSOLVER_MODEL", "gpt-4o"),
            temperature=temperature,
            base_url=base_url,
        )

    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model_name=model_name or os.environ.get("BUGSOLVER_MODEL", "llama-3.3-70b-versatile"),
            temperature=temperature,
        )

    # Default to local Ollama
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=model_name or os.environ.get("BUGSOLVER_MODEL", "qwen2.5-coder:7b"),
        base_url=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
        temperature=temperature,
    )
