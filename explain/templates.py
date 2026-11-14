"""
Templates de explicações em português europeu claro.
Adverse Action Notices para decisões desfavoráveis.
"""

CITIZEN_APPROVED = """
A sua candidatura foi **aprovada**.

**Motivo:** {reason}

**Próximos passos:** {next_steps}

**Referências:** {references}

Se tiver dúvidas, contacte-nos através dos canais oficiais.
"""

CITIZEN_REJECTED = """
A sua candidatura foi **indeferida**.

**Motivo da decisão:** {reason}

**Fundamentação legal:** {legal_basis}

**Direito de recurso:** Tem direito a reclamar desta decisão no prazo de {appeal_deadline} dias úteis, nos termos do artigo {appeal_article} do {appeal_law}.

**Referências:** {references}

Para exercer o seu direito de recurso, contacte-nos através dos canais oficiais.
"""

AUDITOR_VIEW = """
=== VISTA DO AUDITOR ===

**Trace ID:** {trace_id}
**Timestamp:** {timestamp}
**Status:** {status}

**Versões do sistema:**
- Modelo: {model_version}
- Prompt: {prompt_version}
- Regras: {rules_version}

**Árvore de prova:**
{proof_tree}

**Regras avaliadas:**
{rules_evaluated}

**Regras violadas:**
{rules_violated}

**Evidências consultadas:**
{evidences}
"""
