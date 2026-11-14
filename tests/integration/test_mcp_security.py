"""Testes de segurança MCP."""
import pytest
from integration.mcp_security import MCPInputValidator, MCPSecurityLogger


def test_safe_input_passes():
    v = MCPInputValidator()
    result = v.validate_and_sanitize({"query": "SELECT name FROM users", "name": "Joao"})
    assert result["valid"] is True
    assert result["sanitized"]["name"] == "Joao"


def test_sql_injection_detected():
    v = MCPInputValidator()
    result = v.validate_and_sanitize({"query": "x; DROP TABLE users; --"})
    assert result["valid"] is False
    assert "injection" in result["error"].lower()


def test_path_traversal_detected():
    v = MCPInputValidator()
    result = v.validate_and_sanitize({"path": "../../../etc/passwd"})
    assert result["valid"] is False
    assert "traversal" in result["error"].lower()


def test_command_injection_detected():
    v = MCPInputValidator()
    result = v.validate_and_sanitize({"cmd": "'; rm -rf /; echo '"})
    assert result["valid"] is False


def test_audit_logger_records_calls():
    logger = MCPSecurityLogger()
    logger.log_tool_call("tool1", "t1", "u1", {"a": 1}, success=True)
    logger.log_tool_call("tool2", "t1", "u1", {"b": 2}, success=False, error="denied")
    logger.log_tool_call("tool3", "t2", "u2", {}, success=True)
    
    all_logs = logger.get_audit_logs()
    assert len(all_logs) == 3
    
    t1_logs = logger.get_audit_logs(entity_id="t1")
    assert len(t1_logs) == 2
    assert all(l["entity_id"] == "t1" for l in t1_logs)


def test_audit_logger_captures_errors():
    logger = MCPSecurityLogger()
    logger.log_tool_call("t", "e1", "u1", {}, success=False, error="timeout")
    logs = logger.get_audit_logs()
    assert logs[0]["error"] == "timeout"
    assert logs[0]["success"] is False
