"""Core logic for parsing, diffing, and reconciling .env files."""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple


class DiffStatus(Enum):
    """Status of a key when comparing two .env files."""
    ADDED = "added"         # Present in target but not in source
    REMOVED = "removed"     # Present in source but not in target
    CHANGED = "changed"     # Present in both but with different values
    UNCHANGED = "unchanged" # Present in both with identical values


@dataclass
class DiffEntry:
    """Represents a single key's diff result between two .env files."""
    key: str
    status: DiffStatus
    source_value: Optional[str] = None
    target_value: Optional[str] = None

    def __repr__(self) -> str:
        return f"DiffEntry(key={self.key!r}, status={self.status.value})"


@dataclass
class EnvDiffResult:
    """Aggregated result of diffing two .env files."""
    source_path: str
    target_path: str
    entries: list = field(default_factory=list)

    @property
    def added(self):
        return [e for e in self.entries if e.status == DiffStatus.ADDED]

    @property
    def removed(self):
        return [e for e in self.entries if e.status == DiffStatus.REMOVED]

    @property
    def changed(self):
        return [e for e in self.entries if e.status == DiffStatus.CHANGED]

    @property
    def unchanged(self):
        return [e for e in self.entries if e.status == DiffStatus.UNCHANGED]

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def parse_env_file(path: str) -> Dict[str, str]:
    """Parse a .env file into a dictionary of key-value pairs.

    Handles:
    - Comments (lines starting with #)
    - Blank lines
    - Quoted values (single and double quotes)
    - Inline comments after values

    Args:
        path: Filesystem path to the .env file.

    Returns:
        A dict mapping environment variable names to their string values.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If a line is malformed and cannot be parsed.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"env file not found: {path}")

    env: Dict[str, str] = {}

    with open(path, "r", encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()

            # Skip blank lines and comments
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                raise ValueError(
                    f"Malformed line {lineno} in {path!r}: {raw_line!r}"
                )

            key, _, value = line.partition("=")
            key = key.strip()

            # Strip inline comments (only outside quotes)
            value = _strip_inline_comment(value.strip())

            # Strip surrounding quotes
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]

            env[key] = value

    return env


def _strip_inline_comment(value: str) -> str:
    """Remove trailing inline comment from a value string, respecting quotes."""
    in_quote: Optional[str] = None
    for i, ch in enumerate(value):
        if ch in ('"', "'") and in_quote is None:
            in_quote = ch
        elif ch == in_quote:
            in_quote = None
        elif ch == "#" and in_quote is None:
            return value[:i].rstrip()
    return value


def diff_envs(source_path: str, target_path: str) -> EnvDiffResult:
    """Diff two .env files and return a structured result.

    Args:
        source_path: Path to the source (e.g. staging) .env file.
        target_path: Path to the target (e.g. production) .env file.

    Returns:
        An EnvDiffResult containing categorised DiffEntry objects.
    """
    source = parse_env_file(source_path)
    target = parse_env_file(target_path)

    all_keys = sorted(set(source) | set(target))
    result = EnvDiffResult(source_path=source_path, target_path=target_path)

    for key in all_keys:
        src_val = source.get(key)
        tgt_val = target.get(key)

        if src_val is None:
            status = DiffStatus.ADDED
        elif tgt_val is None:
            status = DiffStatus.REMOVED
        elif src_val != tgt_val:
            status = DiffStatus.CHANGED
        else:
            status = DiffStatus.UNCHANGED

        result.entries.append(
            DiffEntry(key=key, status=status, source_value=src_val, target_value=tgt_val)
        )

    return result
