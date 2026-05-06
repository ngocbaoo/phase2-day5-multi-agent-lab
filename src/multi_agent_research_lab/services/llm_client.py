"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from langsmith import traceable

from multi_agent_research_lab.core.config import get_settings


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client skeleton."""

    def __init__(self):
        settings = get_settings()
        self.model = settings.openai_model
        # OpenRouter uses the OpenAI compatible API
        self.client = OpenAI(
            api_key=settings.openai_api_key or "dummy_key",
            base_url=settings.openrouter_base_url,
            default_headers={"HTTP-Referer": "https://localhost", "X-Title": "Multi-Agent Lab"}
        )

    @traceable(run_type="llm", name="LLMClient.complete")
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        content = response.choices[0].message.content or ""
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        # rough estimate for gpt-4o-mini
        cost_usd = (input_tokens * 0.15 / 1000000) + (output_tokens * 0.60 / 1000000)
        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd
        )
