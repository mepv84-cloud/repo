
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="KPI de Cumplimiento | Streamlit Nativo", layout="wide")

st.title("📊 KPI de Cumplimiento (General y por Etapa)")
st.caption("Versión nativa en Streamlit + Plotly (sin CDNs). Carga tu CSV o usa el ejemplo.")

with st.sidebar:
    st.header("⚙️ Configuración")
    st.markdown("**Formato CSV esperado (mínimo):**\n\n- `etapa` (texto)\n- `cumplidas` (int)\n- `total` (int)\n\nOpcional: `pendientes` (int) si deseas mostrarla explícitamente.")
    up = st.file_uploader("Sube tu CSV", type=["csv"])
    donut_hole = st.slider("Ancho del anillo (donut hole)", 0.4, 0.9, 0.65, 0.01)
    show_values = st.checkbox("Mostrar valores en etiquetas", value=True)
    color_ok = st.color_picker("Color Cumplidas", "#16a34a")   # verde
    color_no = st.color_picker("Color No Cumplidas", "#ef4444") # rojo
    color_pend = st.color_picker("Color Pendientes (opcional)", "#f59e0b") # ámbar

# ------------------ Datos ------------------
if up is not None:
    df_raw = pd.read_csv(up)
else:
    # Ejemplo
    df_raw = pd.DataFrame({
        "etapa": ["Recepción", "Preparación", "Análisis", "Revisión", "Informe"],
        "cumplidas": [92, 85, 78, 88, 95],
        "total":     [100, 100, 100, 100, 100],
    })

# Normalización de columnas mínimas
required_cols = {"etapa", "cumplidas", "total"}
missing = required_cols - set(df_raw.columns.str.lower())
# mapear por si el usuario usa mayúsculas o variantes
rename_map = {}
for c in df_raw.columns:
    cl = c.lower()
    if cl in required_cols and c != cl:
        rename_map[c] = cl
df = df_raw.rename(columns=rename_map)
for col in required_cols:
    if col not in df.columns:
        st.error(f"Falta la columna requerida: **{col}**")
        st.stop()

# Calcular incumplidas y pendientes si aplica
if "pendientes" in df.columns:
    # Asegurar tipos numéricos
    for c in ["cumplidas", "total", "pendientes"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    df["incumplidas"] = df["total"] - df["cumplidas"] - df["pendientes"]
else:
    for c in ["cumplidas", "total"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    df["incumplidas"] = (df["total"] - df["cumplidas"]).clip(lower=0)
    df["pendientes"] = 0

# % por etapa
df["pct_cumplimiento"] = np.where(df["total"]>0, df["cumplidas"] / df["total"] * 100.0, 0.0)
df["pct_incumplidas"] = np.where(df["total"]>0, df["incumplidas"] / df["total"] * 100.0, 0.0)
df["pct_pendientes"]  = np.where(df["total"]>0, df["pendientes"]  / df["total"] * 100.0, 0.0)

# KPI general
total_total = df["total"].sum()
total_cumplidas = df["cumplidas"].sum()
total_incumplidas = df["incumplidas"].sum()
total_pendientes = df["pendientes"].sum()
pct_general = (total_cumplidas / total_total * 100.0) if total_total>0 else 0.0

# ------------------ Layout ------------------
col1, col2 = st.columns([1.1, 1.6], gap="large")

with col1:
    st.subheader("✅ KPI General: % Cumplimiento (mes)")
    labels = ["Cumplidas", "No Cumplidas"]
    values = [total_cumplidas, total_incumplidas]
    colors = [color_ok, color_no]
    if total_pendientes > 0:
        labels.append("Pendientes")
        values.append(total_pendientes)
        colors.append(color_pend)

    fig_general = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=donut_hole,
        textinfo="percent+label" if show_values else "label",
        hovertemplate="%{label}: %{value}<extra></extra>",
        sort=False
    )])
    fig_general.update_traces(marker=dict(colors=colors, line=dict(color="white", width=2)))
    fig_general.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        annotations=[dict(text=f"{pct_general:.1f}%", x=0.5, y=0.5, font_size=28, showarrow=False)]
    )
    st.plotly_chart(fig_general, use_container_width=True)

with col2:
    st.subheader("🧭 % Cumplimiento por Etapa")
    # Barras de % cumplimiento
    fig_barras = px.bar(
        df.sort_values("pct_cumplimiento", ascending=True),
        x="pct_cumplimiento",
        y="etapa",
        orientation="h",
        text=df["pct_cumplimiento"].map(lambda x: f"{x:.1f}%") if show_values else None,
        labels={"pct_cumplimiento": "% Cumplimiento", "etapa": "Etapa"},
    )
    fig_barras.update_traces(marker_color=color_ok, textposition="outside")
    fig_barras.update_layout(
        xaxis=dict(range=[0, 100]),
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(categoryorder="array", categoryarray=df.sort_values("pct_cumplimiento")["etapa"].tolist())
    )
    st.plotly_chart(fig_barras, use_container_width=True)

st.divider()
st.subheader("🧩 Anillos por Etapa")
# Grid de donuts por etapa
cols = st.columns( min(4, max(2, int(np.ceil(len(df)/2)))) )
for i, (_, row) in enumerate(df.iterrows()):
    with cols[i % len(cols)]:
        cumplidas, incumplidas, pendientes = row["cumplidas"], row["incumplidas"], row["pendientes"]
        labels = ["Cumplidas", "No Cumplidas"]
        values = [cumplidas, incumplidas]
        colors = [color_ok, color_no]
        if pendientes > 0:
            labels.append("Pendientes")
            values.append(pendientes)
            colors.append(color_pend)
        pct = row["pct_cumplimiento"]
        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=donut_hole,
            textinfo="percent+label" if show_values else "label",
            hovertemplate="%{label}: %{value}<extra></extra>", sort=False)])
        fig.update_traces(marker=dict(colors=colors, line=dict(color="white", width=2)))
        fig.update_layout(showlegend=False, margin=dict(l=10,r=10,t=10,b=10),
                          annotations=[dict(text=f"{pct:.1f}%", x=0.5, y=0.5, font_size=18, showarrow=False)],
                          title=dict(text=f"Etapa: {row['etapa']}", x=0.5, xanchor="center"))
        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("📄 Tabla de datos")
st.dataframe(df, use_container_width=True)
