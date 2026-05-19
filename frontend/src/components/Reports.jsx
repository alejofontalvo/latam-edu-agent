import { useState } from "react";
import { Download, FileJson, WandSparkles } from "lucide-react";
import { exportCsv, exportExcel, generateEvaluation, getPowerBiDataset } from "../services/api.js";

export default function Reports({ mode, datasetId, selectedDataset }) {
  const [status, setStatus] = useState("");
  const [jsonPreview, setJsonPreview] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [form, setForm] = useState({
    area: "lectura critica",
    country: "Colombia",
    exam_reference: "Saber 11",
    difficulty: "media",
    number_of_questions: 5,
    topic: "comprension lectora"
  });

  const handleExport = async (kind) => {
    if (!datasetId) return setStatus("Selecciona un dataset.");
    const action = kind === "csv" ? exportCsv : exportExcel;
    const response = await action(datasetId);
    setStatus(`Archivo generado: ${response.path}`);
  };

  const loadJson = async () => {
    if (!datasetId) return setStatus("Selecciona un dataset.");
    const response = await getPowerBiDataset(datasetId);
    setJsonPreview(response);
  };

  const createEvaluation = async (event) => {
    event.preventDefault();
    const response = await generateEvaluation({
      ...form,
      number_of_questions: Number(form.number_of_questions)
    });
    setEvaluation(response);
  };

  if (mode === "evaluations") {
    return (
      <div className="space-y-5">
        <div>
          <h2 className="text-lg font-semibold">Generador de evaluaciones</h2>
          <p className="text-sm text-slate-600">Crea ítems originales tipo prueba estatal con respuesta y explicación.</p>
        </div>
        <form onSubmit={createEvaluation} className="grid gap-3 border border-slate-200 p-4 md:grid-cols-3">
          {["area", "country", "exam_reference", "difficulty", "topic"].map((field) => (
            <input
              key={field}
              className="input"
              value={form[field]}
              onChange={(event) => setForm({ ...form, [field]: event.target.value })}
              placeholder={field}
            />
          ))}
          <input
            className="input"
            type="number"
            min="1"
            max="20"
            value={form.number_of_questions}
            onChange={(event) => setForm({ ...form, number_of_questions: event.target.value })}
          />
          <button className="button bg-coral text-white md:col-span-3">
            <WandSparkles size={18} /> Generar evaluación
          </button>
        </form>
        {evaluation && (
          <div className="space-y-3">
            <h3 className="font-semibold">{evaluation.title}</h3>
            {evaluation.questions.map((question) => (
              <article key={question.number} className="border border-slate-200 p-4">
                <p className="font-medium">{question.question}</p>
                <ul className="mt-3 grid gap-2 text-sm">
                  {Object.entries(question.options).map(([key, value]) => (
                    <li key={key}>{key}. {value}</li>
                  ))}
                </ul>
                <p className="mt-3 text-sm text-emerald-700">Respuesta: {question.correct_answer}</p>
                <p className="text-sm text-slate-600">{question.explanation}</p>
              </article>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold">Reportes y Power BI</h2>
        <p className="text-sm text-slate-600">Dataset activo: {selectedDataset?.name || "ninguno"}</p>
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        <button className="button border border-slate-300" onClick={() => handleExport("csv")}>
          <Download size={18} /> Exportar CSV
        </button>
        <button className="button border border-slate-300" onClick={() => handleExport("excel")}>
          <Download size={18} /> Exportar Excel
        </button>
        <button className="button border border-slate-300" onClick={loadJson}>
          <FileJson size={18} /> Endpoint JSON
        </button>
      </div>
      {status && <p className="text-sm text-slate-700">{status}</p>}
      {jsonPreview && (
        <pre className="max-h-96 overflow-auto bg-slate-950 p-4 text-xs text-slate-100">
          {JSON.stringify({ ...jsonPreview, records: jsonPreview.records?.slice(0, 3) }, null, 2)}
        </pre>
      )}
    </div>
  );
}
