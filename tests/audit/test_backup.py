"""Testes de backup e restore com verificação de integridade."""
import pytest
import tempfile
import json
from pathlib import Path
from audit.backup import LedgerBackup


@pytest.fixture
def sample_entries(_entry):
    entries = []
    prev_hash = None
    for i in range(5):
        entry = _entry(trace_id=f"trace-{i}", entry_hash=f"hash{i}", previous_hash=prev_hash)
        entries.append(entry)
        prev_hash = entry.entry_hash
    return entries


def test_export_creates_valid_backup(sample_entries):
    backup = LedgerBackup()
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = str(Path(tmpdir) / "backup.json")
        metadata = backup.export_to_file(sample_entries, output_path)
        assert metadata["entry_count"] == 5
        assert metadata["checksum"].startswith("sha256:")
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["version"] == "1.0"
        assert len(data["entries"]) == 5


def test_import_restores_entries(sample_entries):
    backup = LedgerBackup()
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = str(Path(tmpdir) / "backup.json")
        backup.export_to_file(sample_entries, output_path)
        restored = backup.import_from_file(output_path)
        assert len(restored) == 5
        for orig, rest in zip(sample_entries, restored):
            assert orig.trace_id == rest.trace_id


def test_backup_integrity_verification(sample_entries):
    backup = LedgerBackup()
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = str(Path(tmpdir) / "backup.json")
        backup.export_to_file(sample_entries, output_path)
        assert backup.verify_backup(output_path) is True


def test_backup_detects_tampering(sample_entries):
    backup = LedgerBackup()
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = str(Path(tmpdir) / "backup.json")
        backup.export_to_file(sample_entries, output_path)
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["entries"][0]["trace_id"] = "tampered-trace"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        assert backup.verify_backup(output_path) is False
        with pytest.raises(ValueError, match="Checksum mismatch"):
            backup.import_from_file(output_path)


def test_backup_handles_empty_ledger():
    backup = LedgerBackup()
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = str(Path(tmpdir) / "backup.json")
        metadata = backup.export_to_file([], output_path)
        assert metadata["entry_count"] == 0
        restored = backup.import_from_file(output_path)
        assert len(restored) == 0


def test_backup_preserves_order(sample_entries):
    backup = LedgerBackup()
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = str(Path(tmpdir) / "backup.json")
        backup.export_to_file(sample_entries, output_path)
        restored = backup.import_from_file(output_path)
        for orig, rest in zip(sample_entries, restored):
            assert orig.trace_id == rest.trace_id
