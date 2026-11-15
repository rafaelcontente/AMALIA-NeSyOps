# 📊 Evaluation Report: AMALIA-NeSyOps

> *What was evaluated, how, and what was observed. Separates observed results from interpretation.*

---

## 1. 🎯 Evaluation Objective

**Primary question:** Does AMALIA-NeSyOps correctly enforce administrative rules while maintaining auditability, security, and performance under realistic conditions?

**Secondary questions:**
- Can the system distinguish valid from invalid proposals across multiple domains?
- Does the deterministic gate prevent LLM hallucinations and prompt injection?
- Is the audit ledger tamper-evident and GDPR-compliant?
- Does the system sustain production-grade throughput and latency?

**Scope:** This evaluation covers the deterministic decision core, the LLM integration layer, the audit pipeline, and the compliance evidence generators. It does **not** evaluate the legal correctness of specific administrative rules.

---

## 2. 📁 Datasets & Scenarios

### 2.1 Golden Set v3 (Primary Evaluation Dataset)
- **Size:** 200 semi-real cases
- **Domains:** 4 administrative domains (50 cases each): licensing, subsidies, environmental offenses, public health.
- **Structure:** Input data, expected decision, and expected violated rules.
- **Location:** `eval/golden_set_v3.json`

### 2.2 Security Test Suite
- **Patterns:** 25 test cases covering jailbreak, XSS, SQL injection, and nested-field attacks.
- **Location:** `tests/security/`

### 2.3 Performance Scenarios
- **Valid path:** 5,000 iterations of approved proposals.
- **Invalid path:** 5,000 iterations of rejected proposals (fail-fast).
- **Large payload:** 1,000 iterations with 10KB payloads.

### 2.4 Compliance Mapping
- **Framework:** EU AI Act (9 critical articles: 9, 10, 13, 14, 15, 17, 19, 26, 29).
- **Mapping:** 22 test IDs linked to specific articles.
- **Location:** `compliance/eu_ai_act_mapping.json`

---

## 3. 📏 Metrics
- **Decision Accuracy:** Accuracy, Precision, Recall, F1 Score (global and per-category).
- **Security:** Injection detection rate, false positive rate, hallucination rate.
- **Performance:** Throughput (req/s), p95 and average latency (ms).
- **Audit Integrity:** Chain validity (boolean), erasure compliance.
- **Compliance Coverage:** % of mapped articles with at least one passing test.

---

## 4. 📐 Baselines
- **Accuracy Target:** >90% across all domains (Baseline: 50% random).
- **Security Target:** >95% detection rate for known injection patterns (Baseline: 0%).
- **Performance Target:** >500 req/s with p95 latency <50ms for the deterministic core.
- **Compliance Target:** 100% of mapped articles have at least one executable test.

---

## 5. 📈 Observed Results

### 5.1 Decision Accuracy
| Domain | Cases | Accuracy | Precision | Recall | F1 Score |
|--------|-------|----------|-----------|--------|----------|
| licensing | 50 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| subsidies | 50 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| environmental | 50 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| public_health | 50 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **Global** | **200** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |

### 5.2 Security
| Metric | Observed | Target | Status |
|--------|----------|--------|--------|
| Injection detection rate | 100% (25/25) | >95% | ✅ Pass |
| False positive rate | 0% | <5% | ✅ Pass |
| Hallucination rate (explanations) | 0% | 0% | ✅ Pass |

### 5.3 Performance
| Scenario | Throughput (req/s) | p95 Latency (ms) |
|----------|-------------------|------------------|
| Valid path | 36,011 | 0.02 |
| Invalid path | 37,997 | 0.02 |
| Large payload (10KB) | N/A | 0.45 |

### 5.4 Audit & Compliance
- **Chain validity:** True (normal operation and after GDPR erasure).
- **Article coverage:** 9/9 (100%).
- **Test existence:** 22/22 (100%).

---

## 6. 🔍 Error Analysis
- **Decision Errors:** 0 observed on Golden Set v3. Potential risk: rule misinterpretation (mitigated by maker-checker approval).
- **Security False Negatives:** 0 on known patterns. Risk: novel injections (mitigated by defense-in-depth at Gate Layers 3 and 5).
- **Performance:** No degradation observed. Risk: single-node SQLite bottleneck at extreme scale (>100k concurrent reqs).

---

## 7. ⚠️ Limitations
1. **Golden set size:** 200 cases is sufficient for validation, but production requires 1,000+ expert-labelled cases.
2. **Domain coverage:** 4 domains tested. Real systems may have 50+.
3. **LLM evaluation:** Tested for hallucination rate, but not for deep decision quality (requires expert corpus).
4. **External validity:** Tested on macOS. Performance may vary on different hardware/OS.

---

## 8. 🎯 Conclusions
1. The deterministic gate achieves perfect accuracy on the evaluated golden set.
2. Security controls detect 100% of known injection patterns with 0% false positives.
3. Performance exceeds production targets by ~70x.
4. Audit integrity is maintained under normal operation and GDPR-style erasure.
5. Compliance evidence is complete and self-validating.

**Interpretation:** The architecture works as designed. Separating proposal (LLM) from decision (gate) enables both flexibility and auditability. The system is ready for pilot deployment in controlled environments.

---

## 9. 📚 Reproducibility
To reproduce this evaluation:
```bash
git clone https://github.com/rafaelcontente/AMALIA-NeSyOps.git
cd AMALIA-NeSyOps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -v
python scripts/generate_eval_report.py
```
*Evaluation conducted: November 2026. Maintainer: Rafael Contente. Version: 1.0.*
