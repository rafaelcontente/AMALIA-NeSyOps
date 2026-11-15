# AMALIA-NeSyOps

**Neuro-Symbolic Middleware for Regulated Administrative Decision-Making.**

[![CI](https://github.com/rafaelcontente/AMALIA-NeSyOps/actions/workflows/ci.yml/badge.svg)](https://github.com/rafaelcontente/AMALIA-NeSyOps/actions)
[![Tests](https://img.shields.io/badge/tests-600%2B%20passing-brightgreen)](https://github.com/rafaelcontente/AMALIA-NeSyOps/actions)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)

AMALIA-NeSyOps is a production-grade, audit-ready middleware combining LLMs with deterministic symbolic rules. Designed for **EU AI Act compliance**, featuring durable audit, formal explanation validation, and continuous LLMOps.

## 🏆 Key Metrics
- **600+ Automated Tests**: Logic, security, performance, and compliance.
- **37,000+ req/s Throughput**: Deterministic core processes decisions in <0.02ms.
- **Zero Hallucination Guarantee**: Formal proofs for generated explanations.
- **EU AI Act Mapped**: 9 key articles explicitly linked to verifiable test cases.

## 🏗️ Phase 1: Core Engineering & Governance (P1–P9)
| ID | Priority | Deliverables |
|----|----------|--------------|
| **P1** | Evaluation | Golden set v2 (50 cases, 96% accuracy) |
| **P2** | Conformal Prediction | 100% empirical coverage, robust to drift |
| **P3** | Integration & Ops | JWT Auth, rate limiting, resilience, MCP security |
| **P4** | Durable Audit | SQLite WAL append-only, SHA256 backups, RBAC |
| **P5** | Real LLM | Ollama adapter, circuit breaker, anti-hallucination |
| **P6** | Governance | Maker-checker workflow, citizen appeal, runbooks |
| **P7** | Continuous Security | CI job with Gitleaks, pip-audit, and Bandit |
| **P8** | Formal Validation | 11 tests proving zero hallucinations in explanations |
| **P9** | Operational Docs | Deployment, rollback, and limits runbooks |
