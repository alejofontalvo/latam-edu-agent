import { useState } from "react";
import { Send, UploadCloud } from "lucide-react";
import { sendChat, uploadDocuments } from "../services/api.js";

export default function Chat({ datasetId, selectedDataset }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hola. Carga un dataset o documentos técnicos y pregúntame por resultados, brechas, metodología o evaluaciones."
    }
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [docStatus, setDocStatus] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    if (!input.trim()) return;
    const userMessage = input.trim();
    setMessages((current) => [...current, { role: "user", content: userMessage }]);
    setInput("");
    setBusy(true);
    try {
      const response = await sendChat({
        message: userMessage,
        dataset_id: datasetId ? Number(datasetId) : null,
        use_rag: true
      });
      setMessages((current) => [
        ...current,
        { role: "assistant", content: response.answer, sources: response.sources || [] }
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        { role: "assistant", content: error?.response?.data?.detail || "No pude procesar la consulta." }
      ]);
    } finally {
      setBusy(false);
    }
  };

  const handleDocumentUpload = async (event) => {
    const files = Array.from(event.target.files || []);
    if (!files.length) return;
    setDocStatus("Indexando documentos...");
    try {
      const response = await uploadDocuments(files);
      setDocStatus(`${response.total_chunks} fragmentos indexados.`);
    } catch (error) {
      setDocStatus(error?.response?.data?.detail || "No fue posible indexar los documentos.");
    }
  };

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_260px]">
      <div className="flex min-h-[640px] flex-col border border-slate-200">
        <div className="border-b border-slate-200 px-4 py-3">
          <h2 className="text-lg font-semibold">Chat analítico</h2>
          <p className="text-sm text-slate-600">
            Dataset activo: {selectedDataset ? selectedDataset.name : "ninguno"}
          </p>
        </div>
        <div className="flex-1 space-y-3 overflow-y-auto bg-panel p-4">
          {messages.map((message, index) => (
            <article
              key={`${message.role}-${index}`}
              className={`message ${message.role === "user" ? "message-user" : "message-assistant"}`}
            >
              <p className="whitespace-pre-wrap text-sm leading-6">{message.content}</p>
              {message.sources?.length > 0 && (
                <div className="mt-3 border-t border-slate-200 pt-2 text-xs text-slate-600">
                  {message.sources.map((source, sourceIndex) => (
                    <p key={`${source.source}-${sourceIndex}`}>
                      Fuente: {source.source} · fragmento {source.chunk}
                    </p>
                  ))}
                </div>
              )}
            </article>
          ))}
        </div>
        <form onSubmit={submit} className="flex gap-2 border-t border-slate-200 p-3">
          <input
            className="input flex-1"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ej: compara el promedio por país y explica posibles brechas"
          />
          <button className="icon-button bg-accent text-white" disabled={busy} title="Enviar consulta">
            <Send size={18} />
          </button>
        </form>
      </div>

      <aside className="space-y-4">
        <div className="border border-slate-200 p-4">
          <h3 className="font-semibold">Documentos RAG</h3>
          <p className="mt-1 text-sm text-slate-600">PDF, TXT, Markdown o DOCX.</p>
          <label className="mt-3 flex cursor-pointer items-center justify-center gap-2 border border-dashed border-slate-300 px-3 py-6 text-sm hover:border-accent">
            <UploadCloud size={18} />
            Subir documentos
            <input className="hidden" type="file" multiple onChange={handleDocumentUpload} />
          </label>
          {docStatus && <p className="mt-2 text-sm text-slate-700">{docStatus}</p>}
        </div>
        <div className="border border-slate-200 p-4 text-sm text-slate-700">
          <h3 className="font-semibold text-ink">Consultas útiles</h3>
          <button className="sample" onClick={() => setInput("¿Qué variables explican brechas educativas?")}>
            Variables de brecha
          </button>
          <button className="sample" onClick={() => setInput("Resume la metodología del documento cargado.")}>
            Metodología RAG
          </button>
          <button className="sample" onClick={() => setInput("Analiza resultados por género o tipo de colegio.")}>
            Análisis por grupo
          </button>
        </div>
      </aside>
    </div>
  );
}
