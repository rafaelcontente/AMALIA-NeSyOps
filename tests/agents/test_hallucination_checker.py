"""Testes de validação anti-alucinação."""
import pytest
from rdflib import Graph, URIRef, Literal, RDF, RDFS
from agents.hallucination_checker import HallucinationChecker


@pytest.fixture
def knowledge_graph():
    g = Graph()
    g.add((URIRef("http://example.org/person/1"), RDF.type, URIRef("http://example.org/Person")))
    g.add((URIRef("http://example.org/person/1"), RDFS.label, Literal("João Silva")))
    g.add((URIRef("http://example.org/org/1"), RDF.type, URIRef("http://example.org/Organization")))
    g.add((URIRef("http://example.org/org/1"), RDFS.label, Literal("Câmara de Lisboa")))
    return g


@pytest.fixture
def checker(knowledge_graph):
    return HallucinationChecker(knowledge_graph)


def test_valid_entities_pass(checker):
    entities = {"person": "João Silva", "organization": "Câmara de Lisboa"}
    result = checker.check_entities(entities)
    assert result["valid"] is True
    assert len(result["hallucinated"]) == 0
    assert result["checked_count"] == 2


def test_hallucinated_entity_detected(checker):
    entities = {"person": "João Silva", "organization": "Entidade Fictícia"}
    result = checker.check_entities(entities)
    assert result["valid"] is False
    assert "organization:Entidade Fictícia" in result["hallucinated"]
    assert len(result["hallucinated"]) == 1


def test_multiple_hallucinations(checker):
    entities = {
        "person": "Pessoa Inexistente",
        "organization": "Org Fictícia",
        "location": "Cidade Imaginária",
    }
    result = checker.check_entities(entities)
    assert result["valid"] is False
    assert len(result["hallucinated"]) == 3


def test_filter_by_entity_type(checker):
    entities = {"person": "João Silva", "organization": "Entidade Fictícia"}
    result = checker.check_entities(entities, entity_type="person")
    assert result["valid"] is True
    assert len(result["hallucinated"]) == 0
    
    result = checker.check_entities(entities, entity_type="organization")
    assert result["valid"] is False
    assert len(result["hallucinated"]) == 1


def test_empty_entities(checker):
    result = checker.check_entities({})
    assert result["valid"] is True
    assert len(result["hallucinated"]) == 0
    assert result["checked_count"] == 0
