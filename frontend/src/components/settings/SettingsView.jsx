import { ShieldCheck, Terminal } from "lucide-react";
import Card from "../ui/Card.jsx";
import Badge from "../ui/Badge.jsx";

export default function SettingsView() {
  return (
    <div className="space-y-5">
      <div><p className="text-sm font-bold uppercase tracking-[0.25em] text-indigo-500">Configuración</p><h2 className="mt-2 text-3xl font-black">Administración interna</h2></div>
      <Card>
        <ShieldCheck className="text-emerald-500" />
        <h3 className="mt-3 font-black">Carga pública deshabilitada</h3>
        <p className="mt-2 text-sm leading-7 text-slate-500 dark:text-slate-400">Los usuarios finales consultan datasets previamente cargados. La ingesta se realiza por scripts o endpoints admin protegidos con ADMIN_API_KEY.</p>
        <div className="mt-4 flex flex-wrap gap-2"><Badge>ADMIN_API_KEY</Badge><Badge tone="emerald">datasets internos</Badge><Badge tone="amber">Docker opcional</Badge></div>
      </Card>
      <Card hover={false}>
        <div className="flex items-center gap-2 font-black"><Terminal size={18} /> Comandos administrativos</div>
        <pre className="mt-4 overflow-auto rounded-2xl bg-slate-950 p-4 text-sm leading-7 text-slate-100">{`cd backend
source venv/bin/activate
python scripts/seed_demo_data.py
python scripts/rebuild_database.py
python scripts/ingest_all_datasets.py
python scripts/index_documents.py
python scripts/export_powerbi_files.py`}</pre>
      </Card>
    </div>
  );
}
