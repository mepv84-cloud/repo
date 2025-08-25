
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Mockup KPI | Estático", layout="wide")

st.title("📊 Mockup KPI de Cumplimiento")
st.caption("Versión estática (sin CSV) para validar render en Streamlit Cloud.")

# Datos fijos de ejemplo (sin necesidad de archivos externos)
df = pd.DataFrame({
    "etapa": ["Recepción", "Preparación", "Análisis", "Revisión", "Informe"],
    "cumplidas": [92, 85, 78, 88, 95],
    "total":     [100, 100, 100, 100, 100],
})
df["incumplidas"] = df["total"] - df["cumplidas"]
df["pct_cumplimiento"] = df["cumplidas"] / df["total"] * 100

# KPI general
total_total = df["total"].sum()
total_cumplidas = df["cumplidas"].sum()
total_incumplidas = df["incumplidas"].sum()
pct_general = (total_cumplidas/total_total*100) if total_total else 0

# Fila superior: Donut general + barras
col1, col2 = st.columns([1.1, 1.6], gap="large")

with col1:
    st.subheader("✅ KPI General")
    fig_general = go.Figure(data=[go.Pie(
        labels=["Cumplidas","No Cumplidas"],
        values=[total_cumplidas,total_incumplidas],
        hole=0.65,
        textinfo="percent+label",
        hovertemplate="%{label}: %{value}<extra></extra>",
        sort=False
    )])
    fig_general.update_traces(marker=dict(colors=["#16a34a","#ef4444"], line=dict(color="white", width=2)))
    fig_general.update_layout(showlegend=False, margin=dict(l=10,r=10,t=10,b=10),
                              annotations=[dict(text=f"{pct_general:.1f}%", x=0.5, y=0.5, font_size=28, showarrow=False)])
    st.plotly_chart(fig_general, use_container_width=True)

with col2:
    st.subheader("🧭 % por Etapa")
    fig_barras = px.bar(
        df.sort_values("pct_cumplimiento", ascending=True),
        x="pct_cumplimiento", y="etapa",
        orientation="h",
        text=df["pct_cumplimiento"].map(lambda x: f"{x:.1f}%"),
        labels={"pct_cumplimiento":"% Cumplimiento","etapa":"Etapa"},
    )
    fig_barras.update_traces(marker_color="#16a34a", textposition="outside")
    fig_barras.update_layout(xaxis=dict(range=[0,100]), margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig_barras, use_container_width=True)

st.divider()
st.subheader("🧩 Anillos por Etapa (fijo)")
cols = st.columns(3)
for i, row in enumerate(df.itertuples(index=False)):
    with cols[i % 3]:
        fig = go.Figure(data=[go.Pie(
            labels=["Cumplidas","No Cumplidas"],
            values=[row.cumplidas, row.total - row.cumplidas],
            hole=0.65, textinfo="percent+label", sort=False)])
        fig.update_traces(marker=dict(colors=["#16a34a","#ef4444"], line=dict(color="white", width=2)))
        fig.update_layout(showlegend=False, margin=dict(l=10,r=10,t=10,b=10),
                          annotations=[dict(text=f"{row.cumplidas/row.total*100:.1f}%", x=0.5, y=0.5, font_size=18, showarrow=False)],
                          title=dict(text=f"Etapa: {row.etapa}", x=0.5, xanchor="center"))
        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("📄 Tabla (fija)")
st.dataframe(df, use_container_width=True)
