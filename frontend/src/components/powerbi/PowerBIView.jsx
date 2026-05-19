import { useEffect, useState } from "react";
import { Database, FileSpreadsheet, Link2, PieChart } from "lucide-react";
import { getPowerBiCatalog, getPowerBiComparisons, getPowerBiKpis } from "../../services/api.js";
import Card from "../ui/Card.jsx";
import Badge from "../ui/Badge.jsx";

export default function PowerBIView() {
  const [catalog, setCatalog] = useState(null);
  const [kpis, setKpis] = useState(null);
  const [comparisons, setComparisons] = useState(null);

  useEffect(() => {
    Promise.all([getPowerBiCatalog(), getPowerBiKpis(), getPowerBiComparisons()]).then(([c, k, comp]) => {
      setCatalog(c); setKpis(k); setComparisons(comp);
    }).catch(() => {});
  }, []);

  const endpoints = [
    "/powerbi/catalog",
    "/powerbi/dataset/{dataset_id}",
    "/powerbi/normalized-results",
    "/powerbi/kpis",
    "/powerbi/comparisons"
  ];

  return (
    <div className="space-y-5">
      <div><p className="text-sm font-bold uppercase tracking-[0.25em] text-indigo-500">Power BI</p><h2 className="mt-2 text-3xl font-black">Modelo analítico exportable</h2></div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card><Database className="text-indigo-500" /><p className="mt-3 text-2xl font-black">{catalog?.datasets?.length || 0}</p><p className="text-sm text-slate-500">Datasets en catálogo</p></Card>
        <Card><PieChart className="text-emerald-500" /><p className="mt-3 text-2xl font-black">{kpis?.records?.toLocaleString?.() || 0}</p><p className="text-sm text-slate-500">Registros normalizados</p></Card>
        <Card><FileSpreadsheet className="text-amber-500" /><p className="mt-3 text-2xl font-black">6</p><p className="text-sm text-slate-500">CSV de exportación</p></Card>
        <Card><Link2 className="text-rose-500" /><p className="mt-3 text-2xl font-black">{endpoints.length}</p><p className="text-sm text-slate-500">Endpoints JSON</p></Card>
      </div>
      <Card hover={false}>
        <h3 className="font-black">Endpoints para conectar desde Power BI</h3>
        <div className="mt-4 grid gap-2">
          {endpoints.map((endpoint) => <code key={endpoint} className="rounded-2xl bg-slate-950 px-4 py-3 text-sm text-emerald-200">http://localhost:8000{endpoint}</code>)}
        </div>
      </Card>
      <Card hover={false}>
        <h3 className="font-black">Dashboard recomendado</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          {["Resultados generales", "Comparativo país", "Tendencias", "Brechas por género", "Institución", "Nivel socioeconómico", "Áreas evaluadas"].map((item) => <Badge key={item} tone="slate">{item}</Badge>)}
        </div>
        {comparisons?.country?.insight && <p className="mt-4 text-sm leading-7 text-slate-500">{comparisons.country.insight}</p>}
      </Card>
    </div>
  );
}
