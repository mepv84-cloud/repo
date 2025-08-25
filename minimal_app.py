
import streamlit as st

st.set_page_config(page_title="Prueba mínima", layout="centered")
st.title("✅ Streamlit está funcionando")
st.write("Si ves este texto, tu despliegue funciona.")

# Gráfico simple
import plotly.express as px
fig = px.line(x=[1,2,3,4], y=[1,4,2,5], labels={"x":"X","y":"Y"}, title="Linea de prueba")
st.plotly_chart(fig, use_container_width=True)
