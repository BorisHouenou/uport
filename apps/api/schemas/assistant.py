from typing import Literal

from schemas.base import UportaiBase


class AssistantMessage(UportaiBase):
    role: Literal["user", "assistant"]
    content: str


class AssistantChatRequest(UportaiBase):
    messages: list[AssistantMessage]
    agreement_filter: list[str] | None = None  # e.g. ["cusma", "ceta"]
    include_citations: bool = True
