import Button from "../ui/Button.jsx";
import Card from "../ui/Card.jsx";

export default function FilterPanel({ filters, setFilters, datasetFilters, onRun }) {
  const options = (key) => datasetFilters?.[key] || [];
  return (
    <Card hover={false}>
      <h3 className="font-black">Filtros de análisis</h3>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {["country", "exam", "year", "region", "gender", "institution_type", "socioeconomic_level"].map((key) => (
          <select key={key} className="select-premium" value={filters[key] || ""} onChange={(e) => setFilters({ ...filters, [key]: e.target.value })}>
            <option value="">{key.replaceAll("_", " ")}</option>
            {options(key).map((value) => <option key={value}>{value}</option>)}
          </select>
        ))}
        <select className="select-premium" value={filters.metric || "global_score"} onChange={(e) => setFilters({ ...filters, metric: e.target.value })}>
          <option value="global_score">Puntaje global</option>
          <option value="math_score">Matemáticas</option>
          <option value="reading_score">Lectura</option>
          <option value="science_score">Ciencias</option>
          <option value="social_score">Sociales</option>
          <option value="english_score">Inglés</option>
        </select>
      </div>
      <Button className="mt-4" onClick={onRun}>Actualizar análisis</Button>
    </Card>
  );
}
