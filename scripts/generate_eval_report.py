"""
Script para gerar relatório de avaliação versionado.
Gera artefactos JSON e Markdown com métricas globais, por categoria e delta em relação à baseline.
"""
import json
import pathlib
import subprocess
from datetime import datetime, timezone

def get_git_commit():
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
    except Exception:
        return "unknown"

def generate_evaluation_report(evaluator, decision_func, output_dir="reports"):
    # 1. Avaliar
    report_data = evaluator.evaluate(decision_func)
    
    # 2. Adicionar metadados
    report_data["git_commit"] = get_git_commit()
    report_data["generated_at"] = datetime.now(timezone.utc).isoformat()
    
    # 3. Calcular delta em relação ao relatório anterior
    out_dir = pathlib.Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    prev_report_path = out_dir / "evaluation_report_latest.json"
    
    if prev_report_path.exists():
        with open(prev_report_path, "r", encoding="utf-8") as f:
            prev_data = json.load(f)
        curr_acc = report_data["global_metrics"]["accuracy"]
        prev_acc = prev_data.get("global_metrics", {}).get("accuracy", 0.0)
        report_data["delta_accuracy"] = round(curr_acc - prev_acc, 4)
    else:
        report_data["delta_accuracy"] = 0.0
        
    # 4. Guardar JSON
    json_path = out_dir / "evaluation_report_latest.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
        
    # 5. Gerar Markdown
    md_lines = [
        "# Relatório de Avaliação - AMALIA-NeSyOps",
        "",
        f"**Gerado em:** {report_data['generated_at']}",
        f"**Commit Git:** `{report_data['git_commit']}`",
        f"**Versão do Golden Set:** {report_data['golden_set_version']}",
        f"**Total de Casos:** {report_data['global_metrics']['total_cases']}",
        "",
        "## Métricas Globais",
        f"- **Accuracy:** {report_data['global_metrics']['accuracy']:.4f} (Δ {report_data['delta_accuracy']:+.4f})",
        f"- **Precision:** {report_data['global_metrics']['precision']:.4f}",
        f"- **Recall:** {report_data['global_metrics']['recall']:.4f}",
        f"- **F1 Score:** {report_data['global_metrics']['f1_score']:.4f}",
        "",
        "## Métricas por Categoria",
        "| Categoria | Casos | Accuracy | Precision | Recall | F1 Score |",
        "|-----------|-------|----------|-----------|--------|----------|"
    ]
    
    for cat, metrics in sorted(report_data["category_metrics"].items()):
        md_lines.append(
            f"| {cat} | {metrics['total_cases']} | {metrics['accuracy']:.4f} | "
            f"{metrics['precision']:.4f} | {metrics['recall']:.4f} | {metrics['f1_score']:.4f} |"
        )
        
    md_lines.extend([
        "",
        "## Erros Detectados",
        f"Total de erros: {report_data['total_errors']}"
    ])
    
    if report_data["errors"]:
        md_lines.append("\n### Exemplos de Erros (Top 5)")
        for err in report_data["errors"][:5]:
            exp = err.get("expected_violated", [])
            pred = err.get("predicted_violated", [])
            md_lines.append(f"- **{err['case_id']}**: Esperado `{exp}`, Obtido `{pred}`")
            
    md_path = out_dir / "evaluation_report_latest.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
        
    return json_path, md_path

if __name__ == "__main__":
    from eval.category_evaluator import CategoryEvaluator
    
    evaluator = CategoryEvaluator("eval/golden_set_v3.json")
    
    # Função de decisão de exemplo (substituir pela integração real com o sistema)
    def mock_decision(case):
        return {
            "decision": case["expected_decision"],
            "rules_violated": case["expected_rules_violated"]
        }
        
    json_p, md_p = generate_evaluation_report(evaluator, mock_decision)
    print(f"Relatório gerado com sucesso:\n- JSON: {json_p}\n- Markdown: {md_p}")
