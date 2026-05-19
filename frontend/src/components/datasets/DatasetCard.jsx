import { BarChart3, Download, MessageSquareText, Sparkles } from "lucide-react";
import Badge from "../ui/Badge.jsx";
import Button from "../ui/Button.jsx";
import Card from "../ui/Card.jsx";

export default function DatasetCard({ dataset, onAnalyze, onSummary, onExport, onUseChat }) {
  return (
    <Card className="flex h-full flex-col">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-black">{dataset.name}</h3>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{dataset.description}</p>
        </div>
        <Badge tone={dataset.status === "disponible" ? "emerald" : "amber"}>{dataset.status}</Badge>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <Info label="País" value={dataset.country} />
        <Info label="Prueba" value={dataset.exam} />
        <Info label="Año" value={dataset.year_range || dataset.year} />
        <Info label="Registros" value={dataset.row_count?.toLocaleString()} />
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {dataset.areas?.slice(0, 5).map((area) => <Badge key={area} tone="slate">{area}</Badge>)}
        {dataset.is_demo && <Badge tone="amber">demo</Badge>}
      </div>
      <div className="mt-auto grid grid-cols-2 gap-2 pt-5">
        <Button variant="primary" onClick={() => onAnalyze(dataset)}><BarChart3 size={16} /> Analizar</Button>
        <Button variant="secondary" onClick={() => onSummary(dataset)}><Sparkles size={16} /> Resumen</Button>
        <Button variant="secondary" onClick={() => onExport(dataset)}><Download size={16} /> Exportar</Button>
        <Button variant="secondary" onClick={() => onUseChat(dataset)}><MessageSquareText size={16} /> Chat</Button>
      </div>
    </Card>
  );
}

function Info({ label, value }) {
  return (
    <div className="rounded-2xl bg-slate-100/80 p-3 dark:bg-white/5">
      <p className="text-xs font-bold uppercase text-slate-400">{label}</p>
      <p className="mt-1 font-black">{value || "N/D"}</p>
    </div>
  );
}
