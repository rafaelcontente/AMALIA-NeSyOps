# AMALIA-NeSyOps

**Neuro-symbolic middleware for auditable administrative decision support (pt-PT).**

[![CI](https://github.com/rafaelcontente/AMALIA-NeSyOps/actions/workflows/ci.yml/badge.svg)](https://github.com/rafaelcontente/AMALIA-NeSyOps/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-216%20passing-brightgreen)](#testing--ci)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](.github/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-EUPL--1.2-blue)](LICENSE)

> **Maturity: reference implementation.** The deterministic decision core is test-proven
> (216 tests, 87% coverage on decision-critical modules, CI on Python 3.11-3.13).
> LLM calls are mocked, storage is in-memory, and no conformity assessment has been
> performed. Read [Limitations](#limitations) before assuming production readiness.

## Overview

AMALIA-NeSyOps separates what an LLM may *propose* from what the system may *decide*.
Language models draft; a deterministic five-layer gate validates against formal rules,
consistency checks and cited evidence; decisions are written to a hash-chained audit
ledger; borderline cases escalate to humans under a maker-checker workflow.

**What it is**

- A working, test-proven decision pipeline: ingest -> knowledge -> rules/reasoning -> gate -> audit -> explain.
- An evidence generator for regulatory review: traceability matrix, model cards, risk register, signed checklists.
- A reference architecture for high-stakes administrative AI in European Portuguese.

**What it is not**

- Not a certified product. Conformity is a process involving jurists and DPOs, not a library.
- Not an LLM. No model is bundled; the agent layer runs against deterministic mocks in tests.
- Not a database. Ledgers and queues are in-memory; a durability adapter is required before deployment.
- Not legal advice.

## Guarantees, and where each is proven

Every claim below is enforced in code and pinned to an executable test. If a test breaks, the claim is void.

| # | Invariant | Enforcement | Proof |
|---|-----------|-------------|-------|
| 1 | The gate overrides the LLM; validator failure always rejects | `gate/gate.py` | `tests/test_gate.py::test_validator_failure_refuses_always` |
| 2 | Prompt injection is rejected at layer 1, including nested fields | `gate/validator.py` + `ingest/security.py` | `tests/security/test_prompt_injection.py` (25 tests) |
| 3 | DRAFT rules never influence decisions; activation requires positive **and** negative tests; proposer cannot approve | `policy/registry.py`, `policy/engine.py` | `tests/unit/test_rule_parser.py`, `tests/test_policy.py` |
| 4 | Self-repair is bounded: attempt 1 of 2, then human escalation | `gate/planner.py` | `tests/unit/test_guardrails.py` |
| 5 | Missing data never satisfies a HARD rule | `policy/engine.py` | `tests/unit/test_rule_parser.py::test_missing_data_never_approves` |
| 6 | Audit chain is tamper-evident; GDPR-style erasure preserves chain validity | `audit/` | `tests/unit/test_audit_log.py`, `tests/test_audit.py` |
| 7 | Tenants are isolated; identical requests are idempotent | `integration/` | `tests/test_integration.py` |
| 8 | Every module imports and every annotation resolves on Python 3.11-3.13 | CI matrix + smoke tests | `tests/unit/test_imports.py`, `tests/unit/test_annotations.py` |
| 9 | Gate -> ledger integration produces a verifiable audit record | `audit/ledger.py` | `tests/integration/test_decision_pipeline.py` |

**Known gap (tracked):** automatic audit enforcement on the API request path
(`APIGateway`) is in progress. Today the invariant is proven at integration level;
fail-closed enforcement inside the gateway is the next change.
