"""Testes de verificação de integridade do ledger."""
import pytest
from datetime import datetime, timezone, timedelta
from audit.integrity import IntegrityChecker


@pytest.fixture
def checker():
    return IntegrityChecker()


def test_valid_chain_passes_integrity_check(checker, _entry):
    entries = []
    prev_hash = None
    for i in range(5):
        # Criar entry temporária para calcular o hash
        temp_entry = _entry(trace_id=f"trace-{i}", previous_hash=prev_hash)
        correct_hash = temp_entry.compute_hash()
        # Criar entry final com o mesmo ID, timestamp e hash correto
        entry_with_hash = _entry(
            id=temp_entry.id,
            timestamp=temp_entry.timestamp,  # Reutilizar timestamp
            trace_id=f"trace-{i}",
            previous_hash=prev_hash,
            entry_hash=correct_hash
        )
        entries.append(entry_with_hash)
        prev_hash = correct_hash
    result = checker.verify_integrity(entries)
    assert result["valid"] is True
    assert result["issue_count"] == 0


def test_detects_duplicate_ids(checker, _entry):
    entry1 = _entry(id="duplicate-id", trace_id="trace-1", entry_hash="hash1")
    entry2 = _entry(id="duplicate-id", trace_id="trace-2", entry_hash="hash2")
    result = checker.verify_integrity([entry1, entry2])
    assert result["valid"] is False
    duplicate_issues = [i for i in result["issues"] if i["type"] == "duplicate_id"]
    assert len(duplicate_issues) > 0


def test_detects_hash_mismatch(checker, _entry):
    entry = _entry(trace_id="trace-1", entry_hash="wrong_hash")
    result = checker.verify_integrity([entry])
    assert result["valid"] is False
    hash_issues = [i for i in result["issues"] if i["type"] == "hash_mismatch"]
    assert len(hash_issues) > 0


def test_detects_chain_break(checker, _entry):
    entry1 = _entry(trace_id="trace-1", entry_hash="hash1")
    entry2 = _entry(trace_id="trace-2", entry_hash="hash2", previous_hash="wrong_previous_hash")
    result = checker.verify_integrity([entry1, entry2])
    assert result["valid"] is False
    chain_issues = [i for i in result["issues"] if i["type"] == "chain_break"]
    assert len(chain_issues) > 0


def test_detects_timestamp_order_violation(checker, _entry):
    now = datetime.now(timezone.utc)
    entry1 = _entry(trace_id="trace-1", timestamp=now, entry_hash="hash1")
    entry2 = _entry(trace_id="trace-2", timestamp=now - timedelta(hours=1), entry_hash="hash2", previous_hash="hash1")
    result = checker.verify_integrity([entry1, entry2])
    assert result["valid"] is False
    timestamp_issues = [i for i in result["issues"] if i["type"] == "timestamp_order"]
    assert len(timestamp_issues) > 0


def test_quick_check_returns_boolean(checker, _entry):
    # Criar entrada com hash correto (reutilizar ID e timestamp)
    entry1 = _entry(trace_id="trace-1")
    correct_hash = entry1.compute_hash()
    entry1_correct = _entry(
        id=entry1.id,
        timestamp=entry1.timestamp,  # Reutilizar timestamp
        trace_id="trace-1",
        entry_hash=correct_hash
    )
    assert checker.quick_check([entry1_correct]) is True
    # Entrada com hash errado
    entry2 = _entry(trace_id="trace-2", entry_hash="wrong_hash")
    assert checker.quick_check([entry1_correct, entry2]) is False


def test_empty_ledger_is_valid(checker):
    result = checker.verify_integrity([])
    assert result["valid"] is True
    assert result["entry_count"] == 0
    assert result["issue_count"] == 0


def test_integrity_report_includes_metadata(checker, _entry):
    entry = _entry(trace_id="trace-1", entry_hash="hash1")
    result = checker.verify_integrity([entry])
    assert "verified_at" in result
    assert "entry_count" in result
    assert "valid" in result
    assert "issues" in result
    assert "issue_count" in result
