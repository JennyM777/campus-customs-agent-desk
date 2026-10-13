"""Single source of truth for which model every Campus Customs agent uses.

Every agent in this project MUST obtain its model via get_model() below.
No agent file may construct an OpenAIChatModel (or any other model) directly,
and no model name other than MODEL_NAME may appear anywhere in this project.
"""

import os

from pydantic_ai.models.openai import OpenAIChatModel, OpenAIChatModelSettings
from pydantic_ai.providers.openai import OpenAIProvider

MODEL_NAME = "gpt-6-luna"
PORTKEY_BASE_URL = "https://api.portkey.ai/v1"


def get_model() -> OpenAIChatModel:
    """Build the one and only model configuration used across all five agents.

    Routes every request through Portkey using PORTKEY_API_KEY, and is hard-pinned
    to MODEL_NAME so that no other model can slip into the system.
    """
    api_key = os.environ.get("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError(
            "PORTKEY_API_KEY is not set. Export it before running any Campus "
            "Customs agent, e.g.: export PORTKEY_API_KEY=sk-..."
        )

    provider = OpenAIProvider(base_url=PORTKEY_BASE_URL, api_key=api_key)
    # gpt-6-luna rejects function/tool calls on /v1/chat/completions whenever a
    # reasoning_effort is set; every agent here relies on tool calls, so this
    # must stay pinned to 'none' rather than the model's inferred default.
    settings = OpenAIChatModelSettings(openai_reasoning_effort="none")
    return OpenAIChatModel(MODEL_NAME, provider=provider, settings=settings)
