import { Moon, Search, Sun, UserRound } from "lucide-react";
import Badge from "../ui/Badge.jsx";
import Button from "../ui/Button.jsx";

export default function Header({ health, datasets, selectedDatasetId, onDatasetChange, filters, onFiltersChange, darkMode, onToggleTheme }) {
  const countries = [...new Set(datasets.map((item) => item.country))];
  const exams = [...new Set(datasets.map((item) => item.exam))];
  const years = [...new Set(datasets.map((item) => item.year).filter(Boolean))].sort((a, b) => b - a);

  return (
    <header className="sticky top-0 z-30 border-b border-white/60 bg-slate-50/80 px-4 py-4 backdrop-blur-xl dark:border-white/10 dark:bg-slate-950/80 lg:ml-72">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone={health?.status === "ok" ? "emerald" : "rose"}>API {health?.status || "verificando"}</Badge>
            <Badge tone="indigo">IA conectada</Badge>
            <Badge tone="emerald">RAG activo</Badge>
            <Badge tone="slate">Datos actualizados</Badge>
          </div>
          <div className="mt-2 flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            <Search size={16} />
            El chat analiza automáticamente el catálogo completo; los filtros son opcionales.
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <select className="select-premium" value={filters.country} onChange={(e) => onFiltersChange({ ...filters, country: e.target.value })}>
            <option value="">País</option>
            {countries.map((item) => <option key={item}>{item}</option>)}
          </select>
          <select className="select-premium" value={filters.exam} onChange={(e) => onFiltersChange({ ...filters, exam: e.target.value })}>
            <option value="">Prueba</option>
            {exams.map((item) => <option key={item}>{item}</option>)}
          </select>
          <select className="select-premium" value={filters.year} onChange={(e) => onFiltersChange({ ...filters, year: e.target.value })}>
            <option value="">Año</option>
            {years.map((item) => <option key={item}>{item}</option>)}
          </select>
          <select className="select-premium min-w-64" value={selectedDatasetId} onChange={(e) => onDatasetChange(e.target.value)}>
            <option value="">Catálogo completo</option>
            {datasets.map((dataset) => <option key={dataset.registry_id} value={dataset.registry_id}>{dataset.name}</option>)}
          </select>
          <Button variant="secondary" onClick={onToggleTheme} title="Cambiar tema">
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          </Button>
          <div className="flex items-center gap-2 rounded-2xl bg-white/80 px-3 py-2 text-sm font-bold shadow-sm ring-1 ring-slate-200 dark:bg-white/10 dark:ring-white/10">
            <UserRound size={18} />
            Investigador
          </div>
        </div>
      </div>
    </header>
  );
}
