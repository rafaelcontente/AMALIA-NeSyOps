# 1. Separate Proposal from Decision (Neuro-Symbolic Architecture)

**Status:** Accepted  
**Date:** 2024-11-15  
**Deciders:** Rafael Contente, Engineering Team  

## Context
Public administrations want to use LLMs to accelerate decision-making (e.g., licensing, subsidies). However, LLMs are inherently non-deterministic, prone to hallucination, and vulnerable to prompt injection. Regulatory frameworks (like the EU AI Act) require high-risk administrative decisions to be explainable, traceable, and strictly rule-compliant.

## Decision
We adopted a strict **Neuro-Symbolic** architecture where the LLM is restricted to a "proposer" role only. 
- The LLM may draft a decision and claim evidence.
- A deterministic, 5-layer validation Gate independently evaluates the proposal against formal AST-safe rules and a cited RDF knowledge graph.
- **Only the Gate can release a final verdict.** There is no code path from the LLM adapter to the audit ledger without passing the Gate.

## Consequences
- **Positive:** Eliminates LLM hallucination in final decisions. Guarantees 100% rule compliance. Provides a mathematically verifiable audit trail.
- **Negative:** Adds latency to the pipeline. Requires maintaining a formal, versioned rule registry instead of relying purely on prompt engineering.
- **Trade-off accepted:** We sacrifice the "end-to-end neural" simplicity for absolute regulatory compliance and safety.
