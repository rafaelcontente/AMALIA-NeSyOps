"""Measure coverage per critical module and compare against the versioned baseline.

Usage:
    python scripts/check_coverage.py                # compare now vs baseline (CI)
    python scripts/check_coverage.py --set-baseline # freeze current state as baseline

Exits non-zero if the suite is not green or any module regressed below baseline.
"""
import json
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CRITICAL = ["core", "gate", "policy", "audit", "ingest", "reasoning", "formalize", "integration"]
BASELINE = ROOT / "coverage-baseline.json"


def measure():
    cmd = ([sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short",
            "--cov-report=term", "--cov-report=json:coverage.json",
            "--cov-report=xml:coverage.xml"]
           + [f"--cov={m}" for m in CRITICAL])
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if p.returncode != 0:
        print(p.stdout[-3000:])
        sys.exit("Suite not green - coverage NOT evaluated.")
    data = json.loads((ROOT / "coverage.json").read_text())
    agg = {}
    for path, info in data["files"].items():
        mod = path.split("/")[0]
        s = info["summary"]
        a = agg.setdefault(mod, {"stmts": 0, "miss": 0})
        a["stmts"] += s["num_statements"]
        a["miss"] += s["missing_lines"]
    out = {}
    for m in CRITICAL:
        if m in agg and agg[m]["stmts"]:
            out[m] = round(100 * (agg[m]["stmts"] - agg[m]["miss"]) / agg[m]["stmts"], 1)
    return out


def main():
    cov = measure()
    if "--set-baseline" in sys.argv:
        BASELINE.write_text(json.dumps(cov, indent=2) + "\n")
        print(f"baseline frozen in {BASELINE.name}: {cov}")
        return

    base = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
    print(f"{'module':<12} {'now':>6} {'base':>6} {'delta':>7}  status")
    print("-" * 45)
    ok = True
    for m in CRITICAL:
        now = cov.get(m)
        if now is None:
            continue
        b = base.get(m)
        if b is None:
            print(f"{m:<12} {now:>6} {'-':>6} {'-':>7}  NO BASELINE")
            ok = False
            continue
        d = round(now - b, 1)
        status = "OK" if now >= b else "REGRESSION"
        if now < b:
            ok = False
        print(f"{m:<12} {now:>6} {b:>6} {d:>+7}  {status}")
    tn = sum(cov.values()) / len(cov) if cov else 0
    tb = sum(base.values()) / len(base) if base else 0
    print("-" * 45)
    print(f"{'MEAN':<12} {tn:>6.1f} {tb:>6.1f} {tn - tb:>+7.1f}")
    sys.exit(0 if ok else 1)


main()
