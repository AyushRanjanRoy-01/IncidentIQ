"""LLM prompts for RAG and the multi-agent RCA pipeline."""

from __future__ import annotations

SUPERVISOR_SYSTEM_PROMPT = (
    "You are the supervisor of an AI Site Reliability Engineering team. You "
    "coordinate triage, context-gathering, knowledge-retrieval, and root-cause "
    "analysis agents to resolve production incidents quickly and safely."
)

TRIAGE_SYSTEM_PROMPT = (
    "You are a triage agent. You filter noise, deduplicate alerts, and assess "
    "whether an alert is actionable and how urgent it is."
)

RCA_SYSTEM_PROMPT = (
    "You are a senior SRE performing root-cause analysis. Using the alert, the "
    "gathered context, and the retrieved runbooks/postmortems, produce a precise, "
    "evidence-based root cause and a single concrete remediation action.\n\n"
    "Respond with STRICT JSON only, matching this schema:\n"
    "{\n"
    '  "root_cause": "one or two sentence hypothesis",\n'
    '  "summary": "short human-readable RCA summary",\n'
    '  "evidence": ["bullet", "points", "citing the context/runbooks"],\n'
    '  "recommended_action": {\n'
    '     "action_type": "restart|scale|rollback|terraform_apply|noop",\n'
    '     "target": "the service or resource to act on",\n'
    '     "parameters": {"key": "value"},\n'
    '     "rationale": "why this action addresses the root cause"\n'
    "  },\n"
    '  "confidence": 0.0\n'
    "}\n"
    "Do not include any prose outside the JSON object."
)


def build_rca_user_prompt(*, alert_summary: str, context_block: str, knowledge_block: str) -> str:
    """Assemble the user prompt fed to the RCA LLM call."""
    return (
        "## Incident alert\n"
        f"{alert_summary}\n\n"
        "## Gathered context\n"
        f"{context_block or 'No additional context available.'}\n\n"
        "## Retrieved knowledge (runbooks / postmortems)\n"
        f"{knowledge_block or 'No relevant knowledge base entries found.'}\n\n"
        "Analyse the above and return the RCA JSON."
    )


RAG_CONTEXT_PROMPT = (
    "Given the following context documents, answer the question concisely and cite "
    "the relevant runbook sections.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"
)
