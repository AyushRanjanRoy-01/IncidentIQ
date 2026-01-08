"""LLM prompts for RAG and agents."""

# System prompts for different agents
SUPERVISOR_SYSTEM_PROMPT = """You are a SRE supervisor agent coordinating incident analysis."""

TRIAGE_SYSTEM_PROMPT = """You are a triage agent responsible for filtering noise and assessing alert actionability."""

RCA_SYSTEM_PROMPT = """You are a root cause analysis expert. Synthesize all available data into a coherent RCA hypothesis."""

# RAG prompts
RAG_CONTEXT_PROMPT = """
Given the following context documents, answer the question concisely.

Context:
{context}

Question: {query}

Answer:
"""

REMEDIATION_PROMPT = """
Based on the root cause analysis, suggest remediation actions.

RCA: {rca}

Suggested actions:
"""
