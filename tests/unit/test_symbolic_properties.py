"""Property-based tests for the symbolic reasoning core.

Properties verified:
1. Determinism: same rules + same facts -> same verdict (always)
2. Consistency: contradictory rules -> exactly one holds, never both/neither
3. Completeness: insufficient data/evidence -> never a strong approval
4. Semantics: engine result matches Python semantics of the expression
5. Robustness: arbitrary inputs never crash gate or engine

Registry maker-checker flow is tested in test_rule_parser.py / test_policy.py;
here we exercise the engine directly via RuleSet (rules ACTIVE by construction).
"""
import pytest
from hypothesis import given, strategies as st, settings
from policy.models import Rule, RuleSeverity, RuleStatus, RuleSet
from policy.engine import RuleEvaluator
from core.models import Proposal, TraceID, VerdictStatus
from gate.gate import Gate
from gate.validator import GateValidator


def _active_set(rules):
    """RuleSet with ACTIVE rules, bypassing the registry (engine-level properties)."""
    return RuleSet(version="1.0.0", name="prop", rules=rules)


def _rule(rid, expr):
    return Rule(
        id=rid, version="1.0.0", name=f"Rule {rid}", description="Property test rule",
        severity=RuleSeverity.HARD, author="test", expression=expr,
        status=RuleStatus.ACTIVE, test_cases=[],
    )


class TestDeterminism:
    @given(val=st.integers(min_value=0, max_value=100))
    @settings(max_examples=50)
    def test_same_input_same_verdict(self, val):
        ev = RuleEvaluator(_active_set([_rule("R-DET", "val >= 10")]))
        results = [ev.evaluate({"val": val}) for _ in range(10)]
        assert all(r == results[0] for r in results), f"Non-deterministic at val={val}"


class TestConsistency:
    @given(val=st.integers(min_value=-100, max_value=100))
    @settings(max_examples=50)
    def test_contradiction_exactly_one_holds(self, val):
        """Complementary rules: exactly one passes for any val (no arbitrariness)."""
        ev = RuleEvaluator(_active_set([
            _rule("R-GE", "val >= 10"),
            _rule("R-LT", "val < 10"),
        ]))
        results = ev.evaluate({"val": val})
        passed = sum(1 for r in results if r["passed"])
        assert passed == 1, f"val={val}: {passed} rules passed (expected exactly 1)"


class TestCompleteness:
    @given(data=st.sampled_from([{}, {"other": 15}, {"val": None}]))
    @settings(max_examples=30)
    def test_missing_data_never_approves(self, data):
        ev = RuleEvaluator(_active_set([_rule("R-COMP", "val >= 10")]))
        results = ev.evaluate(data)
        assert not any(r["passed"] for r in results), f"Approved with data={data}"

    def test_insufficient_evidence_repair_then_escalate(self):
        """Gate cycle: repair (1 of 2), then escalate with human approval required."""
        gate = Gate(GateValidator())
        p = Proposal(trace_id=TraceID(), agent="test",
                     content={"claim": "valor elevado"}, confidence=0.9)
        ctx = {
            "claims_to_verify": [{"text": "valor", "source_id": "MISSING",
                                  "requires_evidence": True}],
            "available_evidences": [],
        }
        r1 = gate.evaluate(p, ctx)
        assert r1["verdict"].status == VerdictStatus.REPAIRED
        r2 = gate.evaluate(p, ctx, repair_attempt=2)
        assert r2["verdict"].status == VerdictStatus.ESCALATED
        assert r2["needs_human_approval"] is True


class TestFuzzing:
    @given(age=st.integers(min_value=0, max_value=150),
           area=st.integers(min_value=0, max_value=1000),
           tax=st.booleans())
    @settings(max_examples=100)
    def test_fuzz_proposal_inputs(self, age, area, tax):
        gate = Gate(GateValidator())
        p = Proposal(trace_id=TraceID(), agent="fuzz",
                     content={"age": age, "area": area, "tax_paid": tax},
                     confidence=0.9)
        result = gate.evaluate(p)
        assert result["verdict"] is not None
        assert result["verdict"].status in {
            VerdictStatus.APPROVED, VerdictStatus.REJECTED,
            VerdictStatus.ESCALATED, VerdictStatus.REPAIRED,
        }

    @given(val1=st.integers(min_value=-1000, max_value=1000),
           val2=st.integers(min_value=-1000, max_value=1000),
           probe=st.integers(min_value=-1500, max_value=1500))
    @settings(max_examples=100)
    def test_engine_matches_python_semantics(self, val1, val2, probe):
        """Semantic property: engine verdict == Python truth of the expression."""
        ev = RuleEvaluator(_active_set(
            [_rule("R-FUZZ", f"val >= {val1} and val <= {val2}")]))
        results = ev.evaluate({"val": probe})
        expected = val1 <= probe <= val2
        assert len(results) == 1
        assert results[0]["passed"] == expected, (
            f"val={probe}, range=[{val1},{val2}]: engine={results[0]['passed']}, "
            f"python={expected}")


class TestRegression:
    """Regressions found by fuzzing on 2026-11-14.

    Bug 1: ast.BoolOp missing from ALLOWED_NODES made the And/Or branch
           unreachable: every conjunctive rule returned ERROR/passed=False.
    Bug 2: None in an ordering comparison raised TypeError out of the engine.
    """

    def test_conjunction_rule_evaluates(self):
        ev = RuleEvaluator(_active_set([_rule("R-AND", "val >= 0 and val <= 0")]))
        results = ev.evaluate({"val": 0})
        assert results[0]["passed"] is True
        assert results[0]["verdict"] == "PASS"

    def test_disjunction_rule_evaluates(self):
        ev = RuleEvaluator(_active_set([_rule("R-OR", "val < 0 or val > 10")]))
        assert ev.evaluate({"val": 20})[0]["passed"] is True
        assert ev.evaluate({"val": 5})[0]["passed"] is False

    def test_null_data_fails_closed_without_crash(self):
        ev = RuleEvaluator(_active_set([_rule("R-NULL", "val >= 10")]))
        results = ev.evaluate({"val": None})
        assert results[0]["passed"] is False

    def test_wrong_type_fails_closed_without_crash(self):
        ev = RuleEvaluator(_active_set([_rule("R-TYPE", "val >= 10")]))
        results = ev.evaluate({"val": "dez"})
        assert results[0]["passed"] is False
        assert results[0]["verdict"] == "ERROR"


    def test_negative_literal_bounds_evaluate(self):
        """Regression: -1 parsed as UnaryOp(USub, Constant(1)) must work.

        Before fix: raised SecurityError, rule returned ERROR/passed=False
        silently. Rules with negative bounds never worked."""
        ev = RuleEvaluator(_active_set([_rule("R-NEG", "val >= -1 and val <= 0")]))
        r0 = ev.evaluate({"val": 0})[0]
        r_neg = ev.evaluate({"val": -1})[0]
        r_out = ev.evaluate({"val": 1})[0]
        assert r0["passed"] is True and r0["verdict"] == "PASS"
        assert r_neg["passed"] is True
        assert r_out["passed"] is False
