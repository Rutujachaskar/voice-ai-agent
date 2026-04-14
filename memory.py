"""
memory.py — Session memory for the Voice AI Agent
Maintains a rolling history of actions within the session.
"""

from datetime import datetime


class SessionMemory:
    def __init__(self, max_items: int = 10):
        self._history = []
        self._max = max_items

    def add(self, transcript: str, intent_data: dict, result: dict):
        """Add a new interaction to memory."""

        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "transcript": transcript,
            "intent": intent_data.get("intent", "unknown"),
            "action": result.get("action", ""),
            "success": not bool(result.get("error")),
        }

        self._history.append(entry)

        # Maintain rolling memory
        if len(self._history) > self._max:
            self._history.pop(0)

    def get_context(self) -> str:
        """Return recent actions as context string for LLM."""

        if not self._history:
            return ""

        lines = []

        for i, h in enumerate(self._history[-5:], 1):
            status = "✓" if h["success"] else "✗"
            lines.append(
                f"{i}. [{status}] {h['intent']} → {h['action']} "
                f"(\"{h['transcript'][:50]}...\")"
            )

        return "Recent actions:\n" + "\n".join(lines)

    def get_last(self) -> dict:
        """Return last memory item (useful for future features)."""
        return self._history[-1] if self._history else {}

    def clear(self):
        """Clear session memory."""
        self._history = []

    def get_all(self) -> list:
        """Return full memory history."""
        return list(self._history)