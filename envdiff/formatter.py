"""Formatters for displaying EnvDiffResult output."""

from typing import List
from envdiff.core import DiffStatus, EnvDiffResult, DiffEntry


STATUS_SYMBOLS = {
    DiffStatus.ADDED: "+",
    DiffStatus.REMOVED: "-",
    DiffStatus.MODIFIED: "~",
    DiffStatus.UNCHANGED: " ",
}

STATUS_LABELS = {
    DiffStatus.ADDED: "added",
    DiffStatus.REMOVED: "removed",
    DiffStatus.MODIFIED: "modified",
    DiffStatus.UNCHANGED: "unchanged",
}


def format_text(result: EnvDiffResult, show_unchanged: bool = False) -> str:
    """Format a diff result as a human-readable text block."""
    lines: List[str] = []
    for entry in result.entries:
        if entry.status == DiffStatus.UNCHANGED and not show_unchanged:
            continue
        symbol = STATUS_SYMBOLS[entry.status]
        if entry.status == DiffStatus.MODIFIED:
            lines.append(f"{symbol} {entry.key}: {entry.old_value!r} -> {entry.new_value!r}")
        elif entry.status == DiffStatus.ADDED:
            lines.append(f"{symbol} {entry.key}={entry.new_value!r}")
        elif entry.status == DiffStatus.REMOVED:
            lines.append(f"{symbol} {entry.key}={entry.old_value!r}")
        else:
            lines.append(f"{symbol} {entry.key}={entry.new_value!r}")
    return "\n".join(lines)


def format_summary(result: EnvDiffResult) -> str:
    """Return a one-line summary of the diff result."""
    counts = {
        DiffStatus.ADDED: 0,
        DiffStatus.REMOVED: 0,
        DiffStatus.MODIFIED: 0,
        DiffStatus.UNCHANGED: 0,
    }
    for entry in result.entries:
        counts[entry.status] += 1

    parts = []
    for status in (DiffStatus.ADDED, DiffStatus.REMOVED, DiffStatus.MODIFIED, DiffStatus.UNCHANGED):
        if counts[status] > 0:
            parts.append(f"{counts[status]} {STATUS_LABELS[status]}")
    return ", ".join(parts) if parts else "no differences"


def format_json(result: EnvDiffResult) -> dict:
    """Serialize a diff result to a JSON-compatible dictionary."""
    return {
        "entries": [
            {
                "key": e.key,
                "status": e.status.value,
                "old_value": e.old_value,
                "new_value": e.new_value,
            }
            for e in result.entries
        ],
        "summary": format_summary(result),
    }
