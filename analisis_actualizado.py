import pandas as pd
import numpy as np
import unicodedata, re
from scipy.stats import wilcoxon
from pathlib import Path

LIKERT_MAP = {
    "totalmente en desacuerdo": 1,
    "en desacuerdo": 2,
    "ni de acuerdo ni en desacuerdo": 3,
    "neutral": 3,
    "de acuerdo": 4,
    "totalmente de acuerdo": 5,
}

def norm(v):
    if pd.isna(v): return ""
    t = str(v).strip().lower()
    t = unicodedata.normalize('NFKD', t).encode('ascii','ignore').decode('ascii')
    t = re.sub(r'\s+', ' ', t)
    return t

def map_series(s):
    return s.map(lambda x: LIKERT_MAP.get(norm(x), np.nan))

raw = Path('data/raw')
pre = pd.read_excel(raw / 'Experiencia_en_el_uso_de_Power_App_B-Lab.xlsx')
post = pd.read_excel(raw / 'Experiencia_en_el_uso_de_Power_App_B-Lab - postest.xlsx')

pre['Correo electrónico'] = pre['Correo electrónico'].astype(str).str.strip().str.lower()
post['Correo electrónico'] = post['Correo electrónico'].astype(str).str.strip().str.lower()

qs = [c for c in pre.columns if c in post.columns and c not in [
    'Id','Hora de inicio','Hora de finalización','Correo electrónico','Nombre',
    'Si pudieras cambiar solo una cosa para mejorar la Power App, ¿Cuál sería?',
    'En tu día a día, ¿Qué te impediría hacer uso de la PowerApp?'
]]

pre_num = pre[['Correo electrónico'] + qs].copy()
post_num = post[['Correo electrónico'] + qs].copy()

for q in qs:
    pre_num[q] = map_series(pre_num[q])
    post_num[q] = map_series(post_num[q])

df = pre_num.merge(post_num, on='Correo electrónico', suffixes=('_pre', '_post'))

print(f'Pretest personas únicas: {pre["Correo electrónico"].nunique()}')
print(f'Postest personas únicas: {post["Correo electrónico"].nunique()}')
print(f'Pares comparables: {df.shape[0]}')
print(f'Preguntas Likert: {len(qs)}')

pre_cols = [f'{q}_pre' for q in qs]
post_cols = [f'{q}_post' for q in qs]

pre_vals = df[pre_cols].to_numpy(dtype=float).ravel()
post_vals = df[post_cols].to_numpy(dtype=float).ravel()
pre_vals = pre_vals[~np.isnan(pre_vals)]
post_vals = post_vals[~np.isnan(post_vals)]

person_pre = df[pre_cols].mean(axis=1, skipna=True)
person_post = df[post_cols].mean(axis=1, skipna=True)
person_valid = person_pre.notna() & person_post.notna()

print(f'\nPares con índice global válido: {int(person_valid.sum())}')
print(f'Índice global pre: {float(person_pre[person_valid].mean()):.3f}')
print(f'Índice global post: {float(person_post[person_valid].mean()):.3f}')
delta_global = float(person_post[person_valid].mean() - person_pre[person_valid].mean())
print(f'Delta global: {delta_global:+.3f}')

p_global = float(wilcoxon(person_post[person_valid], person_pre[person_valid], zero_method='wilcox', alternative='two-sided').pvalue)
print(f'p-valor Wilcoxon pareado: {p_global:.6f}')

if p_global < 0.05 and delta_global > 0:
    print('\n✓ RESULTADO: LA INTERVENCIÓN FUE SIGNIFICATIVA')
else:
    print(f'\n✗ RESULTADO: No significativa (p={p_global:.4f} vs 0.05)')

# Tabla de resultados por pregunta
rows = []
for q in qs:
    pre_q = df[f'{q}_pre']
    post_q = df[f'{q}_post']
    valid = pre_q.notna() & post_q.notna()
    if valid.sum() == 0: continue
    pre_v = pre_q[valid]
    post_v = post_q[valid]
    delta_v = post_v - pre_v
    rows.append({
        'pregunta': q[:60] + '...' if len(q) > 60 else q,
        'n_pares': int(valid.sum()),
        'pre_mean': float(pre_v.mean()),
        'post_mean': float(post_v.mean()),
        'delta': float(delta_v.mean()),
        'mejoran_%': float((delta_v > 0).mean() * 100),
    })

res = pd.DataFrame(rows).sort_values('delta', ascending=False)
print('\nTop 5 preguntas con mayor mejora:')
print(res.head(5)[['pregunta', 'n_pares', 'delta', 'mejoran_%']].to_string(index=False))
