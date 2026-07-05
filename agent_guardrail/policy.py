"""Policy definitions: scope + pattern matching for agent actions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class Scope(str, Enum):
    """What happens when a policy matches a proposed action."""

    READ_ONLY = "read_only"  # informational; never blocks on its own
    REQUIRES_CONFIRMATION = "requires_confirmation"  # escalate to human
    BLOCKED = "blocked"  # hard deny


class Verdict(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"


@dataclass
class Policy:
    """A single safety policy: match risky actions via regex/keyword patterns."""

    name: str
    scope: Scope
    patterns: list[str]
    description: str = ""

    def matches(self, action: dict[str, Any]) -> bool:
        """Return True if any pattern hits the action's combined text."""
        haystack = " ".join(
            str(action.get(k, "")) for k in ("action_type", "target", "payload", "agent_reasoning")
        ).lower()
        return any(re.search(p, haystack, re.IGNORECASE) for p in self.patterns)


def default_job_agent_policies() -> list[Policy]:
    """Pre-built policies for an autonomous job-application agent demo."""
    return [
        Policy(
            name="read_operations",
            scope=Scope.READ_ONLY,
            patterns=[r"\bread\b", r"browse", r"search", r"view", r"scrape"],
            description="Passive information gathering",
        ),
        Policy(
            name="fabricated_credentials",
            scope=Scope.BLOCKED,
            patterns=[r"fabricat", r"false\s+experience", r"fake\s+resume", r"lie\s+about"],
            description="Block applications built on dishonest claims",
        ),
        Policy(
            name="high_stakes_actions",
            scope=Scope.BLOCKED,
            patterns=[r"purchase", r"transfer_funds", r"delete", r"send_email"],
            description="Block irreversible or financial side-effects",
        ),
        Policy(
            name="submit_application",
            scope=Scope.REQUIRES_CONFIRMATION,
            patterns=[r"submit_application", r"submit\s+application", r"apply\s+to"],
            description="Application submissions need human approval",
        ),
    ]
