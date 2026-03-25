"""RAG compliance assistant service — delegates to packages/ai-agents/rag_assistant."""
from __future__ import annotations

import sys
import os
from collections.abc import AsyncGenerator

# Allow importing from packages directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages/ai-agents"))

from rag_assistant import stream_compliance_answer, get_chat_history  # noqa: F401

__all__ = ["stream_compliance_answer", "get_chat_history"]
