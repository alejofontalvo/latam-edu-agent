import DatasetCard from "./DatasetCard.jsx";
import EmptyState from "../ui/EmptyState.jsx";

export default function DatasetCatalog({ datasets, onAnalyze, onSummary, onExport, onUseChat }) {
  if (!datasets.length) {
    return <EmptyState title="Sin datasets visibles" text="Ejecuta el seed demo o la ingesta interna para alimentar el catálogo." />;
  }
  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-bold uppercase tracking-[0.25em] text-indigo-500">Banco de pruebas</p>
        <h2 className="mt-2 text-3xl font-black tracking-tight">Fuentes disponibles</h2>
        <p className="mt-2 max-w-3xl text-slate-500 dark:text-slate-400">
          El usuario final no carga archivos. Aquí consulta datasets internos procesados por el administrador.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {datasets.map((dataset) => (
          <DatasetCard
            key={dataset.registry_id}
            dataset={dataset}
            onAnalyze={onAnalyze}
            onSummary={onSummary}
            onExport={onExport}
            onUseChat={onUseChat}
          />
        ))}
      </div>
    </div>
  );
}
