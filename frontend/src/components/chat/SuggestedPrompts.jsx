const unique = (items) => [...new Set(items.filter(Boolean))];

function buildPrompts(datasets = []) {
  const countries = unique(datasets.map((item) => item.country));
  const exams = unique(datasets.map((item) => item.exam));
  const hasSeveralCountries = countries.length > 1;
  const hasSeveralYears = unique(datasets.map((item) => item.year)).length > 1;
  const dataState = datasets.some((item) => !item.is_demo) ? "real" : "demo";

  if (!datasets.length) {
    return [
      "¿Qué datos hay disponibles en el sistema?",
      "Explícame cómo cargar datasets por detrás.",
      "Genera una demostración de análisis comparativo."
    ];
  }

  return [
    hasSeveralCountries
      ? `Compara matemáticas entre los países disponibles (${countries.slice(0, 3).join(", ")}).`
      : `Analiza los resultados disponibles de ${countries[0] || "la base cargada"}.`,
    "Muéstrame brechas por género con los datos disponibles.",
    hasSeveralYears ? "Dame las tendencias por año si hay datos comparables." : "Haz un ranking por promedio normalizado.",
    `Genera un resumen para Power BI con los datos ${dataState === "demo" ? "demo" : "reales"} disponibles.`,
    `Explica limitaciones metodológicas para comparar ${exams.slice(0, 3).join(", ") || "estas pruebas"}.`,
    "Crea una evaluación tipo prueba estatal con 5 preguntas."
  ];
}

export default function SuggestedPrompts({ onSelect, datasets }) {
  const prompts = buildPrompts(datasets);
  return (
    <div className="flex flex-wrap gap-2">
      {prompts.map((prompt) => (
        <button key={prompt} onClick={() => onSelect(prompt)} className="rounded-full bg-white/80 px-4 py-2 text-xs font-bold text-slate-700 shadow-sm ring-1 ring-slate-200 transition hover:bg-indigo-600 hover:text-white dark:bg-white/10 dark:text-slate-200 dark:ring-white/10">
          {prompt}
        </button>
      ))}
    </div>
  );
}
