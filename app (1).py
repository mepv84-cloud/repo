
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Mockup KPI | Ligero", layout="wide")

st.title("📊 Mockup KPI (Ligero, sin pandas)")
st.caption("Versión sin CSV ni pandas para minimizar dependencias.")

# Datos fijos
etapas = ["Recepción", "Preparación", "Análisis", "Revisión", "Informe"]
cumplidas = [92, 85, 78, 88, 95]
total = [100, 100, 100, 100, 100]
incumplidas = [t - c for t, c in zip(total, cumplidas)]
pct = [c/t*100 if t else 0 for c, t in zip(cumplidas, total)]

total_total = sum(total)
total_cumplidas = sum(cumplidas)
total_incumplidas = sum(incumplidas)
pct_general = (total_cumplidas/total_total*100) if total_total else 0

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
    # Usamos Plotly Express con una estructura dict
    data_sorted = sorted(zip(etapas, pct), key=lambda x: x[1])
    etapas_sorted = [e for e,_ in data_sorted]
    pct_sorted = [p for _,p in data_sorted]
    fig_barras = px.bar(
        {"etapa": etapas_sorted, "pct": pct_sorted},
        x="pct", y="etapa",
        orientation="h",
        text=[f"{x:.1f}%" for x in pct_sorted],
        labels={"pct":"% Cumplimiento","etapa":"Etapa"},
    )
    fig_barras.update_traces(marker_color="#16a34a", textposition="outside")
    fig_barras.update_layout(xaxis=dict(range=[0,100]), margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig_barras, use_container_width=True)

st.divider()
st.subheader("🧩 Anillos por Etapa (fijo)")
cols = st.columns(3)
for i, (e, c, t) in enumerate(zip(etapas, cumplidas, total)):
    fig = go.Figure(data=[go.Pie(
        labels=["Cumplidas","No Cumplidas"],
        values=[c, t-c],
        hole=0.65, textinfo="percent+label", sort=False)])
    fig.update_traces(marker=dict(colors=["#16a34a","#ef4444"], line=dict(color="white", width=2)))
    fig.update_layout(showlegend=False, margin=dict(l=10,r=10,t=10,b=10),
                      annotations=[dict(text=f"{(c/t*100):.1f}%", x=0.5, y=0.5, font_size=18, showarrow=False)],
                      title=dict(text=f"Etapa: {e}", x=0.5, xanchor="center"))
    with cols[i % 3]:
        st.plotly_chart(fig, use_container_width=True)
