# Regras de Avaliação

## 1. Golden Sets e Regressão
- **Limiar mínimo**: 95% accuracy para passar CI
- **Detecção de regressão**: Qualquer queda abaixo do limiar falha automaticamente
- **Rastreabilidade**: Todas as regressões listadas com item_id, expected vs predicted
- **Categorias**: Itens organizados por categoria (ex: "extração de datas")

## 2. Red Teaming e Segurança
- **Zero tolerância**: Nenhum ataque de injeção pode alterar decisões
- **Bateria padrão**: 5 tipos de ataques de injeção testados
- **Decisões robustas**: Funções de decisão ignoram campos suspeitos
- **Métrica**: `success_rate` deve ser 0.0

## 3. Baseline Comparison
- **Baseline obrigatório**: Todo sistema deve ter baseline simples (só regras)
- **Medição contínua**: Baseline e modelo avaliados nos mesmos dados
- **Justificação automática**: Se improvement < 5%, relatório pede justificação
- **Transparência**: Relatório mostra baseline_accuracy vs model_accuracy

## 4. Qualidade de Código
- **Timezone-aware**: Usar `datetime.now(timezone.utc)` em vez de `datetime.utcnow()`
- **Zero warnings**: Nenhum DeprecationWarning permitido
- **Type hints**: Todos os modelos Pydantic com tipos explícitos

## 5. Relatórios de Avaliação
- **Status automático**: pass/fail/warning baseado em critérios
- **Critical issues**: Lista de problemas críticos bloqueantes
- **Recommendations**: Sugestões de melhoria automáticas
- **Exportável**: Relatório em formato estruturado (JSON/Markdown)
