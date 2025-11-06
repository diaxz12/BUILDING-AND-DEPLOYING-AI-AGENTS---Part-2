"""Lightweight guardrails helpers for the travel planner demo.

Each helper wraps Guardrails AI policies so the FastAPI service can keep the
main endpoint simple and easy to follow for students.
"""

from __future__ import annotations

from typing import Literal

from guardrails import Guard, OnFailAction
from guardrails.hub import QARelevanceLLMEval, SensitiveTopic, ToxicLanguage

PromptStatus = Literal["ok", "blocked", "error"]


def check_user_prompt(prompt: str) -> tuple[PromptStatus, str | None]:
    """Run lightweight safety filters on the incoming user prompt.

    Returns a status plus an optional message that can be surfaced back to the UI.
    """
    if not prompt.strip():
        return "blocked", "Please share a destination or travel idea first."

    guard = Guard().use_many(
        SensitiveTopic(
            sensitive_topics=["extremism", "weapons"],
            disable_classifier=False,
            disable_llm=False,
            on_fail=OnFailAction.EXCEPTION,
        ),
        ToxicLanguage(
            threshold=0.5,
            validation_method="sentence",
            on_fail=OnFailAction.EXCEPTION,
        ),
    )

    try:
        guard.validate(prompt)
        return "ok", None
    except Exception as exc:  # pragma: no cover - guardrails raises custom errors
        return "blocked", f"Prompt rejected by guardrails: {exc}"


def check_agent_answer(prompt: str, answer: str) -> tuple[PromptStatus, str | None]:
    """Ensure the answer stays relevant to the original prompt."""
    guard = Guard().use(
        QARelevanceLLMEval,
        llm_callable="gpt-4o-mini",
        on_fail=OnFailAction.EXCEPTION,
    )

    try:
        guard.validate(
            answer,
            metadata={"original_prompt": prompt},
        )
        return "ok", None
    except Exception as exc:  # pragma: no cover
        return "blocked", f"Response withheld by guardrails: {exc}"
