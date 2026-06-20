import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

# Cargar datos reales
pre_df = pd.read_excel("data/raw/Experiencia_en_el_uso_de_Power_App_B-Lab.xlsx")
post_df = pd.read_excel("data/raw/Experiencia_en_el_uso_de_Power_App_B-Lab - postest.xlsx")

print("=" * 60)
print("DATA STRUCTURE")
print("=" * 60)
print(f"PRE shape: {pre_df.shape}")
print(f"POST shape: {post_df.shape}")
print(f"PRE columns (first 5): {pre_df.columns.tolist()[:5]}")
print()

# Identificar columnas Likert (excluir metadatos)
all_cols = pre_df.columns.tolist()
likert_cols = [c for c in all_cols if c.lower() not in ['email', 'nombre', 'fecha', 'timestamp'] and not c.startswith('Unnamed')][:3]
print(f"Testing with columns: {likert_cols}")
print()

# Probar con una columna individual
test_col = likert_cols[0]
print("=" * 60)
print(f"TESTING COLUMN: {test_col}")
print("=" * 60)

pre_v = pd.Series(pre_df[test_col].dropna().values[:5])
post_v = pd.Series(post_df[test_col].dropna().values[:5])

print(f"pre_v: {pre_v.values} (type: {type(pre_v)}, dtype: {pre_v.dtype})")
print(f"post_v: {post_v.values} (type: {type(post_v)}, dtype: {post_v.dtype})")
print()

# Test 1: Series directly
print("-" * 60)
print("TEST 1: wilcoxon(Series, Series)")
print("-" * 60)
try:
    res = wilcoxon(post_v, pre_v, zero_method="wilcox", alternative="two-sided")
    print(f"✓ SUCCESS: p={res.pvalue}")
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {e}")

print()

# Test 2: With .values
print("-" * 60)
print("TEST 2: wilcoxon(Series.values, Series.values)")
print("-" * 60)
try:
    res = wilcoxon(post_v.values, pre_v.values, zero_method="wilcox", alternative="two-sided")
    print(f"✓ SUCCESS: p={res.pvalue}")
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {e}")

print()

# Test 3: Full paired data test (like the real code)
print("=" * 60)
print("TESTING REAL PAIRED DATA")
print("=" * 60)

# Normalize emails
pre_df['email_norm'] = pre_df.get('Email', pre_df.get('email', '')).fillna('').str.lower().str.strip()
post_df['email_norm'] = post_df.get('Email', post_df.get('email', '')).fillna('').str.lower().str.strip()

# Find common questions
pre_question_cols = [c for c in pre_df.columns if c.lower() not in ['email', 'nombre', 'fecha', 'email_norm', 'timestamp'] and not c.startswith('Unnamed')]
post_question_cols = [c for c in post_df.columns if c.lower() not in ['email', 'nombre', 'fecha', 'email_norm', 'timestamp'] and not c.startswith('Unnamed')]

common_questions = sorted(set(pre_question_cols) & set(post_question_cols))
print(f"Common questions found: {len(common_questions)}")
print(f"Sample: {common_questions[:3]}")
print()

# Create paired dataframe
pre_cols = common_questions
post_cols = common_questions
paired = pd.DataFrame()
for q in common_questions:
    paired[f"{q}_pre"] = pre_df[q]
    paired[f"{q}_post"] = post_df[q]

paired_matched = paired.dropna(subset=[c for c in paired.columns if '_pre' in c or '_post' in c])
print(f"Paired rows: {len(paired_matched)}")
print()

# Test global index calculation
pre_cols_matched = [f"{q}_pre" for q in common_questions]
post_cols_matched = [f"{q}_post" for q in common_questions]

person_pre = paired_matched[pre_cols_matched].mean(axis=1, skipna=True)
person_post = paired_matched[post_cols_matched].mean(axis=1, skipna=True)
person_valid = person_pre.notna() & person_post.notna()

print(f"Valid persons: {person_valid.sum()}")
print(f"person_pre (first 3): {person_pre[person_valid].head(3).values}")
print(f"person_post (first 3): {person_post[person_valid].head(3).values}")
print()

person_pre_v = person_pre[person_valid]
person_post_v = person_post[person_valid]

print("-" * 60)
print("TEST 3A: wilcoxon(Series, Series) with FULL PAIRED DATA")
print("-" * 60)
try:
    res = wilcoxon(person_post_v, person_pre_v, zero_method="wilcox", alternative="two-sided")
    print(f"✓ SUCCESS: p={res.pvalue}")
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {e}")

print()

print("-" * 60)
print("TEST 3B: wilcoxon(Series.values, Series.values) with FULL PAIRED DATA")
print("-" * 60)
try:
    res = wilcoxon(person_post_v.values, person_pre_v.values, zero_method="wilcox", alternative="two-sided")
    print(f"✓ SUCCESS: p={res.pvalue}")
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {e}")
