# Agent Workflows Documentation

## Multi-Agent System Architecture

The platform uses a supervisor pattern with specialized agents working in parallel.

## Agent Types

### Supervisor Agent
- Orchestrates all specialist agents
- Coordinates parallel execution
- Aggregates results
- Determines confidence scores

### Triage Agent
- Filters noise from alerts
- Checks for duplicate alerts
- Prioritizes alerts by severity
- Groups related alerts

### Context Builder Agent
- Gathers logs from Loki
- Retrieves metrics from Prometheus
- Fetches traces from OpenTelemetry
- Collects recent deployment events

### Knowledge Agent
- Searches runbooks via RAG
- Retrieves relevant post-mortems
- Finds similar historical incidents
- Provides resolution recommendations

### RCA Agent
- Synthesizes all gathered data
- Generates root cause hypothesis
- Calculates confidence score
- Provides evidence and recommendations

## Workflow Sequence

1. **Alert Triggered**
   - Alert received from monitoring system
   - Supervisor agent initialized

2. **Parallel Agent Execution**
   - Triage agent filters and prioritizes
   - Context agent gathers data
   - Knowledge agent searches runbooks
   - All agents execute in parallel

3. **Result Aggregation**
   - Supervisor collects all agent outputs
   - Results combined into unified state
   - Confidence scores calculated

4. **RCA Generation**
   - RCA agent synthesizes findings
   - Root cause hypothesis generated
   - Evidence and recommendations provided

5. **Remediation Suggestion**
   - Remediation actions suggested
   - Confidence threshold checked
   - Approval workflow triggered if needed

6. **Action Execution**
   - Human approval (if required)
   - Remediation action executed
   - Results monitored and logged

## State Management

All agents write to a shared state object:
- Alert information
- Gathered context (logs, metrics, traces)
- Knowledge base results
- RCA findings
- Remediation suggestions

## Confidence Scoring

Confidence calculated based on:
- Agent agreement
- Evidence quality
- Historical success rate
- Data completeness
