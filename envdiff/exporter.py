"""Export EnvDiffResult to various file formats (dotenv, JSON, YAML)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from envdiff.core import EnvDiffResult


def export_dotenv(result: "EnvDiffResult", include_removed: bool = False) -> str:
    """Export the diff result as a .env file string.

    By default only keys present in the *production* (right) side are
    included.  Pass ``include_removed=True`` to also emit keys that only
    exist on the staging (left) side, commented out.
    """
    lines: list[str] = []
    for entry in result.entries:
        from envdiff.core import DiffStatus

        if entry.status == DiffStatus.REMOVED:
            if include_removed:
                lines.append(f"# REMOVED: {entry.key}={entry.left_value}")
        elif entry.status == DiffStatus.ADDED:
            lines.append(f"{entry.key}={entry.right_value}")
        elif entry.status == DiffStatus.CHANGED:
            lines.append(f"{entry.key}={entry.right_value}")
        else:  # UNCHANGED
            lines.append(f"{entry.key}={entry.right_value}")
    return "\n".join(lines)


def export_json(result: "EnvDiffResult") -> str:
    """Export the diff result as a JSON string."""
    payload = {
        "summary": {
            "added": result.added_count,
            "removed": result.removed_count,
            "changed": result.changed_count,
            "unchanged": result.unchanged_count,
        },
        "entries": [
            {
                "key": e.key,
                "status": e.status.value,
                "left_value": e.left_value,
                "right_value": e.right_value,
            }
            for e in result.entries
        ],
    }
    return json.dumps(payload, indent=2)


def export_yaml(result: "EnvDiffResult") -> str:
    """Export the diff result as a minimal YAML string (no third-party deps)."""
    lines: list[str] = []
    lines.append("summary:")
    lines.append(f"  added: {result.added_count}")
    lines.append(f"  removed: {result.removed_count}")
    lines.append(f"  changed: {result.changed_count}")
    lines.append(f"  unchanged: {result.unchanged_count}")
    lines.append("entries:")
    for e in result.entries:
        lines.append(f"  - key: {e.key}")
        lines.append(f"    status: {e.status.value}")
        lv = e.left_value if e.left_value is not None else ""
        rv = e.right_value if e.right_value is not None else ""
        lines.append(f"    left_value: {lv}")
        lines.append(f"    right_value: {rv}")
    return "\n".join(lines)
