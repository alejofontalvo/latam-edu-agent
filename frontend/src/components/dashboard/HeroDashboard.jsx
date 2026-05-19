import { BarChart3, Bot, Database, FileQuestion, FileText, Globe2, Layers3, LineChart } from "lucide-react";
import Card from "../ui/Card.jsx";
import KpiCard from "./KpiCard.jsx";
import QuickActionCard from "./QuickActionCard.jsx";

export default function HeroDashboard({ kpis, datasets, onNavigate }) {
  return (
    <div className="space-y-6">
      <section className="relative overflow-hidden rounded-[2rem] border border-white/60 bg-slate-950 p-8 text-white shadow-2xl shadow-indigo-500/20 dark:border-white/10">
        <div className="absolute right-0 top-0 h-72 w-72 rounded-full bg-indigo-500/30 blur-3xl" />
        <div className="absolute bottom-0 right-44 h-56 w-56 rounded-full bg-emerald-400/20 blur-3xl" />
        <div className="relative max-w-4xl">
          <p className="mb-3 inline-flex rounded-full bg-white/10 px-4 py-2 text-sm font-bold text-emerald-200 ring-1 ring-white/10">
            Observatorio educativo con IA · Datos internos prealimentados
          </p>
          <h1 className="text-4xl font-black tracking-tight md:text-6xl">LATAM EduAgent</h1>
          <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-300">
            Analiza, compara y comprende las pruebas estatales de Latinoamérica con inteligencia artificial, RAG y reportes listos para Power BI.
          </p>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <KpiCard icon={Globe2} label="Países integrados" value={kpis?.countries ?? 0} detail="Catálogo interno" tone="sky" />
        <KpiCard icon={Database} label="Datasets" value={kpis?.datasets ?? 0} detail="Disponibles para análisis" tone="indigo" />
        <KpiCard icon={BarChart3} label="Registros" value={(kpis?.records ?? 0).toLocaleString()} detail="Procesados" tone="emerald" />
        <KpiCard icon={Layers3} label="Docs RAG" value={kpis?.documents ?? 0} detail="Indexados" tone="amber" />
        <KpiCard icon={FileQuestion} label="Evaluaciones" value={kpis?.evaluations ?? 0} detail="Generadas" tone="rose" />
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <QuickActionCard icon={Bot} title="Chat inteligente" text="Pregunta sobre resultados, brechas, metodología o reportes." onClick={() => onNavigate("chat")} />
        <QuickActionCard icon={BarChart3} title="Análisis comparativo" text="Filtra por país, prueba, año, área y variables de contexto." onClick={() => onNavigate("analytics")} />
        <QuickActionCard icon={Database} title="Banco de pruebas" text={`${datasets.length} fuentes internas listas para consultar.`} onClick={() => onNavigate("observatory")} />
        <QuickActionCard icon={FileText} title="Reportes Power BI" text="Exporta CSV, Excel y endpoints JSON normalizados." onClick={() => onNavigate("reports")} />
        <QuickActionCard icon={FileQuestion} title="Generador de evaluaciones" text="Crea preguntas tipo prueba estatal con explicación." onClick={() => onNavigate("evaluations")} />
        <QuickActionCard icon={LineChart} title="Documentos metodológicos" text="Consulta diccionarios, manuales e informes indexados." onClick={() => onNavigate("rag")} />
      </div>

      {kpis?.demo_mode && (
        <Card className="border-amber-200 bg-amber-50/80 text-amber-950 dark:border-amber-400/20 dark:bg-amber-500/10 dark:text-amber-100">
          <strong>Datos demo:</strong> la plataforma está poblada con datos simulados realistas para presentación. Sustitúyelos por fuentes oficiales mediante los scripts de ingesta.
        </Card>
      )}
    </div>
  );
}
