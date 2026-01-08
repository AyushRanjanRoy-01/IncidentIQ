"""Shared state for agent communication.

Provides a unified state object that all agents write to and read from.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class AgentState:
    """Shared state object for all agents."""
    
    incident_id: str
    alert_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Context information
    relevant_logs: List[str] = field(default_factory=list)
    recent_metrics: Dict[str, Any] = field(default_factory=dict)
    recent_deployments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Analysis results
    triage_result: Optional[Dict[str, Any]] = None
    context_data: Optional[Dict[str, Any]] = None
    knowledge_results: List[Dict[str, Any]] = field(default_factory=list)
    rca_result: Optional[Dict[str, Any]] = None
    
    # Recommended actions
    recommended_actions: List[Dict[str, Any]] = field(default_factory=list)
    primary_action: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.0
    
    # Metadata
    agent_logs: Dict[str, List[str]] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def add_log(self, agent_name: str, message: str) -> None:
        """Add a log message from an agent."""
        if agent_name not in self.agent_logs:
            self.agent_logs[agent_name] = []
        self.agent_logs[agent_name].append(message)
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        # TODO: Implement serialization logic
        pass
