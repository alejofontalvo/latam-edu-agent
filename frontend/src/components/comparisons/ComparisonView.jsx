import { useEffect, useState } from "react";
import { compareAnalytics } from "../../services/api.js";
import ChartCard from "../analytics/ChartCard.jsx";
import Card from "../ui/Card.jsx";
import Button from "../ui/Button.jsx";

export default function ComparisonView() {
  const [dimension, setDimension] = useState("country");
  const [metric, setMetric] = useState("global_score");
  const [chart, setChart] = useState(null);

  const run = async () => {
    const result = await compareAnalytics({ metric, dimension, filters: {}, dataset_ids: [] });
    setChart(result);
  };

  useEffect(() => { run().catch(() => {}); }, []);

  return (
    <div className="space-y-5">
      <div><p className="text-sm font-bold uppercase tracking-[0.25em] text-indigo-500">Comparativos</p><h2 className="mt-2 text-3xl font-black">Cruces entre países, pruebas y grupos</h2></div>
      <Card hover={false}>
        <div className="grid gap-3 md:grid-cols-3">
          <select className="select-premium" value={dimension} onChange={(e) => setDimension(e.target.value)}>
            <option value="country">País vs país</option>
            <option value="exam">Prueba vs prueba</option>
            <option value="year">Año vs año</option>
            <option value="gender">Género</option>
            <option value="institution_type">Públicas vs privadas</option>
            <option value="socioeconomic_level">Nivel socioeconómico</option>
          </select>
          <select className="select-premium" value={metric} onChange={(e) => setMetric(e.target.value)}>
            <option value="global_score">Puntaje global</option>
            <option value="math_score">Matemáticas</option>
            <option value="reading_score">Lectura</option>
            <option value="science_score">Ciencias</option>
          </select>
          <Button onClick={run}>Comparar</Button>
        </div>
      </Card>
      {chart && <ChartCard title={chart.title} data={chart.data} xKey={chart.x_key} yKey={chart.y_key} insight={chart.insight} />}
    </div>
  );
}
