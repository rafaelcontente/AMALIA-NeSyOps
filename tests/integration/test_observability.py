"""Testes de observabilidade: tracing, métricas, correlation IDs."""
import pytest
from integration.observability import TracingManager, MetricsCollector, CorrelationIDGenerator


def test_correlation_id_uniqueness():
    gen = CorrelationIDGenerator()
    ids = [gen.generate() for _ in range(100)]
    assert len(set(ids)) == 100
    assert all(len(i) >= 16 for i in ids)


def test_span_creation_and_attributes():
    mgr = TracingManager()
    span = mgr.start_span(operation="process", correlation_id="c1", entity_id="t1")
    span.set_attribute("doc_id", "d1")
    span.set_attribute("time_ms", 150)
    span.end()
    
    spans = mgr.get_spans(correlation_id="c1")
    assert len(spans) == 1
    assert spans[0]["operation"] == "process"
    assert spans[0]["attributes"]["doc_id"] == "d1"
    assert spans[0]["duration_ms"] >= 0


def test_nested_spans():
    mgr = TracingManager()
    parent = mgr.start_span(operation="request", correlation_id="c1")
    child1 = mgr.start_span(operation="validate", correlation_id="c1", parent_span=parent)
    child1.end()
    child2 = mgr.start_span(operation="process", correlation_id="c1", parent_span=parent)
    child2.end()
    parent.end()
    
    spans = mgr.get_spans(correlation_id="c1")
    assert len(spans) == 3
    
    children = [s for s in spans if s["parent_id"] == parent.span_id]
    assert len(children) == 2


def test_get_spans_filters_by_correlation():
    mgr = TracingManager()
    mgr.start_span(operation="a", correlation_id="c1").end()
    mgr.start_span(operation="b", correlation_id="c2").end()
    
    assert len(mgr.get_spans(correlation_id="c1")) == 1
    assert len(mgr.get_spans(correlation_id="c2")) == 1
    assert len(mgr.get_spans()) == 2


def test_counter_increment():
    mc = MetricsCollector()
    mc.increment_counter("req_total", {"method": "POST", "status": "200"})
    mc.increment_counter("req_total", {"method": "POST", "status": "200"})
    mc.increment_counter("req_total", {"method": "GET", "status": "404"})
    
    metrics = mc.get_metrics()
    assert metrics["req_total"]["method=POST:status=200"] == 2
    assert metrics["req_total"]["method=GET:status=404"] == 1


def test_histogram_observations():
    mc = MetricsCollector()
    mc.observe_histogram("duration", 0.10, {"endpoint": "/api"})
    mc.observe_histogram("duration", 0.25, {"endpoint": "/api"})
    mc.observe_histogram("duration", 0.15, {"endpoint": "/api"})
    
    metrics = mc.get_metrics()
    h = metrics["duration"]["/api"]
    assert h["count"] == 3
    assert abs(h["sum"] - 0.50) < 0.001
    assert abs(h["min"] - 0.10) < 0.001
    assert abs(h["max"] - 0.25) < 0.001
