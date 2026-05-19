import { Bot, UserRound } from "lucide-react";
import Button from "../ui/Button.jsx";
import InsightCard from "./InsightCard.jsx";
import ChartCard from "../analytics/ChartCard.jsx";

function DataTable({ table }) {
  if (!table?.rows?.length) return null;
  return (
    <div className="mt-4 overflow-hidden rounded-2xl border border-slate-200 dark:border-white/10">
      <div className="bg-slate-100 px-4 py-3 text-sm font-black dark:bg-white/5">{table.title || "Tabla"}</div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-xs">
          <thead className="bg-white/70 text-slate-500 dark:bg-slate-950/40 dark:text-slate-400">
            <tr>{table.columns.map((column) => <th key={column} className="px-4 py-3 font-black">{column}</th>)}</tr>
          </thead>
          <tbody>
            {table.rows.slice(0, 8).map((row, index) => (
              <tr key={index} className="border-t border-slate-100 dark:border-white/5">
                {row.map((value, cellIndex) => <td key={cellIndex} className="px-4 py-3">{String(value ?? "N/D")}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";
  const charts = message.charts || (message.chart ? [message.chart] : []);
  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-600 to-emerald-500 text-white"><Bot size={18} /></div>}
      <article className={`max-w-5xl rounded-3xl p-4 shadow-lg ${isUser ? "bg-indigo-600 text-white" : "bg-white/90 text-slate-950 dark:bg-slate-900/90 dark:text-white"}`}>
        <p className="whitespace-pre-wrap text-sm leading-7">{message.content}</p>
        {!isUser && <InsightCard blocks={message.blocks} insights={message.insights} recommendations={message.recommendations} limitations={message.limitations} />}
        {!isUser && charts?.map((chart, index) => chart?.data?.length > 0 && (
          <div key={`${chart.title}-${index}`} className="mt-4">
            <ChartCard title={chart.title} data={chart.data} xKey={chart.x_key} yKey={chart.y_key} type={chart.type || chart.chart_type} insight={chart.description || chart.insight} />
          </div>
        ))}
        {!isUser && message.tables?.map((table, index) => <DataTable key={`${table.title}-${index}`} table={table} />)}
        {!isUser && message.actions?.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {message.actions.map((action) => <Button key={action} variant="secondary" className="min-h-8 px-3 text-xs">{action}</Button>)}
          </div>
        )}
        {!isUser && message.sources?.length > 0 && (
          <div className="mt-3 border-t border-slate-200 pt-2 text-xs text-slate-500 dark:border-white/10 dark:text-slate-400">
            {message.sources.map((source, index) => <p key={index}>Fuente: {source.title || source.source || "Documento"} {source.chunk ? `· fragmento ${source.chunk}` : ""}</p>)}
          </div>
        )}
      </article>
      {isUser && <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-slate-950 text-white dark:bg-white dark:text-slate-950"><UserRound size={18} /></div>}
    </div>
  );
}
