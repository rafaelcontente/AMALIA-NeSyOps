# Comportamento esperado
1. O resultado do solver é confirmado por um verificador independente (recálculo das restrições em código simples) em 100% dos casos.
2. Uma instância deliberadamente impossível devolve "inviável" e o conjunto mínimo de regras em conflito.
3. A prova devolvida cita ids de regra e de evidência, e explain consegue reconstruir cada passo a partir dela.
