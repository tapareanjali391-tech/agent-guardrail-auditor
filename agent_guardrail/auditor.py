"""ActionAuditor: evaluate proposed agent actions against policies."""

from __future__ import annotations

import json
import re
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .policy import Policy, Scope, Verdict


class ActionAuditor:
    """
    Wraps an agent's action loop: every proposed action is audited before execution.
    Decisions are appended to a JSON audit log for post-hoc review.
    """

    def __init__(
        self,
        policies: list[Policy],
        log_path: str = "audit_log.json",
        max_submissions_per_hour: int | None = 3,
    ):
        self.policies = policies
        self.log_path = Path(log_path)
        self.max_submissions_per_hour = max_submissions_per_hour
        self._submission_times: deque[datetime] = deque()

    def audit(self, action: dict[str, Any]) -> tuple[Verdict, str]:
        """Check action against all policies; return verdict and reason."""
        matched = [p for p in self.policies if p.matches(action)]
        verdict, reason = self._resolve(action, matched)

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "verdict": verdict.value,
            "matched_policies": [p.name for p in matched],
            "reason": reason,
        }
        self._append_log(entry)
        return verdict, reason

    def _resolve(
        self, action: dict[str, Any], matched: list[Policy]
    ) -> tuple[Verdict, str]:
        if any(p.scope == Scope.BLOCKED for p in matched):
            names = [p.name for p in matched if p.scope == Scope.BLOCKED]
            return Verdict.BLOCK, f"Blocked by: {', '.join(names)}"

        if self._rate_limit_exceeded(action):
            return Verdict.ESCALATE_TO_HUMAN, "Rate limit: too many submissions this hour"

        if any(p.scope == Scope.REQUIRES_CONFIRMATION for p in matched):
            names = [p.name for p in matched if p.scope == Scope.REQUIRES_CONFIRMATION]
            return Verdict.ESCALATE_TO_HUMAN, f"Requires human approval: {', '.join(names)}"

        return Verdict.ALLOW, "No blocking policies matched"

    def _rate_limit_exceeded(self, action: dict[str, Any]) -> bool:
        """Escalate when submit actions exceed the hourly cap."""
        if self.max_submissions_per_hour is None:
            return False
        text = str(action.get("action_type", "")) + str(action.get("payload", ""))
        if not re.search(r"submit", text, re.IGNORECASE):
            return False

        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - 3600
        while self._submission_times and self._submission_times[0].timestamp() < cutoff:
            self._submission_times.popleft()

        if len(self._submission_times) >= self.max_submissions_per_hour:
            return True
        self._submission_times.append(now)
        return False

    def seed_submissions(self, count: int) -> None:
        """Pre-fill the rate-limit counter (demo/testing helper; no log entries)."""
        now = datetime.now(timezone.utc)
        for _ in range(count):
            self._submission_times.append(now)

    def _append_log(self, entry: dict[str, Any]) -> None:
        records: list[dict] = []
        if self.log_path.exists():
            records = json.loads(self.log_path.read_text(encoding="utf-8"))
        records.append(entry)
        self.log_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
