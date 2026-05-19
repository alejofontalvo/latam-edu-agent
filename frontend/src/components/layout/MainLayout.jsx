import { AnimatePresence, motion } from "framer-motion";
import Header from "./Header.jsx";
import Sidebar from "./Sidebar.jsx";

export default function MainLayout({ children, activeView, setActiveView, health, datasets, selectedDatasetId, setSelectedDatasetId, filters, setFilters, darkMode, setDarkMode }) {
  return (
    <div className={darkMode ? "dark" : ""}>
      <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,#dbeafe,transparent_35%),linear-gradient(135deg,#f8fafc,#eef2ff_45%,#ecfeff)] text-slate-950 dark:bg-[radial-gradient(circle_at_top_left,#312e81,transparent_30%),linear-gradient(135deg,#020617,#0f172a_45%,#111827)] dark:text-white">
        <Sidebar activeView={activeView} onChange={setActiveView} />
        <Header
          health={health}
          datasets={datasets}
          selectedDatasetId={selectedDatasetId}
          onDatasetChange={setSelectedDatasetId}
          filters={filters}
          onFiltersChange={setFilters}
          darkMode={darkMode}
          onToggleTheme={() => setDarkMode((value) => !value)}
        />
        <main className="px-4 py-6 lg:ml-72 lg:px-8">
          <AnimatePresence mode="wait">
            <motion.div key={activeView} initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.25 }}>
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
