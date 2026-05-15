"""Format EnvDiffResult for human-readable or machine-readable output."""

import json
from envdiff.core import DiffStatus, EnvDiffResult

_STATUS_SYMBOLS = {
    DiffStatus.ADDED: "+",
    DiffStatus.REMOVED: "-",
    DiffStatus.CHANGED: "~",
    DiffStatus.UNCHANGED: " ",
}


def format_text(result: EnvDiffResult, show_unchanged: bool = False) -> str:
    """Return a human-readable diff string."""
    lines = []
    for entry in result.entries:
        if entry.status == DiffStatus.UNCHANGED and not show_unchanged:
            continue
        symbol = _STATUS_SYMBOLS[entry.status]
        if entry.status == DiffStatus.CHANGED:
            lines.append(f"{symbol} {entry.key}: {entry.target_value!r} -> {entry.source_value!r}")
        elif entry.status == DiffStatus.ADDED:
            lines.append(f"{symbol} {entry.key}={entry.source_value!r}")
        elif entry.status == DiffStatus.REMOVED:
            lines.append(f"{symbol} {entry.key}={entry.target_value!r}")
        else:
            lines.append(f"{symbol} {entry.key}={entry.source_value!r}")
    return "\n".join(lines)


def format_summary(result: EnvDiffResult) -> str:
    """Return a one-line summary of the diff."""
    counts = {s: 0 for s in DiffStatus}
    for entry in result.entries:
        counts[entry.status] += 1
    return (
        f"added={counts[DiffStatus.ADDED]} "
        f"removed={counts[DiffStatus.REMOVED]} "
        f"changed={counts[DiffStatus.CHANGED]} "
        f"unchanged={counts[DiffStatus.UNCHANGED]}"
    )


def format_json(result: EnvDiffResult) -> str:
    """Return a JSON representation of the diff."""
    entries = [
        {
            "key": e.key,
            "status": e.status.value,
            "source_value": e.source_value,
            "target_value": e.target_value,
        }
        for e in result.entries
    ]
    return json.dumps({"entries": entries}, indent=2)
