"""Reconcile two .env files by applying diff results."""

from typing import Optional
from envdiff.core import DiffStatus, EnvDiffResult


def reconcile(
    result: EnvDiffResult,
    include_added: bool = True,
    include_removed: bool = False,
    include_changed: bool = True,
    placeholder: Optional[str] = "FILL_ME_IN",
) -> dict:
    """
    Produce a reconciled key-value mapping from a diff result.

    Args:
        result: The EnvDiffResult to reconcile.
        include_added: Include keys present in source but not target.
        include_removed: Include keys present in target but not source.
        include_changed: Include keys whose values differ (uses source value).
        placeholder: Value to assign to added keys when their source value
                     should not be copied verbatim. Set to None to copy the
                     source value directly.

    Returns:
        A dict representing the reconciled environment.
    """
    reconciled = {}

    for entry in result.entries:
        if entry.status == DiffStatus.UNCHANGED:
            reconciled[entry.key] = entry.source_value

        elif entry.status == DiffStatus.ADDED and include_added:
            reconciled[entry.key] = (
                placeholder if placeholder is not None else entry.source_value
            )

        elif entry.status == DiffStatus.REMOVED and include_removed:
            reconciled[entry.key] = entry.target_value

        elif entry.status == DiffStatus.CHANGED and include_changed:
            reconciled[entry.key] = entry.source_value

    return reconciled


def reconciled_to_env_string(mapping: dict) -> str:
    """Serialise a key-value mapping back to .env file format."""
    lines = []
    for key, value in mapping.items():
        if value is None:
            lines.append(f"{key}=")
        elif any(c in str(value) for c in (" ", "\t", "#", "'", '"')):
            escaped = str(value).replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n" if lines else ""
