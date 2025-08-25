
import streamlit as st
from pathlib import Path
import re

st.set_page_config(page_title="Lab Dashboard (React en Streamlit)", layout="wide")

jsx_path = Path("copia_de_lab_response_time_ui.jsx")
if not jsx_path.exists():
    st.error("No encuentro 'copia_de_lab_response_time_ui.jsx' junto a app.py. Sube el archivo al repo (misma carpeta) y recarga.")
    st.stop()

code = jsx_path.read_text(encoding="utf-8")

# --- Detecta nombre del componente por defecto ---
# Soporta:
#   export default function Nombre(...
#   export default Nombre;
default_name = "LabDashboard"
m = re.search(r'export\s+default\s+function\s+([A-Za-z0-9_]+)\s*\(', code)
if m:
    default_name = m.group(1)
else:
    m2 = re.search(r'export\s+default\s+([A-Za-z0-9_]+)\s*;?', code)
    if m2:
        default_name = m2.group(1)

# --- Preprocesa: elimina 'use client', imports/exports de ESM ---
processed = []
for line in code.splitlines():
    s = line.strip()
    if s.startswith("'use client'") or s.startswith('"use client"'):
        continue
    if s.startswith("import "):
        continue
    if s.startswith("export default function "):
        # Reemplaza por function Nombre
        line = line.replace("export default ", "")
    elif s.startswith("export default "):
        # Omitimos esta línea (ya detectamos el nombre antes)
        continue
    elif s.startswith("export "):
        # Quita 'export ' en funciones/const nombradas
        line = line.replace("export ", "")
    processed.append(line)

code_no_modules = "\n".join(processed)

# --- HTML con shims para React/Recharts y captura de errores ---
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

  <!-- Recharts UMD -->
  <script crossorigin src="https://unpkg.com/recharts/umd/Recharts.min.js"></script>

  <!-- Babel para transpilar JSX en el navegador -->
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

  <style>
    html, body, #root {{ height: 100%; }}
    body {{ background-color: #f3f4f6; }}
    .errbox {{ background:#fee2e2; border:1px solid #ef4444; color:#991b1b; padding:12px; border-radius:12px; margin:16px; font-family:ui-sans-serif,system-ui; }}
    .warnbox {{ background:#fef9c3; border:1px solid #eab308; color:#713f12; padding:10px; border-radius:10px; margin:16px; }}
  </style>
</head>
<body>
  <div id="errors"></div>
  <div id="root"></div>

  <script>
    // Captura errores para mostrarlos en pantalla (no solo consola)
    window.addEventListener('error', function(e) {{
      const box = document.createElement('div');
      box.className = 'errbox';
      box.textContent = 'Error: ' + (e.message || e.error);
      document.getElementById('errors').appendChild(box);
    }});
    window.addEventListener('unhandledrejection', function(e) {{
      const box = document.createElement('div');
      box.className = 'errbox';
      box.textContent = 'Unhandled Rejection: ' + (e.reason && (e.reason.message || e.reason)) ;
      document.getElementById('errors').appendChild(box);
    }});
  </script>

  <!-- Shim de identificadores comunes antes del JSX del usuario -->
  <script type="text/babel">
    // React hooks y helpers en scope (por si el JSX hacía import {{ useState, useEffect, ... }})
    const useState = React.useState;
    const useEffect = React.useEffect;
    const useMemo = React.useMemo;
    const useRef = React.useRef;
    const Fragment = React.Fragment;

    // Recharts en scope con nombres de componentes JSX
    const R = (window.Recharts || {{}});
    const ResponsiveContainer = R.ResponsiveContainer;
    const PieChart = R.PieChart, Pie = R.Pie, Cell = R.Cell;
    const BarChart = R.BarChart, Bar = R.Bar;
    const LineChart = R.LineChart, Line = R.Line;
    const AreaChart = R.AreaChart, Area = R.Area;
    const RadialBarChart = R.RadialBarChart, RadialBar = R.RadialBar;
    const CartesianGrid = R.CartesianGrid, XAxis = R.XAxis, YAxis = R.YAxis, ZAxis = R.ZAxis;
    const Tooltip = R.Tooltip, Legend = R.Legend, Brush = R.Brush, ReferenceLine = R.ReferenceLine;
    const ComposedChart = R.ComposedChart, ScatterChart = R.ScatterChart, Scatter = R.Scatter;

    // Warn si Recharts no cargó
    if (!window.Recharts) {{
      const w = document.createElement('div');
      w.className = 'warnbox';
      w.textContent = 'Aviso: Recharts no cargó desde CDN. Revisa la conexión o bloqueos de red.';
      document.getElementById('errors').appendChild(w);
    }}
  </script>

  <!-- Tu JSX original (ya sin imports/exports) -->
  <script type="text/babel">
{code_no_modules}

    // Render seguro con try/catch y nombre detectado: {default_name}
    try {{
      const mount = ReactDOM.createRoot(document.getElementById('root'));
      if (typeof {default_name} !== 'function') {{
        throw new Error('No se encontró el componente por defecto "{default_name}". Verifica el export default en tu JSX.');
      }}
      mount.render(React.createElement({default_name}));
    }} catch (err) {{
      const box = document.createElement('div');
      box.className = 'errbox';
      box.textContent = 'Render error: ' + (err && err.message ? err.message : err);
      document.getElementById('errors').appendChild(box);
      console.error(err);
    }}
  </script>
</body>
</html>
"""

st.components.v1.html(html, height=1100, scrolling=True)
