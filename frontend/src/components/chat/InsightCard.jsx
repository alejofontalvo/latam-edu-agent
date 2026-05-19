import { Lightbulb } from "lucide-react";

export default function InsightCard({ blocks, insights = [], recommendations = [], limitations = [] }) {
  const normalizedBlocks = blocks || {
    insights,
    recommendations,
    limitations
  };
  const entries = [
    ["insights", "Insights"],
    ["recommendations", "Recomendaciones"],
    ["limitations", "Limitaciones"]
  ].filter(([key]) => {
    const value = normalizedBlocks[key];
    return Array.isArray(value) ? value.length : Boolean(value);
  });
  if (!entries.length) return null;
  return (
    <div className="mt-4 grid gap-3 md:grid-cols-2">
      {entries.map(([key, label]) => (
        <div key={key} className="rounded-2xl bg-slate-100 p-3 text-sm dark:bg-white/5">
          <div className="mb-1 flex items-center gap-2 font-black"><Lightbulb size={15} /> {label}</div>
          <p className="leading-6 text-slate-600 dark:text-slate-300">{Array.isArray(normalizedBlocks[key]) ? normalizedBlocks[key].join(" ") : normalizedBlocks[key]}</p>
        </div>
      ))}
    </div>
  );
}
