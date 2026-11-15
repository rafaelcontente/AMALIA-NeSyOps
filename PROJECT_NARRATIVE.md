# 📖 The Story of AMALIA-NeSyOps

> *How do you give an administration the drafting power of an LLM without giving it the decision power?*

---

## 🌱 The origin

This project started with a simple, uncomfortable observation: **public administrations were starting to use LLMs to draft decisions, but nobody had solved the trust problem.**

An LLM can write a beautiful licence approval. It can also hallucinate a legal citation, ignore a zoning rule, or be tricked by a well-crafted prompt into approving anything. Meanwhile, regulators (EU AI Act, GDPR) demand that every high-stakes decision be **explainable, traceable, and human-overseeable**.

The gap was clear: *how do you get the speed and quality of an LLM without giving it the authority to decide?*

## 💡 The founding idea

**The LLM proposes. The system decides.**

This became the north star. Not "make the LLM more accurate" or "add more guardrails." Instead: **separate the proposal from the decision entirely.**

The LLM drafts. A deterministic, test-proven gate validates. Only the gate can release a decision. Every decision is written to a tamper-evident audit ledger. Anything borderline escalates to humans.

This is not a feature. It is the architecture.

## 🏗️ The journey: two phases, fifteen priorities

### Phase 1: Building the core (P1–P9)

We started with the hard parts:

- **Evaluation first** (P1). Before writing a line of code, we built a golden set of 50 cases. If we could not measure it, we could not build it.
- **Uncertainty quantification** (P2). Conformal prediction gave us a mathematical guarantee: "we are 95% confident this decision is correct, and here is the proof."
- **Operations** (P3). JWT auth, rate limiting, circuit breakers. Not glamorous, but without them, nothing runs in production.
- **Durable audit** (P4). SQLite WAL append-only, hash-chained, with GDPR-style erasure that preserves chain validity. Because "we logged it" is not enough; "we can prove it was not tampered with" is.
- **Real LLM integration** (P5). Ollama adapter with circuit breaker, retry, timeout, and anti-hallucination validation. The LLM is a component, not the system.
- **Governance** (P6). Maker-checker workflow, citizen appeals, incident runbooks. Because a system without human oversight is not a decision system; it is a lottery.
- **Continuous security** (P7). Gitleaks, pip-audit, Bandit in CI. Security is not a phase; it is a pipeline.
- **Formal explanation validation** (P8). We proved mathematically that generated explanations cite only rules that ran and evidence that was provided. Zero orphan claims. This is not "we tested it"; this is "we proved it."
- **Operational documentation** (P9). Runbooks for deployment, rollback, failure modes. Because a system you cannot operate is not a system; it is a demo.

### Phase 2: Production and compliance (P10–P15)

With the core proven, we scaled:

- **Expanded golden set** (P10). 200+ semi-real cases across 4 domains, with metrics disaggregated by category. Because "96% accuracy" means nothing if you do not know where the 4% fails.
- **Performance validation** (P11). Throughput >37,000 req/s, p95 latency <0.05ms on the deterministic core. Because "it works" is not enough; "it works under load" is.
- **Controlled pilot mode** (P12). `PILOT_MODE=true` forces every decision into human review. Because rolling out a new system without a controlled pilot is not engineering; it is gambling.
- **EU AI Act compliance mapping** (P13). Machine-readable JSON linking 9 critical articles to specific tests, with a meta-test that fails if any referenced test is renamed or deleted. Because compliance is not a document; it is code.
- **Continuous LLM evaluation** (P14). Script that validates the real model against hallucination and latency limits, failing the pipeline if thresholds are breached. Because the LLM is not static; it drifts.
- **Versioned evaluation reports** (P15). Automated generation of JSON/Markdown reports with metric deltas and commit hashes. Because "it was good last month" is not evidence; "it is good at this commit" is.

## ⚖️ The trade-offs

Every architecture is a set of trade-offs. Here are the ones we made explicitly:

### 1. Determinism over cleverness
We could have used a more sophisticated LLM, or fine-tuned a model, or added more layers of neural reasoning. Instead, we chose **deterministic rules evaluated via a safe AST**. Why? Because a decision system must be reproducible. If the same input produces different outputs on different days, you do not have a decision system; you have a slot machine.

### 2. Fail-closed over fail-open
When the gate is uncertain, it rejects or escalates. It never silently approves. Why? Because a false approval in a regulated environment is a legal liability; a false rejection is an inconvenience. We chose the inconvenience.

### 3. Audit over performance
Every decision is written to a hash-chained ledger. This adds latency. We accepted it. Why? Because in a regulated environment, the ability to prove what happened is more valuable than saving 50ms.

### 4. Human oversight over full automation
We could have built a system that approves everything automatically. We did not. Why? Because the EU AI Act requires human oversight for high-risk systems, and more importantly, because **some decisions should not be fully automated**. The maker-checker workflow is not a limitation; it is a feature.

### 5. Evidence over certification
We produce compliance evidence (model cards, traceability matrices, risk registers), but we do not claim certification. Why? Because **no tool certifies a system by itself**. Conformity assessment is a human process involving jurists and DPOs. We make that process faster and defensible; we do not replace it.

## 🎓 Lessons learned

### 1. Start with the golden set
We built the evaluation suite before the system. This forced us to define what "correct" means before we wrote code that might be "correct." It saved us from building a system that worked but did not solve the problem.

### 2. Every guarantee must be a test
Early on, we had claims in the docs that were not backed by tests. We caught this when a refactor broke a guarantee silently. Now, every claim in the README maps to an executable test. If a test breaks, the claim is void.

### 3. The LLM is a component, not the system
We spent weeks trying to make the LLM "more accurate." Then we realized: the LLM is not the system. The gate is the system. The LLM is a drafting tool. Once we accepted this, the architecture became clear.

### 4. Compliance is code, not documentation
We started with a compliance document. It went stale in two weeks. We replaced it with `compliance/eu_ai_act_mapping.json` — a machine-readable mapping that is validated by tests. Now, compliance cannot drift silently.

### 5. Performance is a feature, not an afterthought
We did not add performance tests at the end. We added them in Phase 2, after the core was proven. Why? Because "it works" is not enough; "it works under load" is. The deterministic core sustains 37,000 req/s. That is not a number we tuned; it is a number we measured.

## 🔭 What this represents

AMALIA-NeSyOps is not just a middleware. It is a **reference architecture** for how to build regulated AI systems.

It proves that you can:
- Use LLMs for drafting without giving them decision authority.
- Build a deterministic, test-proven decision core.
- Produce compliance evidence that is machine-readable and self-validating.
- Operate a system with human oversight as a first-class feature.
- Scale horizontally without sacrificing auditability.

This is not a demo. It is a blueprint.

## 🚀 What comes next

The roadmap is ordered, not committed:

1. **Distributed adapters** (Postgres/Kafka) for horizontal scaling.
2. **Expert-labelled pt-PT corpus** for calibration metrics.
3. **Additional domain packs** and multilingual support.
4. **Manual WCAG audit** to complement the heuristic checker.

But the foundation is solid. The core is proven. The architecture is sound.

## 🙏 Acknowledgments

This project was inspired by:
- **ETALAB** (French State AI Hub) for showing that regulated AI is possible.
- **UNDP transparency tooling** for proving that auditability is a feature, not a burden.
- **SantanderAI fairness work** for demonstrating that bias detection is an engineering problem.
- **The AI Alliance evaluation tooling** for establishing that evaluation is a first-class concern.

And to every engineer who has ever said, "but how do we prove it works?" — this is for you.

---

Maintainer: **Rafael Contente** · [Repository](https://github.com/rafaelcontente/AMALIA-NeSyOps) · [Issues](https://github.com/rafaelcontente/AMALIA-NeSyOps/issues)
