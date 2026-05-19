import { useState } from "react";
import { FileSpreadsheet, Upload } from "lucide-react";
import { uploadDataset } from "../services/api.js";

export default function DatasetUpload({ onUploaded, datasets }) {
  const [status, setStatus] = useState("");

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setStatus("Cargando y limpiando dataset...");
    try {
      const response = await uploadDataset(file);
      setStatus(`Dataset ${response.dataset_id} cargado con ${response.profile.rows} filas.`);
      await onUploaded();
    } catch (error) {
      setStatus(error?.response?.data?.detail || "No se pudo cargar el archivo.");
    }
  };

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold">Carga de datasets</h2>
        <p className="text-sm text-slate-600">
          Soporta CSV, XLSX, JSON y Parquet. El backend normaliza columnas, países, pruebas y valores faltantes.
        </p>
      </div>

      <label className="flex min-h-40 cursor-pointer flex-col items-center justify-center gap-3 border border-dashed border-slate-300 bg-panel p-6 hover:border-accent">
        <Upload size={28} />
        <span className="font-medium">Seleccionar dataset</span>
        <span className="text-sm text-slate-600">CSV, Excel, JSON o Parquet</span>
        <input type="file" className="hidden" onChange={handleUpload} />
      </label>
      {status && <p className="text-sm text-slate-700">{status}</p>}

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {datasets.map((dataset) => (
          <article key={dataset.id} className="border border-slate-200 p-4">
            <div className="flex items-start gap-3">
              <FileSpreadsheet className="text-accent" size={20} />
              <div>
                <h3 className="font-semibold">{dataset.name}</h3>
                <p className="text-sm text-slate-600">{dataset.original_filename}</p>
              </div>
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div>
                <dt className="text-slate-500">Filas</dt>
                <dd className="font-semibold">{dataset.row_count}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Columnas</dt>
                <dd className="font-semibold">{dataset.column_count}</dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
    </div>
  );
}
