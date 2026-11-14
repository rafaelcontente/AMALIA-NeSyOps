"""Regenerates the Metrics section and colored diagram of README.md from real runs.

Measures: per-module coverage (pytest --cov) and test counts per suite
(pytest --collect-only). Refuses to write if the suite is not green.
"""
import re
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CRITICAL = ["core", "gate", "policy", "audit", "ingest", "reasoning"]


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)


def measure_coverage():
    p = run([sys.executable, "-m", "pytest", "tests/", "-q"]
            + [f"--cov={m}" for m in CRITICAL] + ["--cov-report=term"])
    if p.returncode != 0:
        sys.exit("Suite not green - README NOT updated.")
    stmts, miss = {}, {}
    for line in p.stdout.splitlines():
        m = re.match(r"^(\w+)/[\w.]+\.py\s+(\d+)\s+(\d+)\s+\d+%", line)
        if m:
            mod, s, mi = m.group(1), int(m.group(2)), int(m.group(3))
            stmts[mod] = stmts.get(mod, 0) + s
            miss[mod] = miss.get(mod, 0) + mi
    return {m: round(100 * (stmts[m] - miss[m]) / stmts[m]) for m in CRITICAL if m in stmts}


def measure_tests():
    p = run([sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"])
    counts = {"unit": 0, "integration": 0, "security": 0, "acceptance": 0}
    for line in p.stdout.splitlines():
        if "::" not in line:
            continue
        path = line.split("::")[0]
        if path.startswith("tests/unit/"):
            counts["unit"] += 1
        elif path.startswith("tests/integration/"):
            counts["integration"] += 1
        elif path.startswith("tests/security/"):
            counts["security"] += 1
        elif path.startswith("tests/test_"):
            counts["acceptance"] += 1
    return counts


def badge_color(pct):
    if pct >= 90:
        return "brightgreen"
    if pct >= 80:
        return "green"
    if pct >= 70:
        return "yellowgreen"
    if pct >= 60:
        return "yellow"
    if pct >= 50:
        return "orange"
    return "red"


COLORED_DIAGRAM = """```mermaid
flowchart TD
    APPS["apps/ - reviewer console, audit explorer, manager dashboard, rule editor"]:::iface
    INT["integration/ - REST gateway, idempotency, tenant isolation, webhooks, MCP"]:::pipe
    GATE["gate/ - 5 validation layers: structure+injection, consistency, rules, plausibility, claims"]:::pipe
    REVIEW["review/ - human queue with maker-checker"]:::human
    POL["policy/ - AST-safe rules, maker-checker, versioned rule sets"]:::pipe
    REA["reasoning/ - deterministic solver + independent proof check"]:::pipe
    KNO["knowledge/ - RDF ontology, temporal validity, cited retrieval"]:::pipe
    ING["ingest/ - parsing, pt-PT normalization, untrusted-text flagging"]:::pipe
    AGENTS["agents/ - LLM orchestration, mocked in tests: proposes, never decides"]:::llm
    AUD["audit/ - hash-chained ledger"]:::evid
    EXP["explain/ - citizen and auditor views"]:::evid

    APPS -->|API only, zero decision logic| INT
    INT --> GATE
    GATE -->|fail: repair 1 of 2, then escalate| REVIEW
    GATE --> POL
    GATE --> REA
    GATE --> KNO
    GATE --> ING
    AGENTS -->|proposal input| GATE
    GATE -->|every released decision| AUD
    GATE --> EXP

    classDef iface fill:#6f42c1,stroke:#4b2e83,color:#fff
    classDef pipe  fill:#0969da,stroke:#0550ae,color:#fff
    classDef evid  fill:#1a7f37,stroke:#116329,color:#fff
    classDef human fill:#9a6700,stroke:#7d5400,color:#fff
    classDef llm   fill:#57606a,stroke:#424a53,color:#fff
```

Legend: blue = decision pipeline, green = evidence and audit, purple = human-facing
interfaces, amber = human decision point, grey = LLM layer (proposes, never decides).
"""


def main():
    cov = measure_coverage()
    tests = measure_tests()
    total = sum(tests.values())

    readme = ROOT / "README.md"
    src = readme.read_text(encoding="utf-8")

    # 1. Color the architecture diagram (idempotent)
    start = src.index("```mermaid")
    end = src.index("```", start + 8) + 3
    legend_end = src.index("## Repository layout")
    src = src[:start] + COLORED_DIAGRAM + "\n" + src[legend_end:]

    # 2. Build Metrics section
    bars = ", ".join(str(cov[m]) for m in CRITICAL)
    labels = ", ".join(CRITICAL)
    badges = " ".join(
        f"![{m}](https://img.shields.io/badge/{m}-{cov[m]}%25-{badge_color(cov[m])})"
        for m in CRITICAL
    )
    pie_lines = "\n".join(f'    "{k}" : {v}' for k, v in tests.items())

    metrics = (
        "\n## Metrics\n\n"
        "Measured from the repository by `scripts/update_readme_metrics.py`; "
        "never hand-edited.\n\n"
        f"{badges}\n\n"
        "```mermaid\n"
        'xychart-beta\n'
        '    title "Coverage by critical module (%)"\n'
        f"    x-axis [{labels}]\n"
        '    y-axis "coverage (%)" 0 --> 100\n'
        f"    bar [{bars}]\n"
        "```\n\n"
        "```mermaid\n"
        f"pie showData\n"
        f'    title "Tests by suite ({total} total)"\n'
        f"{pie_lines}\n"
        "```\n\n"
    )

    marker = "\n## Metrics"
    if marker in src:
        src = src[:src.index(marker)] + metrics + src[src.index("\n## Security"):]
    else:
        src = src.replace("\n## Security", metrics + "\n## Security", 1)

    readme.write_text(src, encoding="utf-8")
    print(f"coverage: {cov}")
    print(f"tests: {tests} (total {total})")
    print("README.md updated: colored diagram + Metrics section")


main()
