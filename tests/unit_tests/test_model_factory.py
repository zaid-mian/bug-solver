import os
from unittest.mock import patch

from utils.model_factory import get_model


def test_get_model_defaults_to_ollama():
    with patch.dict(os.environ, {}, clear=True):
        model = get_model()
        assert model.__class__.__name__ == "ChatOllama"


def test_get_model_selects_anthropic_when_requested():
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-dummy"}, clear=True):
        model = get_model(provider="anthropic")
        assert model.__class__.__name__ == "ChatAnthropic"


def test_get_model_selects_openai_when_requested():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-dummy"}, clear=True):
        model = get_model(provider="openai")
        assert model.__class__.__name__ == "ChatOpenAI"
