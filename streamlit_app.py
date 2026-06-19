from __future__ import annotations

from pathlib import Path
import re
import unicodedata

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from scipy.stats import wilcoxon
except Exception:
    wilcoxon = None

st.set_page_config(
    page_title="Tablero Satisfaccion Power App",
    page_icon="📊",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
RAW_DIR = BASE_DIR / "data" / "raw"

RANKING_PATH = OUTPUTS_DIR / "ranking_preguntas.csv"
FREQ_PATH = OUTPUTS_DIR / "resumen_metricas.csv"
OPEN_SUMMARY_PATH = OUTPUTS_DIR / "preguntas_abiertas_resumen.csv"
OPEN_TERMS_PATH = OUTPUTS_DIR / "preguntas_abiertas_terminos.csv"
USABILITY_PATH = RAW_DIR / "Usabilidad Power APP.xlsx"
PRETEST_PATH = RAW_DIR / "Experiencia_en_el_uso_de_Power_App_B-Lab.xlsx"
POSTEST_PATH = RAW_DIR / "Experiencia_en_el_uso_de_Power_App_B-Lab - postest.xlsx"
PREPOST_EXPORT_PATH = OUTPUTS_DIR / "comparativo_prepost.csv"

METADATA_COLUMNS = ["Id", "Hora de inicio", "Hora de finalización", "Correo electrónico", "Nombre"]
OPEN_TEXT_COLUMNS = [
    "Si pudieras cambiar solo una cosa para mejorar la Power App, ¿Cuál sería?",
    "En tu día a día, ¿Qué te impediría hacer uso de la PowerApp?",
]

LIKERT_MAP = {
    "totalmente en desacuerdo": 1,
    "en desacuerdo": 2,
    "ni de acuerdo ni en desacuerdo": 3,
    "neutral": 3,
    "de acuerdo": 4,
    "totalmente de acuerdo": 5,
}


def short_text(text: str, max_len: int = 95) -> str:
    value = str(text)
    return value if len(value) <= max_len else f"{value[:max_len - 3]}..."


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text)
    return text


def map_likert(value: object) -> float:
    return LIKERT_MAP.get(normalize_text(value), float("nan"))


def build_question_label_map(ranking_df: pd.DataFrame) -> dict[str, str]:
    """Create stable, unique labels to avoid collisions/truncation mismatches in charts."""
    labels: dict[str, str] = {}
    for i, q in enumerate(ranking_df["pregunta"].tolist(), start=1):
        labels[q] = f"Q{i:02d} - {short_text(q, 78)}"
    return labels


@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_raw_responses() -> pd.DataFrame:
    if PRETEST_PATH.exists():
        return pd.read_excel(PRETEST_PATH)

    excel_files = sorted(RAW_DIR.glob("*.xlsx"))
    if not excel_files:
        return pd.DataFrame()

    # Intenta evitar tomar postest por defecto cuando no hay pretest explicito.
    for path in excel_files:
        if "postest" not in normalize_text(path.name):
            return pd.read_excel(path)
    return pd.read_excel(excel_files[0])


@st.cache_data(show_spinner=False)
def load_prepost_responses() -> tuple[pd.DataFrame, pd.DataFrame]:
    pre_df = pd.read_excel(PRETEST_PATH) if PRETEST_PATH.exists() else pd.DataFrame()
    post_df = pd.read_excel(POSTEST_PATH) if POSTEST_PATH.exists() else pd.DataFrame()
    return pre_df, post_df


def normalize_person_key(value: object) -> str:
    return normalize_text(value)


def detect_common_likert_columns(pre_df: pd.DataFrame, post_df: pd.DataFrame) -> list[str]:
    excluded = set(METADATA_COLUMNS + OPEN_TEXT_COLUMNS)
    return [c for c in pre_df.columns if c in post_df.columns and c not in excluded]


def classify_effect_size_dz(value: float) -> str:
    if pd.isna(value):
        return "NA"
    abs_v = abs(value)
    if abs_v < 0.2:
        return "Muy pequeno"
    if abs_v < 0.5:
        return "Pequeno"
    if abs_v < 0.8:
        return "Mediano"
    return "Grande"


def prepare_prepost_numeric(pre_df: pd.DataFrame, post_df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], int, int]:
    if pre_df.empty or post_df.empty:
        return pd.DataFrame(), [], 0, 0

    common_questions = detect_common_likert_columns(pre_df, post_df)
    if not common_questions:
        return pd.DataFrame(), [], 0, 0

    pre_work = pre_df.copy()
    post_work = post_df.copy()

    if "Correo electrónico" not in pre_work.columns:
        pre_work["Correo electrónico"] = ""
    if "Correo electrónico" not in post_work.columns:
        post_work["Correo electrónico"] = ""
    if "Nombre" not in pre_work.columns:
        pre_work["Nombre"] = ""
    if "Nombre" not in post_work.columns:
        post_work["Nombre"] = ""

    pre_work["person_key"] = pre_work["Correo electrónico"].map(normalize_person_key)
    post_work["person_key"] = post_work["Correo electrónico"].map(normalize_person_key)

    # Fallback a nombre cuando no hay correo.
    pre_name_key = pre_work["Nombre"].map(normalize_person_key)
    post_name_key = post_work["Nombre"].map(normalize_person_key)
    pre_work.loc[pre_work["person_key"] == "", "person_key"] = pre_name_key
    post_work.loc[post_work["person_key"] == "", "person_key"] = post_name_key

    pre_work = pre_work[pre_work["person_key"] != ""].copy()
    post_work = post_work[post_work["person_key"] != ""].copy()

    n_pre_people = int(pre_work["person_key"].nunique())
    n_post_people = int(post_work["person_key"].nunique())

    pre_num = pre_work[["person_key"] + common_questions].copy()
    post_num = post_work[["person_key"] + common_questions].copy()
    for q in common_questions:
        pre_num[q] = pre_num[q].map(map_likert)
        post_num[q] = post_num[q].map(map_likert)

    paired = pre_num.merge(post_num, on="person_key", how="inner", suffixes=("_pre", "_post"))
    return paired, common_questions, n_pre_people, n_post_people


def compute_prepost_change(pre_df: pd.DataFrame, post_df: pd.DataFrame) -> tuple[dict[str, float], pd.DataFrame]:
    paired, questions, n_pre_people, n_post_people = prepare_prepost_numeric(pre_df, post_df)
    base_summary = {
        "n_pre": float(n_pre_people),
        "n_post": float(n_post_people),
        "n_pares": 0.0,
        "n_preguntas": float(len(questions)),
        "indice_pre": float("nan"),
        "indice_post": float("nan"),
        "delta_global": float("nan"),
        "pct_personas_mejoran": float("nan"),
    }

    if paired.empty or not questions:
        return base_summary, pd.DataFrame()

    pre_cols = [f"{q}_pre" for q in questions]
    post_cols = [f"{q}_post" for q in questions]

    person_pre = paired[pre_cols].mean(axis=1, skipna=True)
    person_post = paired[post_cols].mean(axis=1, skipna=True)
    person_valid = person_pre.notna() & person_post.notna()

    rows: list[dict[str, float | str]] = []
    for q in questions:
        pre_q = paired[f"{q}_pre"]
        post_q = paired[f"{q}_post"]
        valid = pre_q.notna() & post_q.notna()
        if valid.sum() == 0:
            continue

        pre_v = pre_q[valid]
        post_v = post_q[valid]
        delta_v = post_v - pre_v
        dz = float("nan")
        if len(delta_v) >= 2 and float(delta_v.std(ddof=1)) > 0:
            dz = float(delta_v.mean() / delta_v.std(ddof=1))

        p_wilcoxon = float("nan")
        if wilcoxon is not None and len(delta_v) >= 5 and float(delta_v.abs().sum()) > 0:
            try:
                p_wilcoxon = float(wilcoxon(post_v, pre_v, zero_method="wilcox", alternative="two-sided").pvalue)
            except Exception:
                p_wilcoxon = float("nan")

        rows.append(
            {
                "pregunta": q,
                "n_pares": float(valid.sum()),
                "promedio_pre": float(pre_v.mean()),
                "promedio_post": float(post_v.mean()),
                "delta_promedio": float(delta_v.mean()),
                "pct_mejora": float((delta_v > 0).mean() * 100),
                "pct_sin_cambio": float((delta_v == 0).mean() * 100),
                "pct_empeora": float((delta_v < 0).mean() * 100),
                "p_wilcoxon": p_wilcoxon,
                "effect_size_dz": dz,
                "effect_size_mag": classify_effect_size_dz(dz),
            }
        )

    change_df = pd.DataFrame(rows).sort_values("delta_promedio", ascending=False)

    summary = base_summary.copy()
    summary["n_pares"] = float(paired.shape[0])
    summary["indice_pre"] = float(person_pre[person_valid].mean()) if person_valid.any() else float("nan")
    summary["indice_post"] = float(person_post[person_valid].mean()) if person_valid.any() else float("nan")
    if pd.notna(summary["indice_pre"]) and pd.notna(summary["indice_post"]):
        summary["delta_global"] = float(summary["indice_post"] - summary["indice_pre"])
    summary["pct_personas_mejoran"] = (
        float((person_post[person_valid] > person_pre[person_valid]).mean() * 100)
        if person_valid.any()
        else float("nan")
    )

    if not change_df.empty:
        summary["n_significativas_005"] = float((change_df["p_wilcoxon"] < 0.05).sum())
    else:
        summary["n_significativas_005"] = 0.0

    return summary, change_df


def export_prepost_change(summary: dict[str, float], change_df: pd.DataFrame) -> Path:
    export_df = change_df.copy()
    export_df.insert(0, "indice_global_pre", summary.get("indice_pre", float("nan")))
    export_df.insert(1, "indice_global_post", summary.get("indice_post", float("nan")))
    export_df.insert(2, "delta_global", summary.get("delta_global", float("nan")))
    export_df.insert(3, "n_pares_global", summary.get("n_pares", float("nan")))
    export_df.insert(4, "n_pre", summary.get("n_pre", float("nan")))
    export_df.insert(5, "n_post", summary.get("n_post", float("nan")))
    export_df.insert(6, "pct_personas_mejoran", summary.get("pct_personas_mejoran", float("nan")))
    PREPOST_EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    export_df.to_csv(PREPOST_EXPORT_PATH, index=False, encoding="utf-8-sig")
    return PREPOST_EXPORT_PATH


def render_prepost_change_analysis(pre_df: pd.DataFrame, post_df: pd.DataFrame) -> None:
    with st.expander("Comparativo de cambio: pretest vs postest", expanded=True):
        if pre_df.empty or post_df.empty:
            st.info(
                "No se encontro pretest o postest en data/raw para comparar. "
                "Se esperan ambos archivos: 'Experiencia_en_el_uso_de_Power_App_B-Lab.xlsx' y "
                "'Experiencia_en_el_uso_de_Power_App_B-Lab - postest.xlsx'."
            )
            return

        summary, change_df = compute_prepost_change(pre_df, post_df)
        if change_df.empty:
            st.warning(
                "No se pudo construir la comparacion pre/post. Verifica que ambos archivos tengan "
                "las mismas preguntas Likert y una clave comun (correo o nombre)."
            )
            return

        alpha = st.select_slider(
            "Umbral de significancia (p)",
            options=[0.1, 0.05, 0.01],
            value=0.05,
            key="prepost_alpha",
        )

        if "p_wilcoxon" in change_df.columns:
            change_df["significativa"] = np.where(change_df["p_wilcoxon"] < alpha, "Si", "No")
        else:
            change_df["significativa"] = "NA"

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Personas pretest", int(summary["n_pre"]))
        c2.metric("Personas postest", int(summary["n_post"]))
        c3.metric("Pares emparejados", int(summary["n_pares"]))
        c4.metric("Indice pre -> post", f"{summary['indice_pre']:.2f} -> {summary['indice_post']:.2f}")
        c5.metric("Delta global", f"{summary['delta_global']:+.2f}")

        if wilcoxon is None:
            st.caption("Prueba Wilcoxon no disponible en el entorno. Instala scipy para habilitar significancia estadistica.")
        else:
            n_sig = int((change_df["p_wilcoxon"] < alpha).sum())
            st.caption(f"Preguntas con cambio significativo (p < {alpha}): {n_sig} de {change_df.shape[0]}")

        st.caption(
            f"Preguntas comparables: {int(summary['n_preguntas'])} | "
            f"% personas que mejoran su promedio individual: {summary['pct_personas_mejoran']:.1f}%"
        )

        export_path = export_prepost_change(summary, change_df)
        st.caption(f"CSV actualizado automaticamente en: {export_path}")

        display_df = change_df.copy()
        display_df = display_df.sort_values("delta_promedio", ascending=False)
        display_df["pregunta_label"] = [f"Q{i:02d} - {short_text(q, 84)}" for i, q in enumerate(display_df["pregunta"], start=1)]

        fig_delta = px.bar(
            display_df.iloc[::-1],
            x="delta_promedio",
            y="pregunta_label",
            orientation="h",
            color="delta_promedio",
            color_continuous_scale="RdYlGn",
            title="Cambio promedio por pregunta (post - pre)",
            hover_data={
                "pregunta": True,
                "n_pares": True,
                "promedio_pre": ":.2f",
                "promedio_post": ":.2f",
                "pct_mejora": ":.1f",
                "pct_empeora": ":.1f",
                "p_wilcoxon": ".4f",
                "effect_size_dz": ".2f",
                "effect_size_mag": True,
                "significativa": True,
                "pregunta_label": False,
            },
        )
        fig_delta.add_vline(x=0, line_dash="dash", line_color="#333333")
        fig_delta.update_layout(xaxis_title="Delta en escala 1-5", yaxis_title="Pregunta")
        st.plotly_chart(fig_delta, use_container_width=True)

        st.dataframe(
            display_df[
                [
                    "pregunta",
                    "n_pares",
                    "promedio_pre",
                    "promedio_post",
                    "delta_promedio",
                    "pct_mejora",
                    "pct_sin_cambio",
                    "pct_empeora",
                    "p_wilcoxon",
                    "effect_size_dz",
                    "effect_size_mag",
                    "significativa",
                ]
            ],
            use_container_width=True,
            height=360,
        )

        st.download_button(
            "Descargar comparativo pre/post (CSV)",
            data=change_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="comparativo_prepost.csv",
            mime="text/csv",
        )



def render_intervention_significance_guide(pre_df: pd.DataFrame, post_df: pd.DataFrame) -> None:
    st.subheader("Como interpretar si la intervencion fue significativa")
    if pre_df.empty or post_df.empty:
        st.info("No hay pretest y postest suficientes para emitir un dictamen.")
        return

    summary, change_df = compute_prepost_change(pre_df, post_df)
    paired_df, questions, _, _ = prepare_prepost_numeric(pre_df, post_df)
    if change_df.empty or paired_df.empty:
        st.warning("No fue posible calcular comparativo pre/post para emitir conclusion.")
        return

    pre_cols = [f"{q}_pre" for q in questions]
    post_cols = [f"{q}_post" for q in questions]
    person_pre = paired_df[pre_cols].mean(axis=1, skipna=True)
    person_post = paired_df[post_cols].mean(axis=1, skipna=True)
    person_valid = person_pre.notna() & person_post.notna()

    if int(person_valid.sum()) < 3:
        st.warning("No hay suficientes pares comparables para calcular significancia del indice global.")
        return

    person_pre_v = person_pre[person_valid]
    person_post_v = person_post[person_valid]
    delta_global = float(person_post_v.mean() - person_pre_v.mean())
    n_pares = int(person_valid.sum())
    n_preguntas = int(len(questions))

    p_global = float("nan")
    if wilcoxon is not None and float((person_post_v - person_pre_v).abs().sum()) > 0:
        try:
            p_global = float(
                wilcoxon(person_post_v, person_pre_v, zero_method="wilcox", alternative="two-sided").pvalue
            )
        except Exception:
            p_global = float("nan")

    # Criterio pedido: basado en el indice global pre/post de las preguntas Likert comparables.
    if pd.notna(p_global):
        es_significativa = (p_global < 0.05) and (delta_global > 0)
    else:
        # Fallback si no hay prueba disponible en entorno: direccion y magnitud minima.
        es_significativa = delta_global >= 0.3

    if es_significativa:
        st.success("Conclusion: la intervencion fue significativa.")
    else:
        st.warning("Conclusion: la intervencion no alcanza significancia con el criterio del indice global pre/post.")

    st.markdown(
        f"""
        **Por que:**
        - Preguntas Likert usadas en el indice global: **{n_preguntas}**.
        - Pares comparables individuales usados: **{n_pares}**.
        - Indice global pre: **{person_pre_v.mean():.2f}**.
        - Indice global post: **{person_post_v.mean():.2f}**.
        - Delta del indice global (post - pre): **{delta_global:+.2f}**.
        - p-valor Wilcoxon del indice global pareado: **{p_global:.4f}**.

        **Criterio usado (solo indice global de las preguntas que van):**
        - Se concluye significativa cuando el indice global mejora (delta > 0)
          y esa mejora es estadisticamente significativa (p < 0.05).
        """
    )

    if n_preguntas != 11:
        st.info(
            f"Nota: en este corte se comparan {n_preguntas} preguntas Likert. "
            "Si esperabas 11 exactas, revisa que ambos archivos tengan las mismas columnas de preguntas."
        )


def validate_files() -> list[Path]:
    needed = [RANKING_PATH, FREQ_PATH, OPEN_SUMMARY_PATH, OPEN_TERMS_PATH]
    return [p for p in needed if not p.exists()]


def render_missing_files(missing_files: list[Path]) -> None:
    st.error("No se encontraron todos los archivos de salida del notebook.")
    st.write("Ejecuta la celda de pipeline en el notebook para regenerar:")
    for p in missing_files:
        st.write(f"- {p}")


def build_open_responses_df(raw_df: pd.DataFrame, question_col: str) -> pd.DataFrame:
    """Build a clean table of open responses for one question."""
    if question_col not in raw_df.columns:
        return pd.DataFrame(columns=["Nombre", "respuesta"])

    work = raw_df.copy()
    if "Nombre" not in work.columns:
        work["Nombre"] = "Sin nombre"

    out = work[["Nombre", question_col]].rename(columns={question_col: "respuesta"})
    out["Nombre"] = out["Nombre"].astype(str).str.strip()
    out["respuesta"] = out["respuesta"].astype(str).str.strip()

    # Evita tratar NaN como texto literal
    out = out[(out["respuesta"] != "") & (out["respuesta"].str.lower() != "nan")]
    return out.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_usability_logs() -> pd.DataFrame:
    if not USABILITY_PATH.exists():
        return pd.DataFrame()

    xls = pd.ExcelFile(USABILITY_PATH)
    target_sheet = "query (5)" if "query (5)" in xls.sheet_names else xls.sheet_names[0]
    return pd.read_excel(USABILITY_PATH, sheet_name=target_sheet)


def _compress_consecutive(values: list[str]) -> list[str]:
    compressed: list[str] = []
    for v in values:
        if not compressed or compressed[-1] != v:
            compressed.append(v)
    return compressed


def prepare_usability_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = ["Usuario", "Creado por", "Creado", "Seccion", "Accion"]
    if df.empty or any(col not in df.columns for col in required):
        return pd.DataFrame(), pd.DataFrame()

    work = df.copy()
    work["Usuario"] = work["Usuario"].astype(str).str.strip().str.lower()
    work["Creado por"] = work["Creado por"].astype(str).str.strip()
    work["Seccion"] = work["Seccion"].astype(str).str.strip()
    work["Accion"] = work["Accion"].astype(str).str.strip()
    work["Creado_dt"] = pd.to_datetime(work["Creado"], errors="coerce")

    work = work[(work["Usuario"] != "") & (work["Creado por"] != "") & work["Creado_dt"].notna()].copy()
    if work.empty:
        return pd.DataFrame(), pd.DataFrame()

    work["user_key"] = work["Usuario"] + " | " + work["Creado por"]
    work = work.sort_values(["user_key", "Creado_dt"]).reset_index(drop=True)

    # Definimos sesion cuando hay un salto mayor a 45 minutos para el mismo usuario.
    gap_minutes = work.groupby("user_key")["Creado_dt"].diff().dt.total_seconds().div(60)
    work["new_session"] = gap_minutes.isna() | (gap_minutes > 45)
    work["session_number"] = work.groupby("user_key")["new_session"].cumsum().astype(int)
    work["session_key"] = work["user_key"] + "#S" + work["session_number"].astype(str)

    sessions = (
        work.groupby(["session_key", "user_key"], as_index=False)
        .agg(
            inicio=("Creado_dt", "min"),
            fin=("Creado_dt", "max"),
            eventos=("Accion", "count"),
            secciones_unicas=("Seccion", "nunique"),
        )
        .sort_values("inicio")
    )
    sessions["duracion_min"] = (sessions["fin"] - sessions["inicio"]).dt.total_seconds().div(60).clip(lower=0)
    sessions["usuario_correo"] = sessions["user_key"].str.split(" \| ").str[0]
    sessions["usuario_nombre"] = sessions["user_key"].str.split(" \| ").str[1]

    return work, sessions


def build_section_abandonment(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame()

    started = events[events["Accion"].str.lower() == "ingreso a sección"].copy()
    completed = events[events["Accion"].str.lower() == "sección completada"].copy()
    if started.empty:
        return pd.DataFrame()

    started_pairs = started[["Seccion", "user_key"]].drop_duplicates()
    completed_pairs = completed[["Seccion", "user_key"]].drop_duplicates()
    merged = started_pairs.merge(
        completed_pairs.assign(completo=1),
        on=["Seccion", "user_key"],
        how="left",
    )
    merged["completo"] = merged["completo"].fillna(0).astype(int)

    out = (
        merged.groupby("Seccion", as_index=False)
        .agg(
            usuarios_inician=("user_key", "nunique"),
            usuarios_completan=("completo", "sum"),
        )
        .sort_values("usuarios_inician", ascending=False)
    )
    out["usuarios_abandonan"] = (out["usuarios_inician"] - out["usuarios_completan"]).clip(lower=0)
    out["tasa_abandono_pct"] = (out["usuarios_abandonan"] / out["usuarios_inician"] * 100).round(1)
    out["tasa_completitud_pct"] = (out["usuarios_completan"] / out["usuarios_inician"] * 100).round(1)
    return out


def build_section_id(section_name: object) -> str:
    normalized = normalize_text(section_name)
    slug = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    if not slug:
        return "SEC_UNKNOWN"
    return f"SEC_{slug.upper()}"


def build_section_abandonment_by_id(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame()

    work = events.copy()
    work["section_id"] = work["Seccion"].apply(build_section_id)

    started = work[work["Accion"].str.lower() == "ingreso a sección"].copy()
    completed = work[work["Accion"].str.lower() == "sección completada"].copy()
    if started.empty:
        return pd.DataFrame()

    started_pairs = started[["section_id", "user_key"]].drop_duplicates()
    completed_pairs = completed[["section_id", "user_key"]].drop_duplicates()
    merged = started_pairs.merge(
        completed_pairs.assign(completo=1),
        on=["section_id", "user_key"],
        how="left",
    )
    merged["completo"] = merged["completo"].fillna(0).astype(int)

    out = (
        merged.groupby("section_id", as_index=False)
        .agg(
            usuarios_inician=("user_key", "nunique"),
            usuarios_completan=("completo", "sum"),
        )
        .sort_values("usuarios_inician", ascending=False)
    )
    out["usuarios_abandonan"] = (out["usuarios_inician"] - out["usuarios_completan"]).clip(lower=0)
    out["tasa_abandono_pct"] = (out["usuarios_abandonan"] / out["usuarios_inician"] * 100).round(1)
    out["tasa_completitud_pct"] = (out["usuarios_completan"] / out["usuarios_inician"] * 100).round(1)

    section_variants = (
        work.groupby(["section_id", "Seccion"], as_index=False)
        .size()
        .rename(columns={"size": "frecuencia"})
        .sort_values(["section_id", "frecuencia"], ascending=[True, False])
    )
    primary_name = section_variants.drop_duplicates("section_id")["section_id"].to_frame()
    primary_name = primary_name.merge(
        section_variants.drop_duplicates("section_id")[["section_id", "Seccion"]],
        on="section_id",
        how="left",
    )
    n_variants = work.groupby("section_id", as_index=False).agg(variantes_texto=("Seccion", "nunique"))

    out = out.merge(primary_name.rename(columns={"Seccion": "seccion_representativa"}), on="section_id", how="left")
    out = out.merge(n_variants, on="section_id", how="left")
    return out


def build_top_paths(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame()

    ingress = events[events["Accion"].str.lower() == "ingreso a sección"].copy()
    if ingress.empty:
        return pd.DataFrame()

    ingress = ingress.sort_values(["session_key", "Creado_dt"])
    path_df = ingress.groupby("session_key", as_index=False).agg(
        user_key=("user_key", "first"),
        secciones=("Seccion", list),
    )
    path_df["secciones"] = path_df["secciones"].apply(_compress_consecutive)
    path_df["camino"] = path_df["secciones"].apply(lambda x: "  ->  ".join(x))
    path_df["n_pasos"] = path_df["secciones"].apply(len)
    path_df = path_df[path_df["n_pasos"] > 0]

    return (
        path_df.groupby("camino", as_index=False)
        .agg(
            sesiones=("session_key", "count"),
            usuarios_unicos=("user_key", "nunique"),
            pasos_promedio=("n_pasos", "mean"),
        )
        .sort_values(["sesiones", "usuarios_unicos"], ascending=False)
    )


def render_app_usage_analysis(usability_events_df: pd.DataFrame, sessions_df: pd.DataFrame) -> None:
    st.subheader("Analitica de uso de la app")
    if usability_events_df.empty or sessions_df.empty:
        st.info("No se encontro informacion util en 'Usabilidad Power APP.xlsx' para construir esta seccion.")
        return

    c_u1, c_u2, c_u3, c_u4 = st.columns(4)
    c_u1.metric("Usuarios unicos", int(sessions_df["user_key"].nunique()))
    c_u2.metric("Sesiones", int(sessions_df.shape[0]))
    c_u3.metric("Duracion media sesion", f"{sessions_df['duracion_min'].mean():.1f} min")
    c_u4.metric("Eventos registrados", int(usability_events_df.shape[0]))

    sessions_week = sessions_df.copy()
    sessions_week = sessions_df.copy()
    sessions_week["dia_semana_idx"] = sessions_week["inicio"].dt.weekday
    dia_map = {
        0: "Lunes",
        1: "Martes",
        2: "Miercoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sabado",
        6: "Domingo",
    }
    sessions_week["dia_semana"] = sessions_week["dia_semana_idx"].map(dia_map)

    by_day = (
        sessions_week.groupby(["dia_semana_idx", "dia_semana"], as_index=False)
        .agg(inicios=("session_key", "count"), usuarios_unicos=("user_key", "nunique"))
        .sort_values("dia_semana_idx")
    )

    with st.expander("1) Distribucion de tiempos de ingreso", expanded=True):
        fig_duracion = px.histogram(
            sessions_df,
            x="duracion_min",
            nbins=25,
            title="Distribucion de duracion de sesiones (minutos)",
            labels={"duracion_min": "Duracion (minutos)"},
            color_discrete_sequence=["#1f77b4"],
        )
        st.plotly_chart(fig_duracion, use_container_width=True)

    with st.expander("2) Tendencia historica de inicios", expanded=True):
        by_date = (
            sessions_df.assign(fecha=sessions_df["inicio"].dt.floor("D"))
            .groupby("fecha", as_index=False)
            .agg(inicios=("session_key", "count"))
            .sort_values("fecha")
        )
        if by_date.empty:
            st.info("No hay fechas disponibles para construir la tendencia.")
        else:
            idx = np.arange(len(by_date))
            if len(by_date) >= 2:
                coef = np.polyfit(idx, by_date["inicios"].to_numpy(dtype=float), 1)
                by_date["tendencia"] = coef[0] * idx + coef[1]
            else:
                by_date["tendencia"] = by_date["inicios"]

            trend_long = by_date.melt(
                id_vars="fecha",
                value_vars=["inicios", "tendencia"],
                var_name="serie",
                value_name="valor",
            )
            fig_trend = px.line(
                trend_long,
                x="fecha",
                y="valor",
                color="serie",
                title="Inicios diarios con linea de tendencia",
                labels={"fecha": "Fecha", "valor": "Numero de inicios", "serie": "Serie"},
                color_discrete_map={"inicios": "#1f77b4", "tendencia": "#e4572e"},
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            st.dataframe(by_date, use_container_width=True, height=220)

    with st.expander("3) Tasa de abandono y completitud por seccion", expanded=True):
        abandonment_df = build_section_abandonment(usability_events_df)
        abandonment_by_id_df = build_section_abandonment_by_id(usability_events_df)

        if abandonment_df.empty and abandonment_by_id_df.empty:
            st.info("No hay suficientes eventos de ingreso/completitud para calcular abandono.")
        else:
            tab_texto, tab_id = st.tabs(["Por texto de seccion", "Por section_id estable"])

            with tab_texto:
                if abandonment_df.empty:
                    st.info("No hay datos para la vista por texto.")
                else:
                    fig_abandono = px.bar(
                        abandonment_df.sort_values("tasa_abandono_pct", ascending=False).head(15),
                        x="tasa_abandono_pct",
                        y="Seccion",
                        orientation="h",
                        title="Top secciones con mayor abandono (%)",
                        labels={"tasa_abandono_pct": "Abandono %"},
                        color="tasa_abandono_pct",
                        color_continuous_scale="Reds",
                    )
                    fig_abandono.update_layout(yaxis={"categoryorder": "total ascending"})
                    st.plotly_chart(fig_abandono, use_container_width=True)
                    st.dataframe(abandonment_df, use_container_width=True, height=320)

            with tab_id:
                if abandonment_by_id_df.empty:
                    st.info("No hay datos para la vista por section_id.")
                else:
                    fig_abandono_id = px.bar(
                        abandonment_by_id_df.sort_values("tasa_abandono_pct", ascending=False).head(15),
                        x="tasa_abandono_pct",
                        y="section_id",
                        orientation="h",
                        title="Top section_id con mayor abandono (%)",
                        labels={"tasa_abandono_pct": "Abandono %", "section_id": "Section ID"},
                        color="tasa_abandono_pct",
                        color_continuous_scale="Oranges",
                        hover_data={"seccion_representativa": True, "variantes_texto": True},
                    )
                    fig_abandono_id.update_layout(yaxis={"categoryorder": "total ascending"})
                    st.plotly_chart(fig_abandono_id, use_container_width=True)
                    st.dataframe(
                        abandonment_by_id_df[
                            [
                                "section_id",
                                "seccion_representativa",
                                "variantes_texto",
                                "usuarios_inician",
                                "usuarios_completan",
                                "usuarios_abandonan",
                                "tasa_abandono_pct",
                                "tasa_completitud_pct",
                            ]
                        ],
                        use_container_width=True,
                        height=320,
                    )

    with st.expander("4) Frecuencia de uso durante la semana", expanded=True):
        fig_week = px.bar(
            by_day,
            x="dia_semana",
            y="inicios",
            title="Inicios por dia de la semana",
            labels={"inicios": "Numero de inicios"},
            color="usuarios_unicos",
            color_continuous_scale="Teal",
        )
        st.plotly_chart(fig_week, use_container_width=True)

    with st.expander("5) Top de combinaciones de caminos", expanded=True):
        top_paths_df = build_top_paths(usability_events_df)
        if top_paths_df.empty:
            st.info("No se pudieron construir caminos con los eventos disponibles.")
        else:
            fig_paths = px.bar(
                top_paths_df.head(10).iloc[::-1],
                x="sesiones",
                y="camino",
                orientation="h",
                title="Top 10 caminos mas recorridos",
                labels={"sesiones": "Sesiones"},
                color="usuarios_unicos",
                color_continuous_scale="Blues",
            )
            st.plotly_chart(fig_paths, use_container_width=True)
            st.dataframe(top_paths_df.head(20), use_container_width=True, height=320)

    with st.expander("6) Franjas horarias con mas inicios", expanded=True):
        franja_labels = [
            "00:00-06:00",
            "06:00-09:00",
            "09:00-12:00",
            "12:00-15:00",
            "15:00-18:00",
            "18:00-21:00",
            "21:00-24:00",
        ]
        sessions_week["franja_horaria"] = pd.cut(
            sessions_week["inicio"].dt.hour,
            bins=[0, 6, 9, 12, 15, 18, 21, 24],
            labels=franja_labels,
            include_lowest=True,
            right=False,
        )
        by_franja = (
            sessions_week.groupby("franja_horaria", observed=False)
            .agg(inicios=("session_key", "count"))
            .reset_index()
        )
        by_franja["franja_horaria"] = by_franja["franja_horaria"].astype(str)

        fig_franja = px.bar(
            by_franja,
            x="franja_horaria",
            y="inicios",
            title="Inicios por franja horaria",
            labels={"franja_horaria": "Franja", "inicios": "Numero de inicios"},
            color="inicios",
            color_continuous_scale="Sunset",
            category_orders={"franja_horaria": franja_labels},
        )
        fig_franja.update_xaxes(type="category", categoryorder="array", categoryarray=franja_labels)
        st.plotly_chart(fig_franja, use_container_width=True)


def main() -> None:
    st.title("Tablero de Analisis - Encuesta Likert Power App")
    st.caption("Visualizacion consolidada de satisfaccion y preguntas abiertas")

    missing_files = validate_files()
    if missing_files:
        render_missing_files(missing_files)
        st.stop()

    ranking_df = load_csv(RANKING_PATH)
    freq_df = load_csv(FREQ_PATH)
    open_summary_df = load_csv(OPEN_SUMMARY_PATH)
    open_terms_df = load_csv(OPEN_TERMS_PATH)
    raw_df = load_raw_responses()
    pretest_df, postest_df = load_prepost_responses()
    usability_raw_df = load_usability_logs()
    usability_events_df, sessions_df = prepare_usability_data(usability_raw_df)

    render_intervention_significance_guide(pretest_df, postest_df)
    st.divider()

    if ranking_df.empty:
        st.warning("El archivo de ranking esta vacio.")
        st.stop()

    worst_row = ranking_df.iloc[0]
    best_row = ranking_df.iloc[-1]

    # Usar el total de filas del Excel crudo como número real de respondentes.
    # max(n_validas) subestima cuando alguien dejó alguna pregunta sin responder.
    if not raw_df.empty:
        n_respuestas = int(raw_df.dropna(how="all").shape[0])
    else:
        n_respuestas = int(ranking_df["n_validas"].max())
    n_preguntas = int(ranking_df.shape[0])
    indice_global = float(ranking_df["promedio"].mean())
    favorabilidad_global = float(ranking_df["favorabilidad_pct"].mean())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Indice global (1-5)", f"{indice_global:.2f}")
    c2.metric("Favorabilidad global", f"{favorabilidad_global:.1f}%")
    c3.metric("Respuestas", n_respuestas)
    c4.metric("Preguntas Likert", n_preguntas)

    st.divider()

    render_prepost_change_analysis(pretest_df, postest_df)

    with st.expander("Mejor y peor pregunta", expanded=True):
        col_a, col_b = st.columns(2)
        col_a.subheader("Peor calificada")
        col_a.write(short_text(worst_row["pregunta"], 140))
        col_a.write(
            f"Promedio: {worst_row['promedio']:.2f} | Top-box: {worst_row['top_box_pct']:.1f}% | Neto: {worst_row['neto_favorabilidad_pct']:.1f}%"
        )

        col_b.subheader("Mejor calificada")
        col_b.write(short_text(best_row["pregunta"], 140))
        col_b.write(
            f"Promedio: {best_row['promedio']:.2f} | Top-box: {best_row['top_box_pct']:.1f}% | Neto: {best_row['neto_favorabilidad_pct']:.1f}%"
        )

    chart_df = ranking_df.copy()
    question_label_map = build_question_label_map(chart_df)
    chart_df["pregunta_label"] = chart_df["pregunta"].map(question_label_map)

    with st.expander("Seccion Encuesta: Ranking de preguntas (peor a mejor)", expanded=True):
        metric_choice = st.radio(
            "Metrica para visualizar",
            ["promedio", "favorabilidad_pct", "top_box_pct", "desfavorabilidad_pct", "neto_favorabilidad_pct"],
            horizontal=True,
        )

        fig_rank = px.bar(
            chart_df,
            x=metric_choice,
            y="pregunta_label",
            orientation="h",
            color=metric_choice,
            color_continuous_scale="RdYlGn",
            title=f"Ranking por {metric_choice}",
            hover_data={"pregunta": True, "pregunta_label": False},
        )
        fig_rank.update_layout(height=max(520, n_preguntas * 45), yaxis_title="Pregunta", xaxis_title=metric_choice)
        st.plotly_chart(fig_rank, use_container_width=True)

    with st.expander("Seccion Encuesta: Distribucion Likert por pregunta", expanded=True):
        likert_cols = [
            "1_totalmente_en_desacuerdo",
            "2_en_desacuerdo",
            "3_neutral",
            "4_de_acuerdo",
            "5_totalmente_de_acuerdo",
        ]

        freq_long = freq_df.copy()
        freq_long["pregunta_label"] = freq_long["pregunta"].map(question_label_map)
        freq_long = freq_long.dropna(subset=["pregunta_label"])
        freq_long = freq_long.melt(
            id_vars=["pregunta", "pregunta_label"],
            value_vars=likert_cols,
            var_name="categoria",
            value_name="conteo",
        )

        totals = freq_long.groupby("pregunta")["conteo"].transform("sum").replace(0, 1)
        freq_long["porcentaje"] = (freq_long["conteo"] / totals) * 100

        category_order = {
            "categoria": likert_cols,
            "pregunta_label": chart_df["pregunta_label"].tolist(),
        }

        fig_likert = px.bar(
            freq_long,
            x="porcentaje",
            y="pregunta_label",
            color="categoria",
            orientation="h",
            category_orders=category_order,
            title="Barras apiladas Likert (%)",
            color_discrete_map={
                "1_totalmente_en_desacuerdo": "#8b0000",
                "2_en_desacuerdo": "#d7301f",
                "3_neutral": "#f0f0f0",
                "4_de_acuerdo": "#74a9cf",
                "5_totalmente_de_acuerdo": "#0570b0",
            },
        )
        fig_likert.update_layout(height=max(520, n_preguntas * 45), xaxis_title="Porcentaje", yaxis_title="Pregunta")
        st.plotly_chart(fig_likert, use_container_width=True)

    with st.expander("Seccion Encuesta: Analisis de preguntas abiertas", expanded=True):
        open_questions = open_terms_df["pregunta_abierta"].dropna().unique().tolist()
        if not open_questions:
            st.info("No hay informacion de preguntas abiertas para mostrar.")
        else:
            selected_open = st.selectbox(
                "Pregunta abierta",
                options=open_questions,
                key="open_question_selector",
            )

            tab1, tab2, tab3 = st.tabs(["Resumen", "Terminos", "Respuestas completas"])

            with tab1:
                st.markdown("Resumen por pregunta abierta")
                summary_view = open_summary_df[open_summary_df["pregunta_abierta"] == selected_open]
                if summary_view.empty:
                    st.dataframe(open_summary_df, use_container_width=True)
                else:
                    st.dataframe(summary_view, use_container_width=True)

                responses_df = build_open_responses_df(raw_df, selected_open)
                c1, c2, c3 = st.columns(3)
                c1.metric("Respuestas no vacias", int(responses_df.shape[0]))
                avg_len = float(responses_df["respuesta"].str.len().mean()) if not responses_df.empty else 0.0
                c2.metric("Longitud promedio", f"{avg_len:.1f} chars")
                c3.metric("Personas unicas", int(responses_df["Nombre"].nunique()) if not responses_df.empty else 0)

            with tab2:
                terms_view = (
                    open_terms_df[open_terms_df["pregunta_abierta"] == selected_open]
                    .sort_values("frecuencia", ascending=False)
                    .head(15)
                )
                fig_terms = px.bar(
                    terms_view,
                    x="frecuencia",
                    y="termino",
                    orientation="h",
                    title="Top terminos",
                    color="frecuencia",
                    color_continuous_scale="Blues",
                )
                fig_terms.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig_terms, use_container_width=True)

            with tab3:
                responses_df = build_open_responses_df(raw_df, selected_open)
                if responses_df.empty:
                    st.info("No hay respuestas textuales para esta pregunta en el archivo crudo.")
                else:
                    search_text = st.text_input("Buscar palabra/frase en respuestas", value="", key="open_search")
                    selected_people = st.multiselect(
                        "Filtrar por nombre",
                        options=sorted(responses_df["Nombre"].unique().tolist()),
                        default=[],
                        key="open_people_filter",
                    )

                    filtered = responses_df.copy()
                    if search_text.strip():
                        filtered = filtered[
                            filtered["respuesta"].str.contains(search_text.strip(), case=False, na=False)
                        ]
                    if selected_people:
                        filtered = filtered[filtered["Nombre"].isin(selected_people)]

                    st.caption(f"Mostrando {filtered.shape[0]} de {responses_df.shape[0]} respuestas")
                    st.dataframe(filtered, use_container_width=True, height=340)

                    st.download_button(
                        "Descargar respuestas filtradas (CSV)",
                        data=filtered.to_csv(index=False).encode("utf-8-sig"),
                        file_name="respuestas_abiertas_filtradas.csv",
                        mime="text/csv",
                    )

    with st.expander("Seccion Encuesta: Detalle tabular", expanded=False):
        st.dataframe(
            ranking_df.sort_values("promedio", ascending=True),
            use_container_width=True,
            height=420,
        )

    with st.expander("Seccion Encuesta: Resultados por nombre", expanded=False):
        if raw_df.empty:
            st.info("No se encontro archivo .xlsx en data/raw para mostrar detalle por persona.")
            return

        if "Nombre" not in raw_df.columns:
            st.warning("El archivo crudo no tiene columna 'Nombre'.")
            return

        available_questions = [q for q in ranking_df["pregunta"].tolist() if q in raw_df.columns]
        if not available_questions:
            st.warning("No fue posible cruzar columnas Likert entre outputs y archivo crudo.")
            return

        people_df = raw_df.copy()
        people_df["Nombre"] = people_df["Nombre"].astype(str).str.strip()
        people_df = people_df[people_df["Nombre"] != ""]

        selected_name = st.selectbox(
            "Selecciona una persona",
            options=sorted(people_df["Nombre"].dropna().unique().tolist()),
        )

        person_row = people_df[people_df["Nombre"] == selected_name].head(1)
        if person_row.empty:
            st.info("No se encontraron respuestas para el nombre seleccionado.")
            return

        # Convierte las respuestas de esa persona y calcula comparativo
        person_scores = person_row[available_questions].T.reset_index()
        person_scores.columns = ["pregunta", "respuesta_texto"]
        person_scores["puntaje_persona"] = person_scores["respuesta_texto"].map(map_likert)

        compare_df = person_scores.merge(
            ranking_df[["pregunta", "promedio"]],
            on="pregunta",
            how="left",
        )
        compare_df = compare_df.rename(columns={"promedio": "promedio_global"})
        compare_df["brecha_vs_global"] = compare_df["puntaje_persona"] - compare_df["promedio_global"]
        compare_df["pregunta_label"] = compare_df["pregunta"].map(question_label_map)

        cpa, cpb, cpc = st.columns(3)
        person_avg = float(compare_df["puntaje_persona"].mean(skipna=True))
        global_avg = float(compare_df["promedio_global"].mean(skipna=True))
        cpa.metric("Promedio persona", f"{person_avg:.2f}")
        cpb.metric("Promedio global", f"{global_avg:.2f}")
        cpc.metric("Brecha persona-global", f"{person_avg - global_avg:+.2f}")

        fig_person = px.bar(
            compare_df.sort_values("puntaje_persona", ascending=True),
            x="puntaje_persona",
            y="pregunta_label",
            orientation="h",
            title=f"Puntaje por pregunta - {selected_name}",
            color="brecha_vs_global",
            color_continuous_scale="RdYlGn",
            hover_data={
                "pregunta": True,
                "respuesta_texto": True,
                "promedio_global": ":.2f",
                "brecha_vs_global": ":+.2f",
                "pregunta_label": False,
            },
        )
        fig_person.update_layout(height=max(520, len(compare_df) * 45), xaxis_title="Puntaje (1-5)", yaxis_title="Pregunta")
        st.plotly_chart(fig_person, use_container_width=True)

        st.dataframe(
            compare_df[["pregunta", "respuesta_texto", "puntaje_persona", "promedio_global", "brecha_vs_global"]]
            .sort_values("puntaje_persona", ascending=True),
            use_container_width=True,
            height=420,
        )

    # Separar este bloque al final para dejar primero el analisis de encuesta.
    render_app_usage_analysis(usability_events_df, sessions_df)


if __name__ == "__main__":
    main()
