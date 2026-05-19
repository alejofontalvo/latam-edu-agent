import Card from "../ui/Card.jsx";

export default function KpiCard({ icon: Icon, label, value, detail, tone = "indigo" }) {
  const gradients = {
    indigo: "from-indigo-500 to-violet-500",
    emerald: "from-emerald-500 to-teal-500",
    sky: "from-sky-500 to-cyan-500",
    amber: "from-amber-500 to-orange-500",
    rose: "from-rose-500 to-fuchsia-500"
  };
  return (
    <Card className="overflow-hidden">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-bold text-slate-500 dark:text-slate-400">{label}</p>
          <p className="mt-2 text-3xl font-black tracking-tight">{value}</p>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{detail}</p>
        </div>
        <div className={`flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br ${gradients[tone]} text-white shadow-lg`}>
          <Icon size={22} />
        </div>
      </div>
    </Card>
  );
}
