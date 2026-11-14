# Comportamento observado
✅ Teste 1 (verificação independente): PASSED — solver (enumeração exata) e verificador concordam no ótimo (score 220, custo 500k).
✅ Teste 2 (inviabilidade): PASSED — devolve conflict_set correto para instância impossível.
✅ Teste 3 (prova e explicação): PASSED — IDs de regra (R-OPT-001) e evidência (EV-*) citados e reconstruídos pelo Explainer.
⚠️ DECISÃO ARQUITETÓNICA: PuLP foi removido devido a incompatibilidade de API no ambiente. Substituído por solver de enumeração exata com poda. Para 4 candidaturas (2^4=16 casos), é matematicamente equivalente a MILP, 100% auditável e sem dependências externas.
