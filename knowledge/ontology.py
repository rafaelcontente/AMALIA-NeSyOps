"""
Grafo de conhecimento com ontologia temporal.
Representa normas, artigos e relações (altera, revoga) com períodos de vigência.
"""
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from datetime import datetime

# Namespace próprio
NE = Namespace("http://amalia-neysyops.pt/ontology#")

class KnowledgeGraph:
    def __init__(self):
        self.graph = Graph()
        self.graph.bind("ne", NE)
    
    def add_norm(self, norm_id: str, title: str, valid_from: str, valid_to: str = None):
        """Adiciona uma norma com período de vigência."""
        norm_uri = URIRef(f"{NE}{norm_id}")
        self.graph.add((norm_uri, RDF.type, NE.Norm))
        self.graph.add((norm_uri, RDFS.label, Literal(title)))
        self.graph.add((norm_uri, NE.validFrom, Literal(valid_from, datatype=XSD.date)))
        if valid_to:
            self.graph.add((norm_uri, NE.validTo, Literal(valid_to, datatype=XSD.date)))
    
    def add_article(self, norm_id: str, article_id: str, content: str):
        """Adiciona um artigo a uma norma."""
        norm_uri = URIRef(f"{NE}{norm_id}")
        article_uri = URIRef(f"{NE}{article_id}")
        self.graph.add((article_uri, RDF.type, NE.Article))
        self.graph.add((article_uri, NE.partOf, norm_uri))
        self.graph.add((article_uri, NE.textContent, Literal(content)))
    
    def add_relation(self, source_id: str, relation: str, target_id: str):
        """Adiciona relação entre normas (altera, revoga, remetePara)."""
        source_uri = URIRef(f"{NE}{source_id}")
        target_uri = URIRef(f"{NE}{target_id}")
        rel_uri = getattr(NE, relation)
        self.graph.add((source_uri, rel_uri, target_uri))
    
    def query_active_norms(self, date_str: str):
        """Consulta normas vigentes numa data específica."""
        query = f"""
        PREFIX ne: <http://amalia-neysyops.pt/ontology#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?norm ?title WHERE {{
            ?norm a ne:Norm ;
                  rdfs:label ?title ;
                  ne:validFrom ?from .
            FILTER(?from <= "{date_str}"^^xsd:date)
            OPTIONAL {{ ?norm ne:validTo ?to }}
            FILTER(!BOUND(?to) || ?to >= "{date_str}"^^xsd:date)
        }}
        """
        return list(self.graph.query(query))
