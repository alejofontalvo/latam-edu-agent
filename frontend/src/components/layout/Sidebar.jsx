import { BarChart3, Bot, FileQuestion, FileText, Gauge, Globe2, Home, Layers3, LineChart, Network, Settings, Zap } from "lucide-react";

const items = [
  { id: "home", label: "Inicio", icon: Home },
  { id: "chat", label: "Chat IA", icon: Bot },
  { id: "observatory", label: "Observatorio LATAM", icon: Globe2 },
  { id: "analytics", label: "Análisis", icon: BarChart3 },
  { id: "comparisons", label: "Comparativos", icon: Network },
  { id: "reports", label: "Reportes", icon: FileText },
  { id: "evaluations", label: "Evaluaciones", icon: FileQuestion },
  { id: "rag", label: "Documentos RAG", icon: Layers3 },
  { id: "powerbi", label: "Power BI", icon: LineChart },
  { id: "settings", label: "Configuración", icon: Settings }
];

export default function Sidebar({ activeView, onChange }) {
  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-72 border-r border-white/60 bg-white/75 p-4 shadow-2xl shadow-slate-200/70 backdrop-blur-xl dark:border-white/10 dark:bg-slate-950/75 dark:shadow-black/30 lg:block">
      <div className="flex items-center gap-3 rounded-3xl bg-gradient-to-br from-indigo-600 to-emerald-500 p-4 text-white shadow-xl shadow-indigo-500/20">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/20">
          <Zap size={24} />
        </div>
        <div>
          <p className="text-lg font-black">LATAM EduAgent</p>
          <p className="text-xs text-white/80">AI Education Observatory</p>
        </div>
      </div>
      <nav className="mt-6 space-y-1">
        {items.map((item) => {
          const Icon = item.icon;
          const active = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onChange(item.id)}
              className={`group flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left text-sm font-bold transition ${
                active
                  ? "bg-slate-950 text-white shadow-lg shadow-slate-900/20 dark:bg-white dark:text-slate-950"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-white/10 dark:hover:text-white"
              }`}
            >
              <Icon size={18} className={active ? "text-emerald-300 dark:text-indigo-600" : "text-slate-400 group-hover:text-indigo-500"} />
              {item.label}
            </button>
          );
        })}
      </nav>
      <div className="absolute bottom-4 left-4 right-4 rounded-3xl border border-indigo-200 bg-indigo-50 p-4 text-sm text-indigo-900 dark:border-indigo-400/20 dark:bg-indigo-500/10 dark:text-indigo-100">
        <div className="mb-2 flex items-center gap-2 font-black">
          <Gauge size={16} />
          Modo demo activo
        </div>
        <p className="text-xs leading-5 opacity-80">Los datos simulados están marcados como demo hasta conectar fuentes oficiales.</p>
      </div>
    </aside>
  );
}
