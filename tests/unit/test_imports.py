"""Import smoke test: every module must import cleanly.

Guards against latent NameError/ImportError in modules that no other
test happens to import (the webhooks/mcp_server bug class).
"""
import importlib
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIRS = ["core", "ingest", "knowledge", "policy", "formalize", "reasoning",
        "agents", "gate", "explain", "audit", "review", "monitor",
        "compliance", "eval", "integration", "domains", "apps"]

MODULES = sorted(
    f"{d}.{p.stem}"
    for d in DIRS
    for p in (ROOT / d).glob("*.py")
    if p.name != "__init__.py"
)

@pytest.mark.parametrize("module", MODULES)
def test_module_imports(module):
    importlib.import_module(module)
