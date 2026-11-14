"""Guarantee: no production module depends on network, LLM SDKs or API keys.

Static checks complement the runtime socket block in tests/conftest.py.
"""
import ast
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIRS = ["core", "ingest", "knowledge", "policy", "formalize", "reasoning", "agents",
        "gate", "explain", "audit", "review", "monitor", "compliance", "eval",
        "integration", "domains", "apps"]
MODULES = sorted(f"{d}.{p.stem}" for d in DIRS
                 for p in (ROOT / d).glob("*.py") if p.name != "__init__.py")

FORBIDDEN_TOP = {"requests", "httpx", "aiohttp", "socket", "openai", "anthropic", "urllib3"}
FORBIDDEN_DOTTED = {"urllib.request"}
KEY_PATTERNS = ("API_KEY", "SECRET", "TOKEN", "PASSWORD")


def _source(module):
    return (ROOT / (module.replace(".", "/") + ".py")).read_text(encoding="utf-8")


@pytest.mark.parametrize("module", MODULES)
def test_no_network_or_llm_imports(module):
    tree = ast.parse(_source(module))
    top, dotted = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                top.add(a.name.split(".")[0])
                dotted.add(a.name)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            top.add(node.module.split(".")[0])
            dotted.add(node.module)
    bad = (top & FORBIDDEN_TOP) | (dotted & FORBIDDEN_DOTTED)
    assert not bad, f"{module} imports network/LLM modules: {sorted(bad)}"


@pytest.mark.parametrize("module", MODULES)
def test_no_api_key_reads(module):
    for i, line in enumerate(_source(module).splitlines(), 1):
        if ("os.environ" in line or "os.getenv" in line) and any(k in line.upper() for k in KEY_PATTERNS):
            pytest.fail(f"{module}:{i} reads a credential from the environment")


def test_suite_runs_without_credentials(monkeypatch):
    """Even with an empty environment, the decision core must work."""
    import importlib
    for name in ("API_KEY", "OPENAI_API_KEY", "AMALIA_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    gate_mod = importlib.import_module("gate.gate")
    val_mod = importlib.import_module("gate.validator")
    from core.models import Proposal, TraceID
    gate = gate_mod.Gate(val_mod.GateValidator())
    r = gate.evaluate(Proposal(trace_id=TraceID(), agent="t",
                               content={"age": 25}, confidence=0.9))
    assert r["verdict"] is not None
