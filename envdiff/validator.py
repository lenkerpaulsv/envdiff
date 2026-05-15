"""Validation utilities for .env file keys and values."""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# POSIX-compliant env var name: starts with letter or underscore, followed by
# letters, digits, or underscores.
_VALID_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


@dataclass
class ValidationIssue:
    key: str
    message: str
    line_number: Optional[int] = None

    def __str__(self) -> str:
        loc = f" (line {self.line_number})" if self.line_number is not None else ""
        return f"[{self.key}]{loc} {self.message}"


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.issues) == 0

    def add(self, key: str, message: str, line_number: Optional[int] = None) -> None:
        self.issues.append(ValidationIssue(key=key, message=message, line_number=line_number))

    def __str__(self) -> str:
        if self.is_valid:
            return "No validation issues found."
        lines = [f"{len(self.issues)} issue(s) found:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


def validate_keys(env: Dict[str, str]) -> ValidationResult:
    """Validate that all keys in a parsed env dict are POSIX-compliant."""
    result = ValidationResult()
    for key in env:
        if not _VALID_KEY_RE.match(key):
            result.add(key, f"Key '{key}' is not a valid POSIX environment variable name.")
        if key != key.upper():
            result.add(key, f"Key '{key}' contains lowercase letters; consider uppercasing.")
    return result


def validate_no_empty_values(env: Dict[str, str]) -> ValidationResult:
    """Warn about keys that have empty string values."""
    result = ValidationResult()
    for key, value in env.items():
        if value == "":
            result.add(key, f"Key '{key}' has an empty value.")
    return result


def validate_env(env: Dict[str, str]) -> ValidationResult:
    """Run all validations and return a combined ValidationResult."""
    combined = ValidationResult()
    for check in (validate_keys, validate_no_empty_values):
        sub = check(env)
        combined.issues.extend(sub.issues)
    return combined
