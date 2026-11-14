# Regras aplicadas

## Matriz de rastreabilidade
- Cada regra tem: requirement_id, source_norm, rule_id, test_id, audit_log_id
- Status: "complete" | "missing_test" | "missing_approval"
- get_missing_tests() retorna regras sem teste
- get_missing_approvals() retorna regras sem aprovação
- validate_completeness() calcula taxa de completude

## Model cards e fichas de dados
- Gerados a partir de metadados reais do sistema
- Exportáveis em Markdown
- Secções padronizadas (intended use, limitations, bias, ethics)
- Timestamps automáticos (created_at, last_updated)

## Mapeamento para frameworks
- EU AI Act (2024): Artigos 9-13 (gestão de riscos, dados, documentação, logging, transparência)
- RGPD (2016/679): Artigos 5, 13-15, 17, 22 (decisões automatizadas)
- Coverage rate: requisitos cobertos / total de requisitos
- map_rule_to_requirement() liga regra do sistema a requisito do framework

## Registo de riscos
- Severity: LOW | MEDIUM | HIGH | CRITICAL
- Likelihood: RARE | UNLIKELY | POSSIBLE | LIKELY | ALMOST_CERTAIN
- Risk score = severity_score × likelihood_score (1-20)
- Status: "open" | "mitigated" | "accepted" | "closed"

## Checklist de conformidade
- Itens categorizados: legal, technical, ethical, operational
- check_item() marca item como verificado com notas e responsável
- sign() adiciona reviewer_name, reviewer_role, signature, review_date
- completion_rate() calcula percentagem de itens verificados
