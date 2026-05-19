import { useEffect, useMemo, useState } from "react";
import AnalyticsDashboard from "./components/analytics/AnalyticsDashboard.jsx";
import ChatPanel from "./components/chat/ChatPanel.jsx";
import ComparisonView from "./components/comparisons/ComparisonView.jsx";
import CountryCard from "./components/dashboard/CountryCard.jsx";
import HeroDashboard from "./components/dashboard/HeroDashboard.jsx";
import DatasetCatalog from "./components/datasets/DatasetCatalog.jsx";
import EvaluationGenerator from "./components/evaluations/EvaluationGenerator.jsx";
import MainLayout from "./components/layout/MainLayout.jsx";
import PowerBIView from "./components/powerbi/PowerBIView.jsx";
import DocumentsView from "./components/rag/DocumentsView.jsx";
import ReportsView from "./components/reports/ReportsView.jsx";
import SettingsView from "./components/settings/SettingsView.jsx";
import Toast from "./components/ui/Toast.jsx";
import { exportExcel, getCountries, getDatasets, getHealth, getKpis } from "./services/api.js";

export default function App() {
  const [activeView, setActiveView] = useState("home");
  const [health, setHealth] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [countries, setCountries] = useState([]);
  const [kpis, setKpis] = useState(null);
  const [selectedDatasetId, setSelectedDatasetId] = useState("");
  const [filters, setFilters] = useState({ country: "", exam: "", year: "" });
  const [darkMode, setDarkMode] = useState(false);
  const [toast, setToast] = useState("");

  const notify = (message) => {
    setToast(message);
    setTimeout(() => setToast(""), 3200);
  };

  const load = async () => {
    const [apiHealth, datasetList, countryList, globalKpis] = await Promise.all([
      getHealth().catch(() => ({ status: "offline" })),
      getDatasets().catch(() => []),
      getCountries().catch(() => []),
      getKpis().catch(() => null)
    ]);
    setHealth(apiHealth);
    setDatasets(datasetList);
    setCountries(countryList);
    setKpis(globalKpis);
  };

  useEffect(() => { load(); }, []);

  const filteredDatasets = useMemo(() => datasets.filter((dataset) => {
    if (filters.country && dataset.country !== filters.country) return false;
    if (filters.exam && dataset.exam !== filters.exam) return false;
    if (filters.year && String(dataset.year) !== String(filters.year)) return false;
    return true;
  }), [datasets, filters]);

  const selectedDataset = datasets.find((dataset) => dataset.registry_id === selectedDatasetId);

  const handleAnalyze = (dataset) => {
    setSelectedDatasetId(dataset.registry_id);
    setActiveView("analytics");
  };
  const handleSummary = (dataset) => {
    setSelectedDatasetId(dataset.registry_id);
    notify(`Resumen listo para ${dataset.name}. Abre Análisis para verlo.`);
  };
  const handleExport = async (dataset) => {
    const response = await exportExcel(dataset.registry_id);
    notify(`Exportado: ${response.path}`);
  };
  const handleUseChat = (dataset) => {
    setSelectedDatasetId(dataset.registry_id);
    setActiveView("chat");
  };

  const views = {
    home: <HeroDashboard kpis={kpis} datasets={datasets} onNavigate={setActiveView} />,
    chat: <ChatPanel selectedDatasetId={selectedDatasetId} datasets={datasets} />,
    observatory: (
      <div className="space-y-5">
        <div><p className="text-sm font-bold uppercase tracking-[0.25em] text-indigo-500">Observatorio LATAM</p><h2 className="mt-2 text-3xl font-black">Países y pruebas disponibles</h2></div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{countries.map((country) => <CountryCard key={country.country} country={country} onExplore={(name) => setFilters({ ...filters, country: name })} />)}</div>
        <DatasetCatalog datasets={filteredDatasets} onAnalyze={handleAnalyze} onSummary={handleSummary} onExport={handleExport} onUseChat={handleUseChat} />
      </div>
    ),
    analytics: <AnalyticsDashboard selectedDatasetId={selectedDatasetId} />,
    comparisons: <ComparisonView />,
    reports: <ReportsView selectedDatasetId={selectedDatasetId} selectedDataset={selectedDataset} notify={notify} />,
    evaluations: <EvaluationGenerator />,
    rag: <DocumentsView />,
    powerbi: <PowerBIView />,
    settings: <SettingsView />
  };

  return (
    <MainLayout
      activeView={activeView}
      setActiveView={setActiveView}
      health={health}
      datasets={datasets}
      selectedDatasetId={selectedDatasetId}
      setSelectedDatasetId={setSelectedDatasetId}
      filters={filters}
      setFilters={setFilters}
      darkMode={darkMode}
      setDarkMode={setDarkMode}
    >
      {views[activeView] || views.home}
      <Toast message={toast} />
    </MainLayout>
  );
}
