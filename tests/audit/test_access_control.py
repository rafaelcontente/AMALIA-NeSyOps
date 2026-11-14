"""Testes de controlo de acesso ao ledger."""
import pytest
from audit.access_control import LedgerAccessControl


@pytest.fixture
def acl():
    return LedgerAccessControl()


def test_grant_and_check_reader_role(acl):
    acl.grant_role("user-1", "reader")
    assert acl.has_permission("user-1", "read") is True
    assert acl.has_permission("user-1", "write") is False
    assert acl.has_permission("user-1", "admin") is False


def test_grant_and_check_writer_role(acl):
    acl.grant_role("user-1", "writer")
    assert acl.has_permission("user-1", "read") is True
    assert acl.has_permission("user-1", "write") is True
    assert acl.has_permission("user-1", "admin") is False


def test_grant_and_check_admin_role(acl):
    acl.grant_role("user-1", "admin")
    assert acl.has_permission("user-1", "read") is True
    assert acl.has_permission("user-1", "write") is True
    assert acl.has_permission("user-1", "admin") is True


def test_multiple_roles(acl):
    acl.grant_role("user-1", "reader")
    acl.grant_role("user-1", "writer")
    assert acl.has_permission("user-1", "read") is True
    assert acl.has_permission("user-1", "write") is True
    assert acl.has_permission("user-1", "admin") is False


def test_revoke_role(acl):
    acl.grant_role("user-1", "writer")
    assert acl.has_permission("user-1", "write") is True
    acl.revoke_role("user-1", "writer")
    assert acl.has_permission("user-1", "write") is False


def test_check_permission_raises_on_denied(acl):
    acl.grant_role("user-1", "reader")
    acl.check_permission("user-1", "read")
    with pytest.raises(PermissionError, match="does not have permission"):
        acl.check_permission("user-1", "write")


def test_invalid_role(acl):
    with pytest.raises(ValueError, match="Invalid role"):
        acl.grant_role("user-1", "superuser")


def test_access_log_records_attempts(acl):
    acl.grant_role("user-1", "reader")
    acl.check_permission("user-1", "read")
    try:
        acl.check_permission("user-1", "write")
    except PermissionError:
        pass
    
    log = acl.get_access_log()
    assert len(log) >= 2
    
    user1_log = acl.get_access_log(user_id="user-1")
    assert all(entry["user_id"] == "user-1" for entry in user1_log)


def test_unknown_user_has_no_permissions(acl):
    assert acl.has_permission("unknown-user", "read") is False
    assert acl.has_permission("unknown-user", "write") is False
    assert acl.has_permission("unknown-user", "admin") is False


def test_access_log_includes_timestamps(acl):
    acl.grant_role("user-1", "reader")
    acl.check_permission("user-1", "read")
    
    log = acl.get_access_log()
    assert len(log) > 0
    
    for entry in log:
        assert "timestamp" in entry
        assert "user_id" in entry
        assert "action" in entry
        assert "success" in entry
