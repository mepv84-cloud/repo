
import streamlit as st
import math

st.set_page_config(page_title="Mockup KPI | Solo Streamlit (SVG)", layout="wide")
st.title("📊 Mockup KPI de Cumplimiento")
st.caption("Versión **sin dependencias externas**: gráficos hechos con SVG/HTML. Ideal para Streamlit Cloud.")

# ---------- Datos fijos ----------
etapas = ["Recepción", "Preparación", "Análisis", "Revisión", "Informe"]
cumplidas = [92, 85, 78, 88, 95]
total = [100, 100, 100, 100, 100]
incumplidas = [t - c for t, c in zip(total, cumplidas)]
pct = [ (c/t*100 if t else 0.0) for c, t in zip(cumplidas, total) ]

total_total = sum(total)
total_c = sum(cumplidas)
total_i = sum(incumplidas)
pct_general = (total_c/total_total*100) if total_total else 0.0

# ---------- Utilidades ----------
def donut_svg(percent, size=220, stroke=22, color_ok="#16a34a", color_no="#ef4444", label=""):
    "Genera un donut SVG (percent de 0 a 100)."
    radius = (size - stroke) / 2
    cx = cy = size/2
    circumference = 2 * math.pi * radius
    done = max(0, min(100, percent)) / 100.0 * circumference
    remain = circumference - done
    # fondo (no cumplido) + arco cumplido
    svg = (
        f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" stroke="{color_no}" stroke-width="{stroke}" '
        f'fill="none" stroke-linecap="round" stroke-dasharray="{circumference} {circumference}" />'
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" stroke="{color_ok}" stroke-width="{stroke}" '
        f'fill="none" stroke-linecap="round" '
        f'stroke-dasharray="{done} {remain}" transform="rotate(-90 {cx} {cy})" />'
        f'<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" '
        f'font-size="{size*0.18:.0f}" font-family="ui-sans-serif, system-ui" fill="#111827">{percent:.1f}%</text>'
        f'<text x="50%" y="{size*0.92:.0f}" dominant-baseline="middle" text-anchor="middle" '
        f'font-size="{size*0.10:.0f}" font-family="ui-sans-serif, system-ui" fill="#374151">{label}</text>'
        f'</svg>'
    )
    return svg

def bar_row(label, percent, color="#16a34a"):
    "Fila de barra horizontal simple en HTML/CSS."
    pct_str = f"{percent:.1f}%"
    bar_html = (
        '<div style="margin:6px 0; font-family:ui-sans-serif, system-ui;">'
        '<div style="display:flex; justify-content:space-between; margin-bottom:4px;">'
        f'<span style="color:#111827;">{label}</span>'
        f'<span style="color:#111827; font-variant-numeric:tabular-nums;">{pct_str}</span>'
        '</div>'
        '<div style="background:#e5e7eb; border-radius:10px; height:16px; position:relative; overflow:hidden;">'
        f'<div style="width:{percent}%; background:{color}; height:100%;"></div>'
        '</div>'
        '</div>'
    )
    return bar_html

# ---------- Layout superior ----------
col1, col2 = st.columns([1.1, 1.6], gap="large")

with col1:
    st.subheader("✅ KPI General")
    st.markdown(donut_svg(pct_general, size=240, stroke=26, label="Cumplimiento"), unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="font-family:ui-sans-serif, system-ui; margin-top:8px; color:#374151;">
          <b>Muestras totales:</b> {total_total} &nbsp; | &nbsp;
          <span style="color:#16a34a;"><b>Cumplidas:</b> {total_c}</span> &nbsp; | &nbsp;
          <span style="color:#ef4444;"><b>No Cumplidas:</b> {total_i}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.subheader("🧭 % por Etapa")
    bars_html = "".join(bar_row(e, p) for e, p in sorted(zip(etapas, pct), key=lambda x: x[1]))
    st.markdown(f'<div style="padding-right:8px;">{bars_html}</div>', unsafe_allow_html=True)

st.divider()
st.subheader("🧩 Anillos por Etapa (fijo)")
cols = st.columns(3)
for i, (e, p) in enumerate(zip(etapas, pct)):
    svg = donut_svg(p, size=200, stroke=22, label=e)
    with cols[i % 3]:
        st.markdown(svg, unsafe_allow_html=True)

st.divider()
st.subheader("📄 Datos (fijos)")
# Muestra tabla simple sin pandas
table_rows = "".join(
    f"<tr><td>{e}</td><td style='text-align:right'>{c}</td><td style='text-align:right'>{t}</td><td style='text-align:right'>{p:.1f}%</td></tr>"
    for e, c, t, p in zip(etapas, cumplidas, total, pct)
)
st.markdown(f"""
<table style="width:100%; border-collapse:collapse; font-family:ui-sans-serif, system-ui;">
  <thead>
    <tr style="background:#f3f4f6">
      <th style="text-align:left; padding:8px;">Etapa</th>
      <th style="text-align:right; padding:8px;">Cumplidas</th>
      <th style="text-align:right; padding:8px;">Total</th>
      <th style="text-align:right; padding:8px;">% Cumplimiento</th>
    </tr>
  </thead>
  <tbody>
    {table_rows}
  </tbody>
</table>
""", unsafe_allow_html=True)
