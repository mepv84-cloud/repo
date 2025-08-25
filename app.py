
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Lab Dashboard (React en Streamlit)", layout="wide")

# Lee el JSX (debes subirlo junto a app.py en el repo)
jsx_path = Path("copia_de_lab_response_time_ui.jsx")
if not jsx_path.exists():
    st.error("No encuentro 'copia_de_lab_response_time_ui.jsx' junto a app.py. Sube o copia el archivo a la misma carpeta y recarga.")
    st.stop()

code = jsx_path.read_text(encoding="utf-8")

# Preprocesa: quita 'use client', elimina imports/exports ESM,
# y convierte 'export default function Nombre' en 'function Nombre'
processed = []
component_name = "LabDashboard"  # fallback si no se detecta
for line in code.splitlines():
    s = line.strip()
    if s.startswith("'use client'") or s.startswith('"use client"'):
        continue
    if s.startswith("import "):
        continue
    if s.startswith("export default function "):
        # Detecta el nombre del componente principal
        try:
            after = s.replace("export default function", "").strip()
            name = after.split("(")[0].strip()
            if name:
                component_name = name
        except Exception:
            pass
        line = line.replace("export default ", "")
    if s.startswith("export default "):
        # export default Nombre; -> omitimos y renderizamos component_name
        continue
    processed.append(line)

code_no_modules = "\n".join(processed)

# HTML que inyecta React/ReactDOM/Recharts/Tailwind por CDN y transpila JSX con Babel
html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Lab Dashboard</title>

  <!-- Tailwind -->
  <script src="https://cdn.tailwindcss.com"></script>

  <!-- React 18 UMD -->
  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>

  <!-- Recharts UMD (usado por tu JSX) -->
  <script crossorigin src="https://unpkg.com/recharts/umd/Recharts.min.js"></script>

  <!-- Babel para transpilar JSX en el navegador -->
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

  <style>
    html, body, #root {{ height: 100%; }}
    body {{ background-color: #f3f4f6; }}
  </style>
</head>
<body>
  <div id="root"></div>

  <!-- Tu JSX original -->
  <script type="text/babel">
{code_no_modules}

    // Render del componente principal detectado: {component_name}
    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(React.createElement({component_name}));
  </script>
</body>
</html>
"""

st.components.v1.html(html, height=1000, scrolling=True)
