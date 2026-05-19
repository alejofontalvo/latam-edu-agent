import { Sparkles } from "lucide-react";
import Card from "../ui/Card.jsx";

export default function InsightPanel({ insight }) {
  return (
    <Card className="bg-gradient-to-br from-indigo-600 to-slate-950 text-white">
      <div className="flex items-start gap-3">
        <div className="rounded-2xl bg-white/15 p-3"><Sparkles size={22} /></div>
        <div>
          <h3 className="text-lg font-black">Interpretación automática</h3>
          <p className="mt-2 leading-7 text-indigo-100">{insight || "Selecciona filtros para generar una interpretación basada en datos."}</p>
        </div>
      </div>
    </Card>
  );
}
