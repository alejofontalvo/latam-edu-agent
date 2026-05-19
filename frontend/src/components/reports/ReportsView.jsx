import { useState } from "react";
import { Download, FileJson, FileText, Sparkles } from "lucide-react";
import { exportCsv, exportExcel, getPowerBiDataset } from "../../services/api.js";
import Button from "../ui/Button.jsx";
import Card from "../ui/Card.jsx";

export default function ReportsView({ selectedDatasetId, selectedDataset, notify }) {
  const [preview, setPreview] = useState(null);

  const runExport = async (kind) => {
    if (!selectedDatasetId) return notify("Selecciona un dataset activo.");
    const response = kind === "csv" ? await exportCsv(selectedDatasetId) : await exportExcel(selectedDatasetId);
    notify(`Archivo generado: ${response.path}`);
  };

  const loadJson = async () => {
    if (!selectedDatasetId) return notify("Selecciona un dataset activo.");
    setPreview(await getPowerBiDataset(selectedDatasetId));
  };

  return (
    <div className="space-y-5">
      <div><p className="text-sm font-bold uppercase tracking-[0.25em] text-indigo-500">Reportes</p><h2 className="mt-2 text-3xl font-black">Exportaciones y resumen ejecutivo</h2></div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card><FileText className="text-indigo-500" /><h3 className="mt-3 font-black">CSV limpio</h3><p className="mt-1 text-sm text-slate-500">Archivo normalizado para análisis externo.</p><Button className="mt-4 w-full" variant="secondary" onClick={() => runExport("csv")}><Download size={16} /> Exportar</Button></Card>
        <Card><FileText className="text-emerald-500" /><h3 className="mt-3 font-black">Excel + diccionario</h3><p className="mt-1 text-sm text-slate-500">Incluye datos y variables.</p><Button className="mt-4 w-full" variant="secondary" onClick={() => runExport("excel")}><Download size={16} /> Exportar</Button></Card>
        <Card><FileJson className="text-amber-500" /><h3 className="mt-3 font-black">Endpoint JSON</h3><p className="mt-1 text-sm text-slate-500">Compatible con Power BI Web.</p><Button className="mt-4 w-full" variant="secondary" onClick={loadJson}>Previsualizar</Button></Card>
        <Card><Sparkles className="text-rose-500" /><h3 className="mt-3 font-black">Reporte analítico</h3><p className="mt-1 text-sm text-slate-500">Resumen ejecutivo generado por IA.</p><Button className="mt-4 w-full" disabled>Próxima mejora</Button></Card>
      </div>
      <Card hover={false}>
        <h3 className="font-black">Dataset activo</h3>
        <p className="mt-2 text-slate-500 dark:text-slate-400">{selectedDataset?.name || "Selecciona un dataset para exportar."}</p>
        {preview && <pre className="mt-4 max-h-96 overflow-auto rounded-2xl bg-slate-950 p-4 text-xs text-slate-100">{JSON.stringify({ ...preview, records: preview.records?.slice(0, 3) }, null, 2)}</pre>}
      </Card>
    </div>
  );
}
