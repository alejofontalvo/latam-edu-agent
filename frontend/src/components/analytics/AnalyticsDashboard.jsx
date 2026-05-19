import { useEffect, useState } from "react";
import { Award, Gauge, GraduationCap, Users } from "lucide-react";
import { autoAnalytics, getBasicAnalytics, getDatasetFilters, overviewAnalytics, queryAnalytics } from "../../services/api.js";
import KpiCard from "../dashboard/KpiCard.jsx";
import ChartCard from "./ChartCard.jsx";
import FilterPanel from "./FilterPanel.jsx";
import InsightPanel from "./InsightPanel.jsx";
import EmptyState from "../ui/EmptyState.jsx";

export default function AnalyticsDashboard({ selectedDatasetId }) {
  const [analytics, setAnalytics] = useState(null);
  const [datasetFilters, setDatasetFilters] = useState({});
  const [filters, setFilters] = useState({ metric: "global_score" });
  const [chart, setChart] = useState(null);

  const load = async () => {
    if (!selectedDatasetId) {
      const overview = await overviewAnalytics({ query: "Genera un análisis general de todos los datos cargados." });
      setAnalytics({ dynamic: true, rows: overview.statistics?.kpis?.records || 0, score_means: {}, overview });
      setDatasetFilters({});
      setChart(overview.charts?.[0] || null);
      return;
    }
    const [basic, availableFilters] = await Promise.all([getBasicAnalytics(selectedDatasetId), getDatasetFilters(selectedDatasetId)]);
    setAnalytics(basic);
    setDatasetFilters(availableFilters);
    const initial = await queryAnalytics({ dataset_id: selectedDatasetId, metric: "global_score", operation: "mean", group_by: "region", filters: {} });
    setChart(initial);
  };

  useEffect(() => { load().catch(() => {}); }, [selectedDatasetId]);

  const run = async () => {
    if (!selectedDatasetId) {
      const result = await autoAnalytics({ query: "Analiza los datos disponibles y genera una gráfica." });
      setChart(result.charts?.[0] || null);
      setAnalytics((current) => ({ ...(current || {}), overview: result }));
      return;
    }
    const { metric, ...rawFilters } = filters;
    const cleanFilters = Object.fromEntries(Object.entries(rawFilters).filter(([, value]) => value));
    const result = await queryAnalytics({ dataset_id: selectedDatasetId, metric, operation: "mean", group_by: "region", filters: cleanFilters });
    setChart(result);
  };

  const scores = analytics?.score_means || {};
  const sortedAreas = Object.entries(scores).filter(([, v]) => v !== null).sort((a, b) => b[1] - a[1]);
  const dynamicKpis = analytics?.overview?.statistics?.kpis || {};
  const dynamicRows = dynamicKpis.records || analytics?.rows || 0;

  return (
    <div className="space-y-5">
      <div><p className="text-sm font-bold uppercase tracking-[0.25em] text-indigo-500">Análisis</p><h2 className="mt-2 text-3xl font-black">Dashboard analítico</h2></div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <KpiCard icon={Gauge} label={selectedDatasetId ? "Promedio global" : "Datasets"} value={selectedDatasetId ? (scores.global_score || 0).toFixed(1) : (dynamicKpis.datasets || 0).toLocaleString()} detail={selectedDatasetId ? "Dataset activo" : "Catálogo dinámico"} />
        <KpiCard icon={Award} label={selectedDatasetId ? "Mejor área" : "Países"} value={selectedDatasetId ? (sortedAreas[0]?.[0]?.replace("_score", "") || "N/D") : (dynamicKpis.countries || 0).toLocaleString()} detail={selectedDatasetId ? ((sortedAreas[0]?.[1] || 0).toFixed?.(1) || "") : "Detectados"} tone="emerald" />
        <KpiCard icon={GraduationCap} label={selectedDatasetId ? "Área crítica" : "Áreas"} value={selectedDatasetId ? (sortedAreas.at(-1)?.[0]?.replace("_score", "") || "N/D") : (dynamicKpis.subjects || 0).toLocaleString()} detail={selectedDatasetId ? ((sortedAreas.at(-1)?.[1] || 0).toFixed?.(1) || "") : "Normalizadas"} tone="amber" />
        <KpiCard icon={Users} label="Registros" value={dynamicRows.toLocaleString()} detail={selectedDatasetId ? "Estudiantes/resultados" : "Procesados"} tone="sky" />
      </div>
      {selectedDatasetId ? <FilterPanel filters={filters} setFilters={setFilters} datasetFilters={datasetFilters} onRun={run} /> : <EmptyState title="Análisis automático del catálogo completo" text="Puedes usar filtros opcionales arriba, pero el sistema puede analizar todos los datos disponibles sin selección previa." />}
      {chart && <ChartCard title={chart.title} data={chart.data} xKey={chart.x_key} yKey={chart.y_key} insight={chart.insight} />}
      <InsightPanel insight={chart?.insight || analytics?.overview?.insights?.join(" ")} />
      <div className="grid gap-4 xl:grid-cols-2">
        {analytics?.charts && Object.entries(analytics.charts).slice(0, 2).map(([key, item]) => (
          <ChartCard key={key} title={item.title} data={item.data} xKey={item.x_key} yKey={item.y_key} insight={item.insight} />
        ))}
      </div>
    </div>
  );
}
