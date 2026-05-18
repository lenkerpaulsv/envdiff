"""Audit .env files for common security and hygiene issues."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from envdiff.core import EnvDiffResult, DiffStatus


class AuditSeverity(str, Enum):
    WARNING = "warning"
    ERROR = "error"


@dataclass
class AuditIssue:
    key: str
    message: str
    severity: AuditSeverity

    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.key}: {self.message}"


@dataclass
class AuditResult:
    issues: List[AuditIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == AuditSeverity.ERROR for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == AuditSeverity.WARNING for i in self.issues)

    def add(self, issue: AuditIssue) -> None:
        self.issues.append(issue)

    def __len__(self) -> int:
        return len(self.issues)


_SENSITIVE_PATTERNS = ("secret", "password", "passwd", "token", "key", "api", "auth", "private")
_PLACEHOLDER_PATTERNS = ("changeme", "todo", "fixme", "placeholder", "your_", "<", ">", "xxx")


def _looks_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(p in lower for p in _SENSITIVE_PATTERNS)


def _looks_like_placeholder(value: str) -> bool:
    lower = value.lower()
    return any(p in lower for p in _PLACEHOLDER_PATTERNS)


def audit(result: EnvDiffResult) -> AuditResult:
    """Run audit checks against an EnvDiffResult."""
    audit_result = AuditResult()

    for entry in result.entries:
        value = entry.staging_value or entry.production_value or ""

        if entry.status == DiffStatus.ADDED and _looks_sensitive(entry.key):
            audit_result.add(AuditIssue(
                key=entry.key,
                message="Sensitive key present in staging but missing in production.",
                severity=AuditSeverity.WARNING,
            ))

        if entry.status == DiffStatus.REMOVED and _looks_sensitive(entry.key):
            audit_result.add(AuditIssue(
                key=entry.key,
                message="Sensitive key present in production but missing in staging.",
                severity=AuditSeverity.WARNING,
            ))

        if _looks_sensitive(entry.key) and _looks_like_placeholder(value):
            audit_result.add(AuditIssue(
                key=entry.key,
                message=f"Sensitive key appears to have a placeholder value: {value!r}.",
                severity=AuditSeverity.ERROR,
            ))

        if entry.key == entry.key.lower() and entry.key.replace("_", "").isalpha():
            audit_result.add(AuditIssue(
                key=entry.key,
                message="Key is not uppercase; convention recommends UPPER_SNAKE_CASE.",
                severity=AuditSeverity.WARNING,
            ))

    return audit_result
