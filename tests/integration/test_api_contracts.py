"""Testes de contratos de API versionados."""
import pytest
from integration.api_contracts import APIContractValidator


def test_v1_valid_request():
    v = APIContractValidator(version="v1")
    result = v.validate_request({"document_text": "test", "metadata": {}})
    assert result["valid"] is True
    assert result["normalized"]["priority"] == "normal"  # default


def test_v1_missing_required_field():
    v = APIContractValidator(version="v1")
    result = v.validate_request({"metadata": {}})
    assert result["valid"] is False
    assert "document_text" in result["error"]


def test_v1_invalid_priority():
    v = APIContractValidator(version="v1")
    result = v.validate_request({"document_text": "test", "priority": "invalid"})
    assert result["valid"] is False


def test_v2_accepts_callback_url():
    v = APIContractValidator(version="v2")
    result = v.validate_request({
        "document_text": "test",
        "callback_url": "https://example.com/hook",
    })
    assert result["valid"] is True
    assert result["normalized"]["callback_url"] == "https://example.com/hook"


def test_response_valid():
    v = APIContractValidator(version="v1")
    result = v.validate_response({
        "trace_id": "t1", "status": "approved", "timestamp": "2026-01-01T00:00:00Z"
    })
    assert result["valid"] is True


def test_response_invalid_status():
    v = APIContractValidator(version="v1")
    result = v.validate_response({
        "trace_id": "t1", "status": "banana", "timestamp": "now"
    })
    assert result["valid"] is False
    assert "status" in result["error"]


def test_response_missing_required():
    v = APIContractValidator(version="v1")
    result = v.validate_response({"trace_id": "t1"})
    assert result["valid"] is False


def test_unsupported_version():
    with pytest.raises(ValueError):
        APIContractValidator(version="v99")
