"""Unit tests for rule parsing, activation guards and evaluation.

Invariants exercised:
- only ACTIVE rules are evaluated (maker-checker)
- activation requires positive AND negative test cases
- missing data must never satisfy a HARD rule
"""
import pytest
from policy.models import Rule, RuleSeverity, RuleStatus, RuleTestCase
from policy.registry import RuleRegistry
from policy.engine import RuleEvaluator


def _draft(rid, expr, cases):
    return Rule(
        id=rid, version="1.0.0", name="Test rule", description="Test",
        severity=RuleSeverity.HARD, author="author",
        expression=expr, status=RuleStatus.DRAFT, test_cases=cases,
    )


def _active_rule_set(rid, expr, cases):
    """Full maker-checker flow: DRAFT -> REVIEWED -> APPROVED -> ACTIVE."""
    reg = RuleRegistry()
    reg.create_rule(_draft(rid, expr, cases))
    reg.review_rule(rid, "checker")
    reg.approve_rule(rid, "checker")
    reg.activate_rule(rid)
    reg.create_rule_set("test", "1.0.0", [rid])
    return reg.get_rule_set("1.0.0")


class TestRuleParser:
    def test_valid_rule_creation(self):
        rule = _draft("R-001", "idade >= 18", [])
        assert rule.id == "R-001"
        assert rule.severity == RuleSeverity.HARD

    def test_duplicate_rule_id_rejected(self):
        reg = RuleRegistry()
        rule = _draft("R-DUP", "idade >= 18", [])
        reg.create_rule(rule)
        with pytest.raises(ValueError, match="existe"):
            reg.create_rule(rule)

    def test_activation_requires_test_cases(self):
        """Invariant: a rule without test cases can never become ACTIVE."""
        reg = RuleRegistry()
        reg.create_rule(_draft("R-NOTEST", "idade >= 18", []))
        reg.review_rule("R-NOTEST", "checker")
        reg.approve_rule("R-NOTEST", "checker")
        with pytest.raises(ValueError, match="casos de teste"):
            reg.activate_rule("R-NOTEST")

    def test_draft_rule_is_not_evaluated(self):
        """Maker-checker: DRAFT rules must never influence decisions."""
        reg = RuleRegistry()
        reg.create_rule(_draft("R-DRAFT", "idade >= 18", []))
        reg.create_rule_set("test", "1.0.0", ["R-DRAFT"])
        ev = RuleEvaluator(reg.get_rule_set("1.0.0"))
        results = ev.evaluate({"idade": 25})
        assert not any(r.get("passed") for r in results), "DRAFT rule must not pass"

    def test_boundary_conditions(self):
        cases = [
            RuleTestCase(input_data={"rendimento": 1000}, expected_result=True),
            RuleTestCase(input_data={"rendimento": 999}, expected_result=False),
        ]
        rs = _active_rule_set("R-B", "rendimento >= 1000", cases)
        ev = RuleEvaluator(rs)
        for value, expected in [(999, False), (1000, True), (1001, True)]:
            results = ev.evaluate({"rendimento": value})
            assert len(results) == 1, f"Expected 1 result at rendimento={value}, got {len(results)}"
            assert results[0]["passed"] == expected, f"Boundary failed at rendimento={value}"

    def test_missing_data_never_approves(self):
        """Safety property: missing data must never produce passed=True."""
        cases = [
            RuleTestCase(input_data={"idade": 18}, expected_result=True),
            RuleTestCase(input_data={"idade": 17}, expected_result=False),
        ]
        rs = _active_rule_set("R-M", "idade >= 18", cases)
        ev = RuleEvaluator(rs)
        results = ev.evaluate({})
        assert not any(r.get("passed") for r in results), "Missing data approved a HARD rule"
