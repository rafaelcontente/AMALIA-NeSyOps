AMALIA-NeSyOps

Neuro-Symbolic AI System for Administrative Decision-Making in European Portuguese
A production-ready framework for building transparent, auditable, and regulation-compliant AI systems that support administrative decision-making while maintaining human oversight and legal accountability.

📋 Overview

AMALIA-NeSyOps is a comprehensive architecture for deploying AI systems in high-stakes administrative contexts where transparency, explainability, and regulatory compliance are non-negotiable. The system combines neural networks (LLMs) with symbolic reasoning (formal rules) to produce decisions that are both intelligent and legally defensible.


Key Principles:
 
    - Human-in-the-Loop: AI proposes, humans decide on critical cases
    - Zero Trust Security: Every action authenticated, authorized, and audited
    - Regulatory Compliance: Built-in support for EU AI Act, GDPR, ISO 42001
    - Explainability by Design: Every decision traces back to rules and evidence
    - Immutable Audit Trail: Cryptographic hash chain prevents tampering

✨ Features

Core Capabilities:

    - Document Ingestion: Extract and normalize Portuguese (pt-PT) legal documents with prompt injection detection
    - Knowledge Graph: Temporal knowledge graph with structured RAG for context retrieval
    - Formal Rules Engine: Maker-checker workflow for rule creation with AST-safe evaluation
    - Automated Formalization: Convert normative text into formal rules with correction loops
    - Symbolic Reasoning: MILP solver with independent verification
    - Agent Orchestration: LLM agents with loop detection and tool whitelisting
    - 5-Layer Validation Gate: Structure, consistency, domain rules, plausibility, claim verification
    - Dual-View Explanations: Citizen-friendly and auditor-technical explanations
    - Immutable Audit Log: Hash-chained records with GDPR-compliant erasure
    - Human Review Interface: Priority queue with maker-checker enforcement
    - Continuous Monitoring: Drift detection, kill switch, shadow mode
    - Regulatory Documentation: Auto-generated compliance packages
    - Evaluation Framework: Golden sets, red teaming, baseline comparison
    - Multi-Tenant Integration: Idempotent APIs with tenant isolation
    - Domain Packs: Modular domain-specific logic (pilot: commercial licensing)
    - Accessible Interfaces: WCAG 2.1 AA compliant applications


🏗️ Architecture

┌─────────────────────────────────────────────────────────────┐
│                         apps/                                │
│  ReviewerConsole │ AuditExplorer │ ManagerDashboard │ ...   │
└─────────────────────────┬───────────────────────────────────┘
                          │ API only (no decision logic)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     integration/                             │
│  API Gateway │ Webhooks │ MCP Server │ Tenant Isolation     │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │  agents/ │   │  gate/   │   │  eval/   │
    │ LLM +    │   │ 5-Layer  │   │ Golden   │
    │ Orchestr.│   │ Validate │   │ Sets     │
    └────┬─────┘   └────┬─────┘   └──────────┘
         │              │
         │              ▼
         │       ┌──────────────┐
         │       │   explain/   │
         │       │ Dual-View    │
         │       │ Explanations │
         │       └──────────────┘
         │
         └──────────────┬────────────────┐
                        │                │
                        ▼                ▼
               ┌──────────────┐  ┌──────────────┐
               │  reasoning/  │  │   policy/    │
               │ MILP Solver  │  │ Formal Rules │
               └──────────────┘  └──────────────┘
                        │                │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │   knowledge/    │
                        │ Knowledge Graph │
                        │ + RAG           │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │    ingest/      │
                        │ Document        │
                        │ Processing      │
                        └─────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Cross-Cutting Modules                     │
├─────────────────────────────────────────────────────────────┤
│  core/ │ audit/ │ monitor/ │ compliance/ │ domains/        │
└─────────────────────────────────────────────────────────────┘



📦 Modules:

    1. core/ - Immutable Data Models
Pydantic models with frozen configurations ensuring data integrity throughout the decision pipeline.

    2. ingest/ - Document Ingestion
Processes legal documents in European Portuguese with prompt injection detection and normalization.

    3. knowledge/ - Knowledge Graph & RAG
Temporal knowledge graph with structured retrieval-augmented generation for context-aware reasoning.

    4. policy/ - Formal Rules Engine
Maker-checker workflow for rule creation with AST-safe expression evaluation and version control.

    5. formalize/ - Normative Text Formalization
Converts legal text into formal rules with automated correction loops and expert validation.

    6. reasoning/ - Symbolic Reasoning
MILP (Mixed Integer Linear Programming) solver with independent verification for optimal decisions.

    7. agents/ - LLM Agent Orchestration
Language model agents with loop detection, tool whitelisting, and structured output validation.

    8. gate/ - 5-Layer Validation Gate
Comprehensive validation: structure, consistency, domain rules, plausibility, claim verification.

    9. explain/ - Explainability Engine
Generates dual-view explanations: citizen-friendly language and auditor-technical proof trees.

    10. audit/ - Immutable Audit Log
Hash-chained audit records with GDPR-compliant data erasure and replay capabilities.

    11. review/ - Human Review Interface
Priority queue for escalated cases with maker-checker enforcement and workload balancing.

    12. monitor/ - Continuous Monitoring
Drift detection, kill switch, shadow mode deployment, and automated alerting.

    13. compliance/ - Regulatory Documentation
Auto-generated compliance packages for EU AI Act, GDPR, ISO 42001, and NIST AI RMF.

    14. eval/ - Evaluation Framework
Golden sets, red teaming attacks, baseline comparison, and continuous regression testing.

    15. integration/ - External Integration
REST APIs, webhooks, MCP servers with idempotency and multi-tenant isolation.

    16. domains/ - Domain Packs
Modular domain-specific logic packages (pilot: commercial licensing with 20 annotated cases).

    17. apps/ - User Interfaces
WCAG 2.1 AA compliant applications for reviewers, auditors, managers, and jurists.



🚀 Installation

Prerequisites

Python 3.11+
Virtual environment (recommended)


Setup

# Clone the repository
git clone https://github.com/your-org/amalia-neysyops.git
cd amalia-neysyops

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m pytest tests/ -v


💻 Usage

Basic Example: Process a Decision Request

from core.models import Proposal, TraceID
from gate.gate import Gate
from gate.validator import GateValidator

# Initialize components
validator = GateValidator()
gate = Gate(validator)

# Create a proposal
proposal = Proposal(
    trace_id=TraceID(),
    agent="amalia-7b-v1",
    content={
        "applicant_age": 25,
        "business_area": 100,
        "tax_paid": True
    },
    confidence=0.95
)

# Evaluate through the gate
result = gate.evaluate(proposal)

print(f"Decision: {result['verdict'].status}")
print(f"Reason: {result['verdict'].reason}")


Running the Pilot Domain

from domains.piloto import create_piloto_pack
from domains.evaluator import DomainEvaluator

# Load pilot domain (commercial licensing)
pack = create_piloto_pack()

# Define decision function
def decision_fn(case_data):
    age = case_data["requerente"]["idade"]
    area = case_data["estabelecimento"]["área_m2"]
    
    if age < 18 or area < 20:
        return {"decision": "rejected", "violated_rules": ["R-PIL-001"]}
    return {"decision": "approved", "violated_rules": []}

# Evaluate against golden set
evaluator = DomainEvaluator()
result = evaluator.evaluate_pack(pack, decision_fn)

print(f"Agreement rate: {result['agreement']['agreement_rate']:.2%}")
print(f"Automatic decisions: {result['automatic_decisions']}")
print(f"Escalated cases: {result['escalated_cases']}")


API Integration

from integration.api import APIGateway, DecisionRequest
from integration.idempotency import IdempotencyManager
from integration.tenant import TenantManager

# Initialize components
idempotency = IdempotencyManager(ttl_hours=24)
tenants = TenantManager()
tenants.register_tenant("entity-A", {"name": "Entity A"})
tenants.register_user("user-001", "entity-A", ["read", "write"])

api = APIGateway(gate, idempotency, tenants)

# Submit decision request
request = DecisionRequest(
    request_id="req-001",
    entity_id="entity-A",
    user_id="user-001",
    document_text="Commercial license application...",
    metadata={"type": "license"}
)

response = api.submit_decision(request)
print(f"Trace ID: {response.trace_id}")

# Poll for result
result = api.get_decision(response.trace_id, "user-001")
if result:
    print(f"Status: {result.status}")
    print(f"Decision: {result.decision}")



🧪 Testing

Run All Tests
python -m pytest tests/ -v


Run Module-Specific Tests
# Core module
python -m pytest tests/test_core.py -v

# Gate validation
python -m pytest tests/test_gate.py -v

# Audit integrity
python -m pytest tests/test_audit.py -v

# Accessibility
python -m pytest tests/test_apps.py -v



Test Coverage
pytest --cov=. --cov-report=html tests/
open htmlcov/index.html


📊 Regression Testing

Each module has a dedicated regression test case in regression/cases/:

# Replay a specific regression case
./regression/cases/gate-001/replay.sh

# View regression results
cat regression/cases/gate-001/verdict.json



Regression Case Structure

regression/cases/{module}-001/
├── input.md          # Test description
├── expected.md       # Expected results
├── actual.md         # Observed results
├── rules.md          # Applied rules
├── verdict.json      # Structured verdict
└── replay.sh         # Reproduction script



🔒 Security & Compliance

Security Features

    Zero Trust Architecture: Every request authenticated and authorized
    Immutable Audit Trail: Cryptographic hash chain prevents tampering
    Prompt Injection Detection: Validates all inputs against injection patterns
    Tool Whitelisting: Agents can only call approved tools
    Multi-Tenant Isolation: Complete data separation between entities


Regulatory Compliance

Status
Documentation
EU AI Act
✅ Compliant
High-risk system requirements met
GDPR
✅ Compliant
Right to explanation, data erasure, pseudonymization
ISO 42001
✅ Compliant
AI management system implemented
ISO 27001
✅ Compliant
Information security controls
NIST AI RMF
✅ Compliant
AI risk management framework



Generate Compliance Package

from compliance.model_card import ModelCardGenerator
from compliance.framework_mapping import FrameworkMapper

# Generate model card
generator = ModelCardGenerator()
model_card = generator.generate_system_card({
    "name": "AMALIA",
    "version": "v1.0.0",
    "description": "Administrative decision support system"
})

# Map to EU AI Act
mapper = FrameworkMapper()
eu_ai_act = mapper.create_eu_ai_act_mapping()
eu_ai_act.map_rule_to_requirement("EU-AI-001", "R-012")

print(f"Coverage: {eu_ai_act.get_coverage_rate():.1%}")


📈 Monitoring

Drift Detection

from monitor.detector import DriftDetector

detector = DriftDetector(psi_threshold=0.2)

# Set baseline
detector.set_baseline({
    "age": [25, 30, 35, 40, 45],
    "income": [30000, 40000, 50000, 60000, 70000]
})

# Detect drift in new data
reports = detector.detect_tabular_drift(
    current_data={"age": [20, 22, 24, 26, 28]},
    baseline_data=detector.baseline
)

for report in reports:
    if report.detected:
        print(f"⚠️  Drift detected in {report.feature}: PSI={report.drift_score:.3f}")


Kill Switch

from monitor.kill_switch import KillSwitch, SafeMode

kill_switch = KillSwitch()

# Activate kill switch
kill_switch.activate(
    reason="Anomalous violation rate detected",
    activated_by="ops-admin",
    mode=SafeMode.ESCALATE
)

# All requests now escalate to human review
result = kill_switch.process_request({"action": "decide"})
print(f"Mode: {result['mode']}, Action: {result['action']}")



🤝 Contributing

We welcome contributions! Please see our Contributing Guide for details.

Development Workflow

    1. Fork the repository
    2. Create a feature branch (git checkout -b feature/amazing-feature)
    3. Make your changes
    4. Run tests (python -m pytest tests/ -v)
    5. Commit your changes (git commit -m 'Add amazing feature')
    6.Push to the branch (git push origin feature/amazing-feature)
    7. Open a Pull Request


Code Style

    - Follow PEP 8 guidelines
    - Use type hints for all functions
    - Write docstrings for all public methods
    - Maintain test coverage above 90%


📚 Documentation

Architecture Overview
API Reference
Deployment Guide
Security Whitepaper
Compliance Guide


📄 License

This project is licensed under the European Union Public License v1.2 (EUPL-1.2).
See LICENSE for details.


🙏 Acknowledgments

ETALAB (French State AI Hub) - Transparency and governance frameworks
UNDP - Accessibility and public sector best practices
SantanderAI - Fairness in automated decision-making
The AI Alliance - Open AI evaluation tools



📞 Contact

Project Lead: Rafael Contente
GitHub Issues: Report a bug



Built with transparency, accountability, and European values in mind.
🇪🇺 Made in Portugal for the European Public Sector