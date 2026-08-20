"""Structured observability and telemetry subsystem for the self-healing scraping lifecycle."""

import asyncio
import json
import os
import threading
import time
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field
from app.config.logging import get_logger

logger = get_logger("REPAIR_OBSERVABILITY")


class RepairSessionTelemetry(BaseModel):
    """Structured telemetry record capturing the complete lifecycle of an autonomous repair attempt."""

    session_id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str
    domain: str
    root_cause: str
    initial_health: float
    final_health: float = 0.0
    improvement: float = 0.0
    attempts_count: int = 0
    candidates_generated: int = 0
    actions_executed: int = 0
    multi_page_evaluated: bool = False
    multi_page_count: int = 0
    confidence_score: float = 0.0
    confidence_level: str = "low"
    accepted: bool = False
    persisted: bool = False
    rejection_reason: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: float = Field(default_factory=time.time)


class RepairObservability:
    """Singleton-like telemetry buffer and JSONL log persistence for self-healing operations."""

    def __init__(self, log_path: str = ".repair_sessions.jsonl"):
        self.log_path = log_path
        self._sessions: list[RepairSessionTelemetry] = []
        self._lock = threading.Lock()

    def record_session(self, session: RepairSessionTelemetry) -> None:
        """Buffer and append a repair session telemetry event without blocking event loop."""
        with self._lock:
            self._sessions.append(session)
            # Keep in-memory buffer bounded to last 200 sessions
            if len(self._sessions) > 200:
                self._sessions = self._sessions[-200:]

        def _append_to_file():
            try:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(session.model_dump_json() + "\n")
            except Exception as e:
                logger.debug(f"Could not append session telemetry to file: {e}")

        # Offload file append to background thread or execute safely
        try:
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, _append_to_file)
        except RuntimeError:
            _append_to_file()

        logger.debug(
            f"Logged repair telemetry: session={session.session_id[:8]}, "
            f"domain={session.domain}, accepted={session.accepted}, "
            f"health={session.initial_health:.2f}->{session.final_health:.2f}, "
            f"confidence={session.confidence_level}"
        )

    def load_all_persisted_sessions(self, limit: Optional[int] = None) -> list[RepairSessionTelemetry]:
        """Read and parse persisted repair sessions from JSONL log with optional tail limit."""
        if not os.path.exists(self.log_path):
            return []

        loaded: list[RepairSessionTelemetry] = []
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if limit and len(lines) > limit:
                    lines = lines[-limit:]
                for line in lines:
                    line_str = line.strip()
                    if line_str:
                        try:
                            loaded.append(RepairSessionTelemetry.model_validate_json(line_str))
                        except Exception as parse_err:
                            logger.debug(f"Skipping malformed telemetry record: {parse_err}")
        except Exception as e:
            logger.warning(f"Error reading telemetry log from '{self.log_path}': {e}")

        with self._lock:
            if loaded and not self._sessions:
                self._sessions = loaded[-200:]

        return loaded

    def get_recent_sessions(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return the most recent repair sessions using bounded tail scan."""
        with self._lock:
            if self._sessions:
                return [s.model_dump() for s in self._sessions[-limit:]]
        
        tail = self.load_all_persisted_sessions(limit=limit)
        return [s.model_dump() for s in tail[-limit:]]

    def get_summary(self) -> dict[str, Any]:
        """Aggregate statistical summary across all observed repair sessions."""
        with self._lock:
            if not self._sessions and os.path.exists(self.log_path):
                self.load_all_persisted_sessions()
            sessions = self._sessions

            total = len(sessions)
            if total == 0:
                return {"total_sessions": 0, "success_rate": 0.0}

            accepted = sum(1 for s in sessions if s.accepted)
            persisted = sum(1 for s in sessions if s.persisted)
            avg_duration = sum(s.duration_ms for s in sessions) / total
            avg_improvement = sum(s.improvement for s in sessions) / total

            return {
                "total_sessions": total,
                "accepted_count": accepted,
                "success_rate": round(accepted / total, 3),
                "persisted_count": persisted,
                "avg_duration_ms": round(avg_duration, 1),
                "avg_improvement": round(avg_improvement, 3),
            }

    def get_comprehensive_metrics(self) -> dict[str, Any]:
        """Aggregate multi-dimensional statistical metrics across all persisted sessions."""
        sessions = self.load_all_persisted_sessions()
        total = len(sessions)
        if total == 0:
            return {
                "total_sessions": 0,
                "accepted_count": 0,
                "success_rate": 0.0,
                "persisted_count": 0,
                "avg_duration_ms": 0.0,
                "avg_improvement": 0.0,
                "root_causes": {},
                "domain_stats": {},
                "confidence_distribution": {},
                "multi_page_stats": {"evaluated": 0, "accepted": 0},
            }

        accepted_count = sum(1 for s in sessions if s.accepted)
        persisted_count = sum(1 for s in sessions if s.persisted)
        avg_duration = sum(s.duration_ms for s in sessions) / total
        avg_improvement = sum(s.improvement for s in sessions) / total
        avg_initial_health = sum(s.initial_health for s in sessions) / total
        avg_final_health = sum(s.final_health for s in sessions) / total

        # Root causes breakdown
        root_causes: Dict[str, Dict[str, Any]] = {}
        for s in sessions:
            rc = s.root_cause
            if rc not in root_causes:
                root_causes[rc] = {"total": 0, "accepted": 0, "total_improvement": 0.0}
            root_causes[rc]["total"] += 1
            if s.accepted:
                root_causes[rc]["accepted"] += 1
            root_causes[rc]["total_improvement"] += s.improvement

        for rc, data in root_causes.items():
            data["success_rate"] = round(data["accepted"] / data["total"], 3) if data["total"] > 0 else 0.0
            data["avg_improvement"] = round(data["total_improvement"] / data["total"], 3) if data["total"] > 0 else 0.0

        # Domain breakdown
        domain_stats: Dict[str, Dict[str, Any]] = {}
        for s in sessions:
            d = s.domain
            if d not in domain_stats:
                domain_stats[d] = {"total": 0, "accepted": 0, "total_improvement": 0.0}
            domain_stats[d]["total"] += 1
            if s.accepted:
                domain_stats[d]["accepted"] += 1
            domain_stats[d]["total_improvement"] += s.improvement

        for d, data in domain_stats.items():
            data["success_rate"] = round(data["accepted"] / data["total"], 3) if data["total"] > 0 else 0.0
            data["avg_improvement"] = round(data["total_improvement"] / data["total"], 3) if data["total"] > 0 else 0.0

        # Confidence distribution
        confidence_distribution: Dict[str, int] = {}
        for s in sessions:
            c = s.confidence_level
            confidence_distribution[c] = confidence_distribution.get(c, 0) + 1

        # Multi-page stats
        mp_evaluated = sum(1 for s in sessions if s.multi_page_evaluated)
        mp_accepted = sum(1 for s in sessions if s.multi_page_evaluated and s.accepted)

        return {
            "total_sessions": total,
            "accepted_count": accepted_count,
            "success_rate": round(accepted_count / total, 3),
            "persisted_count": persisted_count,
            "avg_duration_ms": round(avg_duration, 1),
            "avg_initial_health": round(avg_initial_health, 3),
            "avg_final_health": round(avg_final_health, 3),
            "avg_improvement": round(avg_improvement, 3),
            "root_causes": root_causes,
            "domain_stats": domain_stats,
            "confidence_distribution": confidence_distribution,
            "multi_page_stats": {
                "evaluated": mp_evaluated,
                "accepted": mp_accepted,
                "pass_rate": round(mp_accepted / mp_evaluated, 3) if mp_evaluated > 0 else 1.0,
            },
        }

    def generate_dashboard_markdown(self) -> str:
        """Generate a GitHub Markdown formatted telemetry dashboard report."""
        metrics = self.get_comprehensive_metrics()
        total = metrics["total_sessions"]

        lines = [
            "# Self-Healing Scraping Telemetry Dashboard",
            "",
            "## Lifetime Operational Overview",
            f"- **Total Repair Sessions:** `{total}`",
            f"- **Repairs Accepted:** `{metrics['accepted_count']}` ({metrics['success_rate'] * 100:.1f}%)",
            f"- **Memory Persisted:** `{metrics['persisted_count']}`",
            f"- **Average Health Delta:** `{metrics.get('avg_initial_health', 0.0):.2f} -> {metrics.get('avg_final_health', 0.0):.2f}` (+{metrics.get('avg_improvement', 0.0):.2f})",
            f"- **Average Repair Latency:** `{metrics['avg_duration_ms']} ms`",
            "",
            "## Root Cause Breakdown",
            "| Root Cause | Total Incidents | Accepted | Success Rate | Avg Health Improvement |",
            "| :--- | :---: | :---: | :---: | :---: |",
        ]

        for rc, data in sorted(metrics.get("root_causes", {}).items(), key=lambda x: x[1]["total"], reverse=True):
            lines.append(f"| `{rc}` | {data['total']} | {data['accepted']} | {data['success_rate']*100:.1f}% | +{data['avg_improvement']:.2f} |")

        lines.extend([
            "",
            "## Domain Performance",
            "| Domain | Total Attempts | Accepted | Success Rate | Avg Health Gain |",
            "| :--- | :---: | :---: | :---: | :---: |",
        ])

        for d, data in sorted(metrics.get("domain_stats", {}).items(), key=lambda x: x[1]["total"], reverse=True):
            lines.append(f"| `{d}` | {data['total']} | {data['accepted']} | {data['success_rate']*100:.1f}% | +{data['avg_improvement']:.2f} |")

        lines.extend([
            "",
            "## Multi-Page Consistency Validation",
            f"- **Multi-Page Evaluated Sessions:** `{metrics['multi_page_stats']['evaluated']}`",
            f"- **Multi-Page Accepted:** `{metrics['multi_page_stats']['accepted']}` ({metrics['multi_page_stats']['pass_rate']*100:.1f}%)",
            "",
            "## Confidence Distribution",
        ])
        for conf, count in metrics.get("confidence_distribution", {}).items():
            lines.append(f"- **{conf.upper()} Tier:** `{count}` sessions")

        return "\n".join(lines)

    def generate_dashboard_html(self, output_file: Optional[str] = None) -> str:
        """Generate a modern HTML dashboard with visual cards, progress bars, and metrics tables."""
        metrics = self.get_comprehensive_metrics()
        total = metrics["total_sessions"]
        success_pct = round(metrics["success_rate"] * 100, 1)

        rc_rows = "".join([
            f"<tr><td><code>{rc}</code></td><td>{d['total']}</td><td>{d['accepted']}</td>"
            f"<td><div class='progress-bar'><div class='fill' style='width:{d['success_rate']*100}%'></div></div>{d['success_rate']*100:.1f}%</td>"
            f"<td class='gain'>+{d['avg_improvement']:.2f}</td></tr>"
            for rc, d in sorted(metrics.get("root_causes", {}).items(), key=lambda x: x[1]["total"], reverse=True)
        ])

        domain_rows = "".join([
            f"<tr><td><strong>{d}</strong></td><td>{data['total']}</td><td>{data['accepted']}</td>"
            f"<td>{data['success_rate']*100:.1f}%</td><td class='gain'>+{data['avg_improvement']:.2f}</td></tr>"
            for d, data in sorted(metrics.get("domain_stats", {}).items(), key=lambda x: x[1]["total"], reverse=True)
        ])

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Self-Healing Scraping Telemetry Dashboard</title>
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --border: #334155;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #38bdf8;
            --success: #4ade80;
            --warning: #fbbf24;
            --danger: #f87171;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 24px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ margin-bottom: 24px; }}
        h1 {{ font-size: 28px; font-weight: 700; color: var(--primary); margin: 0 0 8px 0; }}
        .subtitle {{ color: var(--text-muted); font-size: 14px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 18px; }}
        .card-title {{ font-size: 13px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }}
        .card-value {{ font-size: 26px; font-weight: 700; color: var(--text); }}
        .card-value.highlight {{ color: var(--success); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 14px; }}
        th, td {{ padding: 12px 14px; text-align: left; border-bottom: 1px solid var(--border); }}
        th {{ background: rgba(0,0,0,0.2); color: var(--text-muted); font-weight: 600; }}
        tr:hover {{ background: rgba(255,255,255,0.02); }}
        .progress-bar {{ width: 80px; height: 8px; background: var(--border); border-radius: 4px; display: inline-block; margin-right: 8px; vertical-align: middle; }}
        .fill {{ height: 100%; background: var(--success); border-radius: 4px; }}
        .gain {{ color: var(--success); font-weight: 600; }}
        code {{ background: rgba(255,255,255,0.08); padding: 3px 6px; border-radius: 4px; font-family: monospace; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Self-Healing Scraping Telemetry Dashboard</h1>
            <div class="subtitle">Real-time autonomous resilience metrics, diagnostic breakdowns, and multi-page validation stats.</div>
        </header>

        <div class="grid">
            <div class="card">
                <div class="card-title">Total Repair Sessions</div>
                <div class="card-value">{total}</div>
            </div>
            <div class="card">
                <div class="card-title">Acceptance Rate</div>
                <div class="card-value highlight">{success_pct}%</div>
            </div>
            <div class="card">
                <div class="card-title">Avg Health Gain</div>
                <div class="card-value highlight">+{metrics.get('avg_improvement', 0.0):.2f}</div>
            </div>
            <div class="card">
                <div class="card-title">Avg Repair Latency</div>
                <div class="card-value">{metrics['avg_duration_ms']} ms</div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 24px;">
            <h2>Root Cause Diagnostic Distribution</h2>
            <table>
                <thead>
                    <tr><th>Root Cause</th><th>Total Incidents</th><th>Accepted</th><th>Success Rate</th><th>Avg Health Improvement</th></tr>
                </thead>
                <tbody>
                    {rc_rows if rc_rows else "<tr><td colspan='5'>No root cause events recorded yet.</td></tr>"}
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>Domain Resilience Performance</h2>
            <table>
                <thead>
                    <tr><th>Domain</th><th>Attempts</th><th>Accepted</th><th>Success Rate</th><th>Avg Health Gain</th></tr>
                </thead>
                <tbody>
                    {domain_rows if domain_rows else "<tr><td colspan='5'>No domain sessions recorded yet.</td></tr>"}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>"""
        if output_file:
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info(f"Dashboard HTML exported to '{output_file}'")
            except Exception as e:
                logger.warning(f"Could not export HTML to '{output_file}': {e}")

        return html_content


if __name__ == "__main__":
    import sys
    obs = RepairObservability()
    if "--html" in sys.argv:
        out_path = "repair_dashboard.html"
        obs.generate_dashboard_html(output_file=out_path)
        print(f"Generated HTML dashboard: {out_path}")
    else:
        print(obs.generate_dashboard_markdown())
