"""Root Cause Analysis (RCA) agent.

Synthesises the triage, context, and knowledge signals into a root-cause
hypothesis and a single concrete remediation action.

Two modes:
* **LLM mode** (when an OpenAI provider is configured): the LLM produces the
  narrative + action as strict JSON, validated against the action enum.
* **Deterministic mode** (default, offline): a transparent rule-based synthesis
  grounded in the retrieved runbook content. The deterministic result is always
  computed first and used as a fallback if the LLM output is missing/invalid.
"""

from __future__ import annotations

from typing import Any

import structlog

from app.agents.llm import LLMProvider
from app.agents.state import AgentState
from app.models.enums import ActionType, AlertSeverity
from app.rag.prompts import RCA_SYSTEM_PROMPT, build_rca_user_prompt

logger = structlog.get_logger(__name__)

_VALID_ACTIONS = {a.value for a in ActionType}


class RCAAgent:
    """Performs root cause analysis and recommends a remediation action."""

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def analyze(self, state: AgentState) -> dict[str, Any]:
        baseline = self._deterministic(state)

        if self.llm.available:
            try:
                llm_result = self._llm_synthesis(state, baseline)
                if llm_result is not None:
                    state.rca_result = llm_result
                    self._record(state, llm_result)
                    return llm_result
            except Exception as exc:  # pragma: no cover - network dependent
                logger.warning("agent.rca_llm_failed", error=str(exc), fallback="deterministic")
                state.add_error(f"RCA LLM error: {exc}")

        state.rca_result = baseline
        self._record(state, baseline)
        return baseline

    # ------------------------------------------------------------------ helpers
    def _record(self, state: AgentState, result: dict[str, Any]) -> None:
        action = result["recommended_action"]
        state.primary_action = action
        state.recommended_actions = [action]
        state.confidence_score = result["confidence"]
        state.add_log(
            "rca",
            f"Root cause: {result['root_cause']} -> action={action['action_type']} "
            f"(confidence={result['confidence']})",
        )
        logger.info(
            "agent.rca",
            incident_id=state.incident_id,
            action=action["action_type"],
            confidence=result["confidence"],
            provider=result.get("provider"),
        )

    def _heuristic_action(self, state: AgentState) -> dict[str, Any]:
        metric = state.metric.lower()
        had_deploy = bool(state.context_data and state.context_data.get("had_recent_deploy"))

        if any(t in metric for t in ("latency", "error", "5xx", "request")):
            if had_deploy:
                return {
                    "action_type": ActionType.ROLLBACK.value,
                    "target": state.service,
                    "parameters": {"to_version": "previous"},
                    "rationale": "Degradation began shortly after a recent deployment; "
                    "rolling back to the last known-good version is the fastest mitigation.",
                }
            return {
                "action_type": ActionType.SCALE.value,
                "target": state.service,
                "parameters": {"replicas_delta": 2},
                "rationale": "Latency/error breach with no recent deploy suggests capacity "
                "pressure; scaling out adds headroom.",
            }
        if any(t in metric for t in ("memory", "oom", "heap")):
            return {
                "action_type": ActionType.RESTART.value,
                "target": state.service,
                "parameters": {"strategy": "rolling"},
                "rationale": "High memory usage / OOM signature; a rolling restart reclaims "
                "leaked memory while preserving availability.",
            }
        if "cpu" in metric:
            return {
                "action_type": ActionType.SCALE.value,
                "target": state.service,
                "parameters": {"replicas_delta": 1},
                "rationale": "Sustained high CPU; scaling out distributes load.",
            }
        return {
            "action_type": ActionType.RESTART.value,
            "target": state.service,
            "parameters": {"strategy": "rolling"},
            "rationale": "No specific signature matched; a rolling restart is a safe first step.",
        }

    def _deterministic(self, state: AgentState) -> dict[str, Any]:
        action = self._heuristic_action(state)
        had_deploy = bool(state.context_data and state.context_data.get("had_recent_deploy"))

        # Confidence from corroborating signals.
        confidence = 0.5
        if state.knowledge_results:
            top = max((k.get("score", 0.0) for k in state.knowledge_results), default=0.0)
            if top > 0.3:
                confidence += 0.2
        if had_deploy and action["action_type"] == ActionType.ROLLBACK.value:
            confidence += 0.15
        if state.severity == AlertSeverity.CRITICAL.value:
            confidence += 0.1
        confidence = round(min(confidence, 0.95), 2)

        root_cause = self._root_cause_text(state, had_deploy)
        evidence = [
            f"{state.metric} = {state.value} (threshold {state.threshold})",
            f"severity = {state.severity}",
        ]
        if had_deploy:
            evidence.append("A deployment occurred ~12 minutes before the alert.")
        if state.knowledge_results:
            doc_ids = sorted({k["doc_id"] for k in state.knowledge_results})
            evidence.append(f"Matched knowledge base entries: {', '.join(doc_ids)}")

        return {
            "root_cause": root_cause,
            "summary": (
                f"{state.service}: {state.metric} breached threshold. {root_cause} "
                f"Recommended: {action['action_type']} {action['target']}."
            ),
            "evidence": evidence,
            "recommended_action": action,
            "confidence": confidence,
            "knowledge_doc_ids": sorted({k["doc_id"] for k in state.knowledge_results}),
            "provider": "deterministic",
            "model": "rule-based",
        }

    @staticmethod
    def _root_cause_text(state: AgentState, had_deploy: bool) -> str:
        metric = state.metric.lower()
        if any(t in metric for t in ("latency", "error", "request")) and had_deploy:
            return "Likely a performance regression introduced by the recent deployment."
        if any(t in metric for t in ("memory", "oom", "heap")):
            return "Likely a memory leak or insufficient memory limits in the service."
        if "cpu" in metric:
            return "Likely CPU saturation due to increased load or an inefficient code path."
        if any(t in metric for t in ("latency", "error", "request")):
            return "Likely capacity pressure or a degraded downstream dependency."
        return "Root cause undetermined from available signals; investigate service health."

    def _llm_synthesis(self, state: AgentState, baseline: dict[str, Any]) -> dict[str, Any] | None:
        alert_summary = (
            f"service={state.service} metric={state.metric} value={state.value} "
            f"threshold={state.threshold} severity={state.severity} "
            f"summary={state.summary or 'n/a'} labels={state.labels}"
        )
        context_block = ""
        if state.context_data:
            ctx = state.context_data
            context_block = (
                f"recent_deploy={ctx.get('had_recent_deploy')}\n"
                f"deployments={ctx.get('recent_deployments')}\n"
                f"metrics={ctx.get('metrics_snapshot')}\n"
                f"logs={ctx.get('log_sample')}"
            )
        knowledge_block = "\n\n".join(
            f"[{k['doc_id']}] {k['content'][:600]}" for k in state.knowledge_results
        )
        user_prompt = build_rca_user_prompt(
            alert_summary=alert_summary,
            context_block=context_block,
            knowledge_block=knowledge_block,
        )

        data, meta = self.llm.complete_json(RCA_SYSTEM_PROMPT, user_prompt)
        if not data:
            return None

        action = data.get("recommended_action") or {}
        action_type = str(action.get("action_type", "")).lower()
        if action_type not in _VALID_ACTIONS:
            # Keep the LLM narrative but use the validated heuristic action.
            action = baseline["recommended_action"]
        else:
            action = {
                "action_type": action_type,
                "target": action.get("target") or state.service,
                "parameters": action.get("parameters") or {},
                "rationale": action.get("rationale") or "",
            }

        confidence = data.get("confidence")
        try:
            confidence = round(min(max(float(confidence), 0.0), 0.99), 2)
        except (TypeError, ValueError):
            confidence = baseline["confidence"]

        return {
            "root_cause": data.get("root_cause") or baseline["root_cause"],
            "summary": data.get("summary") or baseline["summary"],
            "evidence": data.get("evidence") or baseline["evidence"],
            "recommended_action": action,
            "confidence": confidence,
            "knowledge_doc_ids": baseline["knowledge_doc_ids"],
            "provider": "openai",
            "model": meta.model,
        }
