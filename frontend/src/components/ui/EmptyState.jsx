import { Sparkles } from "lucide-react";

export default function EmptyState({ title = "Sin datos", text = "Ajusta los filtros o selecciona otro dataset." }) {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center rounded-3xl border border-dashed border-slate-300 bg-white/50 p-8 text-center dark:border-white/10 dark:bg-white/5">
      <Sparkles className="mb-3 text-indigo-500" size={28} />
      <h3 className="text-lg font-bold">{title}</h3>
      <p className="mt-1 max-w-md text-sm text-slate-500 dark:text-slate-400">{text}</p>
    </div>
  );
}
