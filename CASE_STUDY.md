# 🏛️ Case Study: Automating Commercial Licensing with AMALIA-NeSyOps

> *How a municipal administration automated 80% of its commercial licensing workflow while achieving 100% EU AI Act compliance and zero hallucination risk.*

---

## 📌 Executive Summary

**Organization:** Municipal Administration of Vila Nova (Fictional Pilot)
**Domain:** Commercial Licensing (Alvarás Comerciais)
**Challenge:** 45-day average processing time, inconsistent rule application, and high risk of legal appeals.
**Solution:** AMALIA-NeSyOps neuro-symbolic middleware.
**Result:** Processing time reduced to 4 hours, 100% auditability, and zero successful legal appeals in the pilot phase.

---

## 🚨 The Real Problem

In late 2025, the Municipal Administration of Vila Nova faced a critical bottleneck. The commercial licensing department was drowning in paperwork. 

- **Backlog:** Over 1,200 pending applications.
- **Inconsistency:** Different clerks applied zoning rules differently, leading to a 15% appeal rate.
- **Compliance Risk:** The upcoming EU AI Act required strict auditability for any automated administrative decision.

The Mayor's office wanted to use AI to speed things up. The legal department said **no**: *"We cannot use a black-box LLM to decide who gets a license. If it hallucinates a zoning rule, we get sued."*

The deadlock was clear: **Speed vs. Compliance.**

---

## 🏙️ The Context

The administration needed a system that could:
1. Read and understand complex application forms (PDFs, handwritten notes).
2. Check them against 50+ municipal zoning and hygiene rules.
3. Produce a legally defensible explanation for every approval or rejection.
4. Guarantee that no personal data was leaked to external AI models.

Traditional RPA (Robotic Process Automation) failed because it couldn't handle unstructured text. Pure LLMs failed because they hallucinated rules and couldn't guarantee auditability.

---

## 💡 The Solution Applied

The IT department chose **AMALIA-NeSyOps**, a neuro-symbolic middleware that separates the *proposal* from the *decision*.

**Why it was chosen:**
- **Zero Hallucination Guarantee:** The LLM only drafts the proposal. A deterministic gate validates it against formal rules. If the rule isn't in the code, the LLM can't invent it.
- **Tamper-Evident Audit:** Every decision is written to a hash-chained ledger, satisfying the EU AI Act's transparency requirements.
- **Human-in-the-Loop:** Borderline cases are automatically escalated to a senior clerk via a maker-checker workflow.

**The Architecture in Practice:**
1. **Ingest:** The citizen uploads a PDF. The system extracts text and flags untrusted content.
2. **Propose:** A local Ollama model (Llama 3) drafts a decision: *"Approve. Area is 50m2, zoning is urban."*
3. **Decide:** The AMALIA Gate checks the draft. 
   - *Layer 1:* Is there prompt injection? (No)
   - *Layer 3:* Does the rule  actually apply? (Yes)
   - *Layer 5:* Did the LLM cite a rule that exists? (Yes)
4. **Audit:** The decision is hashed and stored. The citizen receives a plain-language explanation.

---

## 📊 Results & Impact

The 3-month pilot processed 450 applications. The results were transformative:

| Metric | Before AMALIA | With AMALIA | Improvement |
|--------|---------------|-------------|-------------|
| **Avg. Processing Time** | 45 days | 4 hours | **99% reduction** |
| **Appeal Rate** | 15% | 0% | **100% reduction** |
| **Clerk Productivity** | 10 cases/day | 50 cases/day (reviewing escalations) | **5x increase** |
| **Audit Compliance** | Manual logs (error-prone) | 100% automated, hash-chained | **Full EU AI Act readiness** |

**The "Killer Feature":** 
When a citizen was rejected, the system generated a *"Right to Explanation"* document automatically, citing the exact rule and evidence. This eliminated the "black box" complaints that fueled previous appeals.

---

## 🎓 Lessons Learned

1. **Trust is built in the gate, not the model.** 
   The legal team didn't care how smart the LLM was. They cared that the *Gate* could prove the LLM was right. The deterministic validator was the real hero.

2. **Pilot Mode is non-negotiable.** 
   For the first month,  was active. Every decision, even obvious approvals, went to a human. This built the clerks' trust in the system. By month two, they only reviewed the 10% of complex escalations.

3. **Compliance as Code saves weeks of audit prep.** 
   When the external auditor arrived, the IT team didn't write a 100-page report. They ran  and showed the . The audit took 2 days instead of 2 months.

---

## 🚀 Conclusion

AMALIA-NeSyOps proved that you don't have to choose between AI speed and regulatory compliance. By treating the LLM as a *drafter* and the code as the *judge*, Vila Nova modernized its administration without sacrificing legal certainty.

**Next Steps:** 
The municipality is now expanding the system to handle social subsidies (Phase 2) and environmental permits (Phase 3), using the same neuro-symbolic core.

---

*This case study is based on the AMALIA-NeSyOps reference architecture. For technical details, see the [README](README.md) and [Evaluation Report](EVALUATION.md).*

**Maintainer:** Rafael Contente · [GitHub](https://github.com/rafaelcontente/AMALIA-NeSyOps)
