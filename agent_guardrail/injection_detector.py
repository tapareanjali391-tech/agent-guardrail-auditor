"""PromptInjectionDetector: quarantine hijack attempts in retrieved context."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


# Patterns that suggest an untrusted document is trying to override agent instructions.
INJECTION_PATTERNS: list[tuple[str, str]] = [
    ("ignore_instructions", r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions"),
    ("new_system_prompt", r"new\s+system\s+prompt"),
    ("role_override", r"you\s+are\s+now\s+(?:a\s+)?(?:admin|root|superuser|unrestricted)"),
    ("authority_claim", r"(?:i\s+am|this\s+is)\s+(?:the\s+)?(?:system|admin|developer)\s+(?:and|,)"),
    ("prompt_leak", r"#{1,3}\s*system\s*:"),
    ("disregard", r"disregard\s+(?:your\s+)?(?:safety|original|prior)\s+(?:rules|instructions)"),
]


@dataclass
class ScanResult:
    """Outcome of scanning a single piece of untrusted content."""

    clean: bool
    flags: list[str] = field(default_factory=list)
    quarantined_content: str | None = None
    sanitized_content: str = ""


class PromptInjectionDetector:
    """Scan tool outputs / scraped pages before they enter the agent context."""

    def __init__(self, patterns: list[tuple[str, str]] | None = None):
        self.patterns = patterns or INJECTION_PATTERNS

    def scan(self, content: str) -> ScanResult:
        flags = [label for label, pat in self.patterns if re.search(pat, content, re.IGNORECASE)]
        if flags:
            return ScanResult(
                clean=False,
                flags=flags,
                quarantined_content=content,
                sanitized_content="[QUARANTINED: suspicious injection patterns detected]",
            )
        return ScanResult(clean=True, sanitized_content=content)

    def filter_context(self, sources: dict[str, str]) -> dict[str, ScanResult]:
        """Scan multiple context sources; return per-source results."""
        return {name: self.scan(text) for name, text in sources.items()}
