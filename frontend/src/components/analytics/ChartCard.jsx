import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart, Radar, RadarChart, PolarAngleAxis, PolarGrid, PolarRadiusAxis, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import Card from "../ui/Card.jsx";

const COLORS = ["#4f46e5", "#0f766e", "#f97316", "#db2777", "#0891b2", "#7c3aed", "#65a30d"];

export default function ChartCard({ title, data = [], xKey, yKey, type = "bar", insight }) {
  return (
    <Card hover={false}>
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-black">{title}</h3>
          {insight && <p className="mt-1 text-sm leading-6 text-slate-500 dark:text-slate-400">{insight}</p>}
        </div>
      </div>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          {type === "line" ? (
            <LineChart data={data}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey={xKey} /><YAxis /><Tooltip /><Line type="monotone" dataKey={yKey} stroke="#4f46e5" strokeWidth={3} /></LineChart>
          ) : type === "pie" ? (
            <PieChart><Tooltip /><Pie data={data} dataKey={yKey} nameKey={xKey} outerRadius={115}>{data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}</Pie></PieChart>
          ) : type === "radar" ? (
            <RadarChart data={data}><PolarGrid /><PolarAngleAxis dataKey={xKey} /><PolarRadiusAxis /><Radar dataKey={yKey} fill="#4f46e5" fillOpacity={0.35} stroke="#4f46e5" /></RadarChart>
          ) : (
            <BarChart data={data}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey={xKey} tick={{ fontSize: 12 }} /><YAxis /><Tooltip /><Bar dataKey={yKey} radius={[10, 10, 0, 0]}>{data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}</Bar></BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
