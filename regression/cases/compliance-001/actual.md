# Resultados observados

## Teste 1: Matriz de rastreabilidade
✅ 3 regras adicionadas à matriz
✅ R-012: source_norm="Lei n.º 123/2024, art. 45.º", test_id="T-044", status="complete"
✅ R-020: source_norm="Decreto-Lei n.º 456/2023, art. 12.º", test_id="T-045", status="complete"
✅ R-031: test_id="SEM_TESTE", status="missing_test" (sem teste e sem aprovação)
✅ Estatísticas: total_rules=3, complete=2, missing_tests=1, missing_approvals=0
✅ get_missing_tests() retorna [R-031]

## Teste 2: Reprodutibilidade do pacote
✅ Model card gerado duas vezes com mesmos metadados
✅ model_name="AMALIA", version="v0.3" idênticos
✅ metrics={"accuracy": 0.95, "precision": 0.93} idênticos
✅ Markdown exportável: "# Model Card: AMALIA v0.3" presente
✅ Mapeamento EU AI Act criado com 5 requisitos
✅ EU-AI-001 mapeado para R-012, EU-AI-002 mapeado para R-020
✅ coverage_rate > 0 (2 de 5 requisitos cobertos)

## Teste 3: Checklist assinada por jurista
✅ Checklist gerada com 10 itens (4 legais, 3 técnicos, 2 éticos, 2 operacionais)
✅ Estado inicial: complete=False, completion_rate=0.0
✅ Após verificar 4 itens: completion_rate=0.4
✅ LEGAL-001 verificado por "jurista-001" com nota "EU AI Act Art. 9 implementado"
✅ Após verificar todos os 10 itens: complete=True, completion_rate=1.0
✅ Assinatura: reviewer_name="Dra. Ana Silva", reviewer_role="jurist", signature="HASH-SHA256-ABC123"
✅ review_date definido automaticamente
✅ Markdown exportável contém "Dra. Ana Silva", "jurist" e "HASH-SHA256-ABC123"

## Documentação gerada
✅ Model card com secções: Descrição, Uso Previsto, Desempenho, Limitações, Viés, Formação, Ética
✅ Data sheet com secções: Composição, Recolha, Pré-processamento, Usos, Distribuição, Manutenção
✅ Matriz de rastreabilidade em formato Markdown com tabela
✅ Registo de riscos com score (severity × likelihood)
✅ Mapeamento EU AI Act com taxa de cobertura
✅ Checklist de conformidade com itens categorizados
