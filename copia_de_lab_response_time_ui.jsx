'use client';

import React, { useState } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

// ==== UI MINIMAL (sin dependencias externas) ====
function Card({ className = '', children }) {
  return <div className={`bg-white rounded-2xl shadow ${className}`}>{children}</div>;
}
function CardContent({ className = '', children }) {
  return <div className={className}>{children}</div>;
}
function Button({ variant = 'default', size = 'md', className = '', ...props }) {
  const base = 'rounded-2xl px-4 py-2 text-sm font-medium shadow';
  const v = variant === 'outline' ? 'border border-gray-300 bg-white text-gray-700' : 'bg-gray-900 text-white';
  const s = size === 'sm' ? 'px-3 py-1.5 text-sm' : '';
  return <button className={`${base} ${v} ${s} ${className}`} {...props} />;
}
function Input({ className = '', ...props }) {
  return <input className={`border rounded p-2 text-sm w-full ${className}`} {...props} />;
}
function Progress({ value = 0 }) {
  const v = Math.min(100, Math.max(0, value));
  return (
    <div className="w-full h-2 bg-gray-200 rounded">
      <div className="h-2 bg-gray-900 rounded" style={{ width: `${v}%` }} />
    </div>
  );
}

// ==== CONSTANTES ====
const STAGE_DEADLINES = {
  Ingreso: 5,
  Pesaje: 70,
  Ataque: 300,
  Lectura: 60,
  Reporte: 60,
  'Validación de resultados': 5,
};
const DEFAULT_STAGES = [
  { name: 'Ingreso', start: null, end: null, completed: false },
  { name: 'Pesaje', start: null, end: null, completed: false },
  { name: 'Ataque', start: null, end: null, completed: false },
  { name: 'Lectura', start: null, end: null, completed: false },
  { name: 'Reporte', start: null, end: null, completed: false },
  { name: 'Validación de resultados', start: null, end: null, completed: false },
];
const SHEET_DEADLINE_LABEL = '8h 20m';

const fmtDateKey = (d = new Date()) => {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
};
const fmtSheetName = (d = new Date(), n = 1) => {
  const dd = String(d.getDate()).padStart(2, '0');
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  return `${dd}-${mm}-${yyyy}/${n}`;
};

export default function LabDashboard() {
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' | 'kpi' | 'ingreso'
  const [sheetCountByDate, setSheetCountByDate] = useState({});

  // Hojas de trabajo (cada hoja con múltiples muestras)
  const [sheets, setSheets] = useState(() => {
    const samples = Array.from({ length: 20 }, (_, i) => ({
      id: i + 1,
      name: `Muestra ${i + 1}`,
      addedAt: new Date(),
      stages: JSON.parse(JSON.stringify(DEFAULT_STAGES)),
      type: i % 2 === 0 ? 'Metálico' : 'No Metálico',
      analyst: '—',
    }));
    const createdAt = new Date();
    const dateKey = fmtDateKey(createdAt);
    const initialCount = 1;
    return [
      {
        id: Math.random().toString(36).slice(2),
        name: fmtSheetName(createdAt, initialCount),
        createdAt,
        dateKey,
        samples,
      },
    ];
  });

  const [filterDate, setFilterDate] = useState('');
  const [selectedSheetId, setSelectedSheetId] = useState('');
  const [expandedSheets, setExpandedSheets] = useState([]);
  const [bulkRows, setBulkRows] = useState([{ id: '', name: '', type: 'Metálico', analyst: '' }]);

  React.useEffect(() => {
    if (!selectedSheetId && sheets[0]?.id) setSelectedSheetId(sheets[0].id);
  }, [sheets, selectedSheetId]);

  const stagesList = Object.keys(STAGE_DEADLINES);

  const calculateSampleProgress = (stages) => {
    const total = stages.length;
    const done = stages.filter((s) => s.completed).length;
    return (done / total) * 100;
  };
  const calculateSheetProgress = (sheet) => {
    if (!sheet.samples.length) return 0;
    const sum = sheet.samples.reduce((acc, s) => acc + calculateSampleProgress(s.stages), 0);
    return sum / sheet.samples.length;
  };
  const getElapsedTime = (addedAt) => {
    const now = new Date();
    const diffMs = now - new Date(addedAt);
    const diffHours = Math.floor(diffMs / 1000 / 60 / 60);
    const diffMinutes = Math.floor((diffMs / 1000 / 60) % 60);
    return `${diffHours}h ${diffMinutes}m`;
  };

  // KPI mock
  const complianceGeneral = 87;
  const complianceByStage = [
    { name: 'Ingreso', value: 95 },
    { name: 'Pesaje', value: 85 },
    { name: 'Ataque', value: 80 },
    { name: 'Lectura', value: 75 },
    { name: 'Reporte', value: 70 },
    { name: 'Validación', value: 90 },
  ];
  const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

  // Registrar hora para TODA una hoja, con analista opcional
  const registerStageTimeForSheet = (sheetId, stageName, type, analystName) => {
    setSheets((prev) =>
      prev.map((sheet) => {
        if (sheet.id !== sheetId) return sheet;
        const nowLabel = new Date().toLocaleTimeString();
        return {
          ...sheet,
          samples: sheet.samples.map((s) => ({
            ...s,
            analyst: analystName ? analystName : s.analyst,
            stages: s.stages.map((st) => {
              if (st.name !== stageName) return st;
              return type === 'inicio' ? { ...st, start: st.start || nowLabel } : { ...st, end: nowLabel, completed: true };
            }),
          })),
        };
      })
    );
  };

  const toggleExpand = (sheetId) => {
    setExpandedSheets((prev) => (prev.includes(sheetId) ? prev.filter((id) => id !== sheetId) : [...prev, sheetId]));
  };

  const addBulkRow = () => setBulkRows((rows) => [...rows, { id: '', name: '', type: 'Metálico', analyst: '' }]);
  const removeBulkRow = (idx) => setBulkRows((rows) => rows.filter((_, i) => i !== idx));
  const updateBulkRow = (idx, field, value) => setBulkRows((rows) => rows.map((r, i) => (i === idx ? { ...r, [field]: value } : r)));

  const saveBatch = () => {
    const sanitized = bulkRows
      .map((r) => ({ ...r, id: String(r.id).trim(), name: r.name.trim(), analyst: r.analyst.trim() }))
      .filter((r) => r.id !== '' && (r.type === 'Metálico' || r.type === 'No Metálico'));
    if (!sanitized.length) return;

    const newSamples = sanitized.map((r) => ({
      id: isNaN(Number(r.id)) ? r.id : Number(r.id),
      name: r.name || `Muestra ${r.id}`,
      addedAt: new Date(),
      stages: JSON.parse(JSON.stringify(DEFAULT_STAGES)),
      type: r.type,
      analyst: r.analyst || '—',
    }));

    const createdAt = new Date();
    const dateKey = fmtDateKey(createdAt);
    const count = (sheetCountByDate[dateKey] || 0) + 1; // reinicia por fecha

    const newSheet = {
      id: Math.random().toString(36).slice(2),
      name: fmtSheetName(createdAt, count),
      createdAt,
      dateKey,
      samples: newSamples,
    };

    setSheets((prev) => [newSheet, ...prev]);
    setSheetCountByDate((prev) => ({ ...prev, [dateKey]: count }));
    setSelectedSheetId(newSheet.id);
    setBulkRows([{ id: '', name: '', type: 'Metálico', analyst: '' }]);
    setActiveTab('dashboard');
  };

  const filteredSheets = sheets.filter((s) => (filterDate ? s.dateKey === filterDate : true));

  // KPI derivados
  const totalMuestras = sheets.reduce((acc, sh) => acc + sh.samples.length, 0);
  const muestrasCompletas = sheets.reduce((acc, sh) => acc + sh.samples.filter((s) => s.stages.every((st) => st.completed)).length, 0);
  const muestrasEnCurso = totalMuestras - muestrasCompletas;

  // Filtros y distribución (mock)
  const allSamples = sheets.flatMap((sh) => sh.samples);
  const analystOptions = ['Todos', ...Array.from(new Set(allSamples.map((s) => s.analyst).filter(Boolean)))];
  const [filterAnalystKPI, setFilterAnalystKPI] = useState('Todos');
  const samplesForKPI = filterAnalystKPI === 'Todos' ? allSamples : allSamples.filter((s) => s.analyst === filterAnalystKPI);

  const stageNames = Object.keys(STAGE_DEADLINES);
  const avgByStage = stageNames.map((st) => {
    const base = STAGE_DEADLINES[st];
    const factor = 0.9 + ((st.charCodeAt(0) % 5) * 0.03);
    return { etapa: st, minutos: Math.round(base * factor) };
  });
  const totalBase = Object.values(STAGE_DEADLINES).reduce((a, b) => a + b, 0);
  const tatSamples = samplesForKPI.length ? samplesForKPI : allSamples;
  const simulatedTAT = tatSamples.map((s, i) => {
    const baseId = typeof s.id === 'number' ? s.id : i;
    const factor = 0.85 + ((baseId % 7) * 0.04);
    return Math.round(totalBase * factor);
  });
  const buckets = [
    { rango: '0-120', min: 0, max: 120 },
    { rango: '121-240', min: 121, max: 240 },
    { rango: '241-360', min: 241, max: 360 },
    { rango: '361-480', min: 361, max: 480 },
    { rango: '481-600', min: 481, max: 600 },
    { rango: '>600', min: 601, max: Infinity },
  ];
  const tatHistogram = buckets.map((b) => ({ rango: b.rango, muestras: simulatedTAT.filter((v) => v >= b.min && v <= b.max).length }));

  // Estado UI registro rápido
  const [stageAction, setStageAction] = useState(stagesList[0] || 'Ingreso');
  const [actionType, setActionType] = useState('inicio');
  const [actionAnalyst, setActionAnalyst] = useState('');

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Header */}
      <header className="mb-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold">Dashboard de Laboratorio</h1>
        <div className="flex gap-2">
          <Button variant={activeTab === 'dashboard' ? 'default' : 'outline'} onClick={() => setActiveTab('dashboard')}>Panel</Button>
          <Button variant={activeTab === 'kpi' ? 'default' : 'outline'} onClick={() => setActiveTab('kpi')}>KPI</Button>
          <Button variant={activeTab === 'ingreso' ? 'default' : 'outline'} onClick={() => setActiveTab('ingreso')}>Ingreso de Muestras</Button>
          <Button variant="outline">Cerrar Sesión</Button>
        </div>
      </header>

      {activeTab === 'kpi' && (
        <>
          {/* Filtro KPI */}
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <label className="text-sm">Analista:</label>
            <select className="border rounded p-2 text-sm" value={filterAnalystKPI} onChange={(e) => setFilterAnalystKPI(e.target.value)}>
              {analystOptions.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>

          {/* Resumen */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <Card>
              <CardContent className="p-6 text-center">
                <h2 className="text-lg font-semibold mb-2">Cumplimiento General</h2>
                <div className="relative">
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie
                        data={[{ name: 'Cumplido', value: complianceGeneral }, { name: 'Incumplido', value: 100 - complianceGeneral }]}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
                        dataKey="value"
                      >
                        <Cell fill="#10B981" />
                        <Cell fill="#E5E7EB" />
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <span className="text-2xl font-bold">{complianceGeneral}%</span>
                  </div>
                </div>
                <div className="mt-3 text-sm text-gray-500">SLA global: {SHEET_DEADLINE_LABEL}</div>
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardContent className="p-6">
                <h2 className="text-lg font-semibold mb-4">Resumen Operacional</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white rounded-2xl shadow p-4">
                    <div className="text-sm text-gray-500">Muestras totales</div>
                    <div className="text-3xl font-bold">{totalMuestras}</div>
                  </div>
                  <div className="bg-white rounded-2xl shadow p-4">
                    <div className="text-sm text-gray-500">En curso</div>
                    <div className="text-3xl font-bold">{muestrasEnCurso}</div>
                  </div>
                  <div className="bg-white rounded-2xl shadow p-4">
                    <div className="text-sm text-gray-500">Completadas</div>
                    <div className="text-3xl font-bold">{muestrasCompletas}</div>
                  </div>
                  <div className="bg-white rounded-2xl shadow p-4">
                    <div className="text-sm text-gray-500">T. resp. promedio</div>
                    <div className="text-3xl font-bold">4.2h</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Cumplimiento por etapa (anillos) */}
          <Card className="mb-6">
            <CardContent className="p-6">
              <h2 className="text-lg font-semibold mb-4">% Cumplimiento por Etapa</h2>
              <div className="flex flex-wrap gap-6 justify-center">
                {complianceByStage.map((c, idx) => (
                  <div key={c.name} className="text-center">
                    <div style={{ width: 140, height: 140 }} className="relative">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={[{ name: 'Cumplido', value: c.value }, { name: 'Incumplido', value: 100 - c.value }]}
                            cx="50%"
                            cy="50%"
                            innerRadius={40}
                            outerRadius={60}
                            dataKey="value"
                          >
                            <Cell fill={COLORS[idx % COLORS.length]} />
                            <Cell fill="#E5E7EB" />
                          </Pie>
                        </PieChart>
                      </ResponsiveContainer>
                      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <span className="text-sm font-semibold">{c.value}%</span>
                      </div>
                    </div>
                    <div className="mt-2 text-sm font-medium">{c.name}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Cuellos de botella */}
          <Card className="mb-6">
            <CardContent className="p-6">
              <h2 className="text-lg font-semibold mb-4">Tiempo promedio por etapa (min)</h2>
              <div className="w-full h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={avgByStage} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="etapa" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="minutos" name="Minutos" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="text-xs text-gray-500 mt-2">* Valores simulados a partir de los deadlines.</p>
            </CardContent>
          </Card>

          {/* Distribución TAT */}
          <Card>
            <CardContent className="p-6">
              <h2 className="text-lg font-semibold mb-4">Distribución de TAT por muestra (min)</h2>
              <div className="w-full h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={tatHistogram} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="rango" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="muestras" name="# Muestras" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="text-xs text-gray-500 mt-2">* Muestras consideradas: {samplesForKPI.length}. Mock para demo.</p>
            </CardContent>
          </Card>
        </>
      )}

      {activeTab === 'dashboard' && (
        <>
          {/* Tarjetas compactas */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <Card>
              <CardContent className="p-6 text-center">
                <h2 className="text-lg font-semibold">Tiempo Promedio</h2>
                <p className="text-3xl font-bold">4.2h</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <h2 className="text-lg font-semibold">T. por Etapa</h2>
                <p className="text-sm">Ver en KPI</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <h2 className="text-lg font-semibold">% Cumplimiento</h2>
                <div className="relative">
                  <ResponsiveContainer width="100%" height={120}>
                    <PieChart>
                      <Pie data={[{ value: complianceGeneral }, { value: 100 - complianceGeneral }]} cx="50%" cy="50%" innerRadius={35} outerRadius={55} dataKey="value">
                        <Cell fill="#10B981" />
                        <Cell fill="#E5E7EB" />
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <span className="text-base font-bold">{complianceGeneral}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <h2 className="text-lg font-semibold">% por Etapa</h2>
                <ResponsiveContainer width="100%" height={120}>
                  <PieChart>
                    <Pie data={complianceByStage} dataKey="value" cx="50%" cy="50%" innerRadius={35} outerRadius={55}>
                      {complianceByStage.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-2 grid grid-cols-2 gap-1 text-[11px]">
                  {complianceByStage.map((c, i) => (
                    <div key={c.name} className="flex items-center justify-between">
                      <span className="truncate">{c.name}</span>
                      <span className="font-semibold">{c.value}%</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filtro por fecha */}
          <div className="mb-3 flex items-center gap-3">
            <label className="text-sm">Filtrar por fecha:</label>
            <input type="date" className="border rounded p-2 text-sm" value={filterDate} onChange={(e) => setFilterDate(e.target.value)} />
            {filterDate && (<Button variant="outline" size="sm" onClick={() => setFilterDate('')}>Limpiar</Button>)}
          </div>

          {/* Hojas de trabajo */}
          <Card>
            <CardContent className="p-4">
              <h2 className="text-xl font-semibold mb-4">Hojas de trabajo</h2>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-sm">
                  <thead>
                    <tr className="bg-gray-200 text-left">
                      <th className="p-2">Nombre</th>
                      <th className="p-2">Creación</th>
                      <th className="p-2"># Muestras</th>
                      <th className="p-2">Progreso</th>
                      <th className="p-2">Deadline</th>
                      <th className="p-2">Detalle</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredSheets.map((sheet) => (
                      <React.Fragment key={sheet.id}>
                        <tr className="border-b hover:bg-gray-50">
                          <td className="p-2 font-medium">{sheet.name}</td>
                          <td className="p-2">{new Date(sheet.createdAt).toLocaleString('es-CL', { dateStyle: 'short', timeStyle: 'short' })}</td>
                          <td className="p-2">{sheet.samples.length}</td>
                          <td className="p-2">
                            <Progress value={calculateSheetProgress(sheet)} />
                            <span className="text-sm text-gray-500">{calculateSheetProgress(sheet).toFixed(0)}%</span>
                          </td>
                          <td className="p-2">{SHEET_DEADLINE_LABEL}</td>
                          <td className="p-2"><Button variant="outline" size="sm" onClick={() => toggleExpand(sheet.id)}>{expandedSheets.includes(sheet.id) ? 'Ocultar' : 'Ver'}</Button></td>
                        </tr>
                        {expandedSheets.includes(sheet.id) && (
                          <tr>
                            <td colSpan={6} className="p-0 bg-gray-50">
                              <div className="p-3">
                                <div className="text-sm font-medium mb-2">Muestras en {sheet.name}</div>
                                <div className="overflow-x-auto">
                                  <table className="w-full border-collapse text-xs">
                                    <thead>
                                      <tr className="bg-gray-200 text-left">
                                        <th className="p-2">ID</th>
                                        <th className="p-2">Nombre</th>
                                        <th className="p-2">Tipo</th>
                                        <th className="p-2">Analista</th>
                                        <th className="p-2">Progreso</th>
                                        <th className="p-2">Tiempo</th>
                                        <th className="p-2">Deadline</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {sheet.samples.map((s) => (
                                        <tr key={s.id} className="border-b">
                                          <td className="p-2">{s.id}</td>
                                          <td className="p-2">{s.name}</td>
                                          <td className="p-2">{s.type}</td>
                                          <td className="p-2">{s.analyst}</td>
                                          <td className="p-2">
                                            <Progress value={calculateSampleProgress(s.stages)} />
                                            <span className="text-[10px] text-gray-500">{calculateSampleProgress(s.stages).toFixed(0)}%</span>
                                          </td>
                                          <td className="p-2">{getElapsedTime(s.addedAt)}</td>
                                          <td className="p-2">{SHEET_DEADLINE_LABEL}</td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Registro rápido por hoja */}
          <Card className="mt-6">
            <CardContent className="p-4">
              <h2 className="text-lg font-semibold mb-2">Registro Rápido de Avance (por Hoja)</h2>
              <div className="flex flex-wrap gap-2 items-center">
                <select className="border rounded p-2 text-sm" value={selectedSheetId} onChange={(e) => setSelectedSheetId(e.target.value)}>
                  {filteredSheets.map((s) => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
                <select className="border rounded p-2 text-sm" value={stageAction} onChange={(e) => setStageAction(e.target.value)}>
                  {stagesList.map((stage) => (<option key={stage} value={stage}>{stage}</option>))}
                </select>
                <select className="border rounded p-2 text-sm" value={actionType} onChange={(e) => setActionType(e.target.value)}>
                  <option value="inicio">Registrar Inicio</option>
                  <option value="fin">Registrar Fin</option>
                </select>
                <Input className="w-48" placeholder="Analista" value={actionAnalyst} onChange={(e) => setActionAnalyst(e.target.value)} />
                <Button onClick={() => selectedSheetId && registerStageTimeForSheet(selectedSheetId, stageAction, actionType, actionAnalyst)}>Registrar Hora</Button>
              </div>
              <p className="text-xs text-gray-500 mt-2">* Aplica la hora del sistema a todas las muestras de la hoja seleccionada.</p>
            </CardContent>
          </Card>
        </>
      )}

      {activeTab === 'ingreso' && (
        <>
          <Card>
            <CardContent className="p-4">
              <h2 className="text-xl font-semibold mb-4">Ingreso de Muestras (Nueva hoja de trabajo)</h2>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-sm">
                  <thead>
                    <tr className="bg-gray-200 text-left">
                      <th className="p-2">ID</th>
                      <th className="p-2">Nombre/Descripción</th>
                      <th className="p-2">Tipo</th>
                      <th className="p-2">Analista</th>
                      <th className="p-2">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bulkRows.map((row, idx) => (
                      <tr key={idx} className="border-b">
                        <td className="p-2 w-32"><Input value={row.id} onChange={(e) => updateBulkRow(idx, 'id', e.target.value)} placeholder="ID" /></td>
                        <td className="p-2"><Input value={row.name} onChange={(e) => updateBulkRow(idx, 'name', e.target.value)} placeholder="Nombre o descripción" /></td>
                        <td className="p-2 w-48">
                          <select className="border rounded p-2 w-full" value={row.type} onChange={(e) => updateBulkRow(idx, 'type', e.target.value)}>
                            <option>Metálico</option>
                            <option>No Metálico</option>
                          </select>
                        </td>
                        <td className="p-2 w-56"><Input value={row.analyst} onChange={(e) => updateBulkRow(idx, 'analyst', e.target.value)} placeholder="Analista asignado" /></td>
                        <td className="p-2 w-32"><Button variant="outline" onClick={() => removeBulkRow(idx)}>Quitar</Button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="flex justify-between mt-4">
                <Button variant="outline" onClick={addBulkRow}>+ Agregar muestra</Button>
                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => setActiveTab('dashboard')}>Cancelar</Button>
                  <Button onClick={saveBatch}>Guardar hoja</Button>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-2">* Se crea una nueva hoja nombrada por fecha y número del día (ej. 18-08-2025/2).</p>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
