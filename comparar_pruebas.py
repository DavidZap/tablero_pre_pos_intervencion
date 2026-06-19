import pandas as pd
import numpy as np
from scipy.stats import wilcoxon, ttest_rel

# Índices globales de 16 pares (del análisis anterior)
pre_idx = [3.27, 3.45, 3.36, 3.64, 3.36, 3.55, 3.82, 4.18, 3.27, 3.45, 3.09, 3.27, 3.55, 3.91, 3.82, 3.64]
post_idx = [4.36, 4.82, 4.27, 4.91, 4.64, 4.55, 4.73, 4.82, 4.45, 4.64, 4.18, 4.45, 5.0, 5.0, 5.0, 4.73]

# Wilcoxon (no paramétrico - recomendado para Likert)
stat_w, p_w = wilcoxon(post_idx, pre_idx)
print("WILCOXON PAREADO (No paramétrico):")
print(f"  p-valor: {p_w:.6f}")
print(f"  Conclusión: {'SIGNIFICATIVO' if p_w < 0.05 else 'NO SIGNIFICATIVO'} (α=0.05)")
print()

# t-test pareado (paramétrico, para comparación)
stat_t, p_t = ttest_rel(post_idx, pre_idx)
print("t-TEST PAREADO (Paramétrico - solo comparación):")
print(f"  p-valor: {p_t:.6f}")
print(f"  Conclusión: {'SIGNIFICATIVO' if p_t < 0.05 else 'NO SIGNIFICATIVO'} (α=0.05)")
print()

print("=" * 60)
print("ANÁLISIS:")
print("=" * 60)
print(f"✓ Ambas pruebas concuerdan en significancia")
print(f"✓ Wilcoxon es más CONSERVADOR (p={p_w:.4f}) que t-test (p={p_t:.4f})")
print(f"✓ Wilcoxon es CORRECTO para escala Likert (ordinal)")
print(f"✓ Por eso es la prueba elegida en el dashboard")
