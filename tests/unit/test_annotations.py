"""All annotations must resolve eagerly (Python <= 3.13 behaviour).

Python 3.14+ defers annotation evaluation (PEP 649), hiding missing
imports locally. This test forces resolution so the bug class is caught
on ANY Python version, not only in the CI matrix.
"""
import importlib
import inspect
import pathlib
import typing
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIRS = ["core", "ingest", "knowledge", "policy", "formalize", "reasoning",
        "agents", "gate", "explain", "audit", "review", "monitor",
        "compliance", "eval", "integration", "domains", "apps"]
MODULES = sorted(f"{d}.{p.stem}" for d in DIRS
                 for p in (ROOT / d).glob("*.py") if p.name != "__init__.py")


@pytest.mark.parametrize("module", MODULES)
def test_annotations_resolve(module):
    mod = importlib.import_module(module)
    objs = [mod]
    for obj in vars(mod).values():
        if inspect.isclass(obj) and obj.__module__ == module:
            objs.append(obj)
            for m in vars(obj).values():
                if isinstance(m, staticmethod):
                    m = m.__func__
                if inspect.isfunction(m):
                    objs.append(m)
        elif inspect.isfunction(obj) and obj.__module__ == module:
            objs.append(obj)
    for o in objs:
        typing.get_type_hints(o)
