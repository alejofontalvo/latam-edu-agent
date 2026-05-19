import { useEffect, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getBasicAnalytics, getDatasetSummary, queryAnalytics } from "../services/api.js";

export default function Dashboard({ datasetId, selectedDataset }) {
  const [summary, setSummary] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [query, setQuery] = useState({ metric: "", group_by: "", operation: "mean" });
  const [queryResult, setQueryResult] = useState(null);

  useEffect(() => {
    if (!datasetId) {
      setSummary(null);
      setAnalytics(null);
      return;
    }
    getDatasetSummary(datasetId).then(setSummary);
    getBasicAnalytics(datasetId).then(setAnalytics);
  }, [datasetId]);

  const numericColumns = useMemo(() => analytics ? Object.keys(analytics.numeric_statistics || {}) : [], [analytics]);
  const allColumns = summary?.columns?.map((column) => column.name) || [];
  const chartData = queryResult?.chart_data?.length ? queryResult.chart_data : [];
  const valueKey = chartData[0] ? Object.keys(chartData[0]).find((key) => key !== query.group_by) : null;

  const submitQuery = async (event) => {
    event.preventDefault();
    if (!datasetId) return;
    const response = await queryAnalytics({
      dataset_id: Number(datasetId),
      metric: query.metric || null,
      group_by: query.group_by || null,
      operation: query.operation,
      filters: {}
    });
    setQueryResult(response);
  };

  if (!datasetId) {
    return <EmptyState text="Carga y selecciona un dataset para ver análisis estadístico." />;
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold">Análisis estadístico</h2>
        <p className="text-sm text-slate-600">Dataset activo: {selectedDataset?.name}</p>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        <Metric label="Filas" value={summary?.profile?.rows || 0} />
        <Metric label="Columnas" value={summary?.profile?.columns || 0} />
        <Metric label="Métricas numéricas" value={numericColumns.length} />
      </div>

      <form onSubmit={submitQuery} className="grid gap-3 border border-slate-200 p-4 md:grid-cols-4">
        <select className="input" value={query.metric} onChange={(event) => setQuery({ ...query, metric: event.target.value })}>
          <option value="">Conteo de filas</option>
          {numericColumns.map((column) => <option key={column} value={column}>{column}</option>)}
        </select>
        <select className="input" value={query.group_by} onChange={(event) => setQuery({ ...query, group_by: event.target.value })}>
          <option value="">Sin agrupación</option>
          {allColumns.map((column) => <option key={column} value={column}>{column}</option>)}
        </select>
        <select className="input" value={query.operation} onChange={(event) => setQuery({ ...query, operation: event.target.value })}>
          <option value="mean">Promedio</option>
          <option value="median">Mediana</option>
          <option value="std">Desviación estándar</option>
          <option value="min">Mínimo</option>
          <option value="max">Máximo</option>
          <option value="count">Conteo</option>
        </select>
        <button className="button bg-accent text-white">Analizar</button>
      </form>

      {chartData.length > 0 && valueKey && (
        <div className="h-96 border border-slate-200 p-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={query.group_by || "label"} tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey={valueKey} fill="#0f766e" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="grid gap-3 md:grid-cols-2">
        {numericColumns.slice(0, 8).map((column) => (
          <article key={column} className="border border-slate-200 p-4">
            <h3 className="font-semibold">{column}</h3>
            <dl className="mt-3 grid grid-cols-3 gap-2 text-sm">
              <MetricSmall label="Prom." value={analytics.numeric_statistics[column].mean} />
              <MetricSmall label="Med." value={analytics.numeric_statistics[column].median} />
              <MetricSmall label="P75" value={analytics.numeric_statistics[column].p75} />
            </dl>
          </article>
        ))}
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="border border-slate-200 p-4">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </div>
  );
}

function MetricSmall({ label, value }) {
  const formatted = typeof value === "number" ? value.toFixed(2) : value;
  return (
    <div>
      <dt className="text-slate-500">{label}</dt>
      <dd className="font-semibold">{formatted}</dd>
    </div>
  );
}

function EmptyState({ text }) {
  return <div className="flex min-h-96 items-center justify-center border border-dashed border-slate-300 text-slate-600">{text}</div>;
}
