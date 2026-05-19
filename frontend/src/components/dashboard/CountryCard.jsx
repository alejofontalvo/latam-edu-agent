import { MapPin } from "lucide-react";
import Badge from "../ui/Badge.jsx";
import Card from "../ui/Card.jsx";
import Button from "../ui/Button.jsx";

const FLAGS = {
  Colombia: "🇨🇴",
  Brasil: "🇧🇷",
  México: "🇲🇽",
  Chile: "🇨🇱",
  Perú: "🇵🇪",
  Argentina: "🇦🇷",
  Uruguay: "🇺🇾",
  Ecuador: "🇪🇨",
  Latinoamérica: "🌎"
};

export default function CountryCard({ country, onExplore }) {
  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <div className="text-4xl">{FLAGS[country.country] || "🌐"}</div>
          <h3 className="mt-3 text-lg font-black">{country.country}</h3>
          <p className="mt-1 flex items-center gap-1 text-sm text-slate-500 dark:text-slate-400">
            <MapPin size={15} /> {country.datasets} datasets · {country.records.toLocaleString()} registros
          </p>
        </div>
        <Badge tone="emerald">{country.status}</Badge>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {country.exams.slice(0, 4).map((exam) => <Badge key={exam} tone="slate">{exam}</Badge>)}
      </div>
      <Button className="mt-5 w-full" variant="secondary" onClick={() => onExplore(country.country)}>Explorar país</Button>
    </Card>
  );
}
