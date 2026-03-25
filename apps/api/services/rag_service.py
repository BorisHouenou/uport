"""RAG compliance assistant service — delegates to packages/ai-agents/rag_assistant."""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages/ai-agents"))

from rag_assistant import stream_compliance_answer, get_chat_history, save_chat_turn  # noqa: F401

__all__ = ["stream_compliance_answer", "get_chat_history", "save_chat_turn"]
