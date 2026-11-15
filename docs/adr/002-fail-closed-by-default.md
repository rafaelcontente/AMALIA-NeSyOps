# 2. Fail-Closed by Default in the Decision Gate

**Status:** Accepted  
**Date:** 2024-11-15  
**Deciders:** Rafael Contente, Engineering Team  

## Context
In high-stakes administrative environments, the cost of a false positive (e.g., illegally approving a commercial license) is severe legal liability and loss of public trust. The cost of a false negative (e.g., temporarily rejecting a valid application) is an operational inconvenience that can be resolved via human review or appeal.

## Decision
The Decision Gate is designed to **fail-closed**. If any of the following conditions occur, the system will automatically reject the proposal or escalate it to the human maker-checker queue:
- Missing or malformed input data.
- Timeout or Circuit Breaker activation in the LLM adapter.
- Failure to resolve a cited entity in the knowledge graph.
- Any unhandled exception during rule evaluation.

## Consequences
- **Positive:** Maximum safety. The system will never silently approve an invalid request due to a transient failure or edge case.
- **Negative:** Higher rate of human-in-the-loop escalations during system degradation or novel edge cases.
- **Trade-off accepted:** We prioritize legal safety and auditability over raw automation throughput.
