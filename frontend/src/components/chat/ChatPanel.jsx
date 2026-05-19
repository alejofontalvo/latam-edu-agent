import { useState } from "react";
import { Send, Sparkles } from "lucide-react";
import { sendChat } from "../../services/api.js";
import Button from "../ui/Button.jsx";
import Card from "../ui/Card.jsx";
import MessageBubble from "./MessageBubble.jsx";
import SuggestedPrompts from "./SuggestedPrompts.jsx";

export default function ChatPanel({ selectedDatasetId, datasets }) {
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Soy LATAM EduAgent. Puedo analizar datasets internos, comparar países, explicar brechas, consultar documentos RAG y crear evaluaciones.",
      blocks: {
        resumen: "El sistema ya viene alimentado por el administrador.",
        datos_usados: "Catálogo interno de pruebas latinoamericanas.",
        visualizacion_sugerida: "Comparativo por país, región o variable socioeconómica."
      },
      actions: ["Analizar dataset", "Comparar países", "Generar evaluación"]
    }
  ]);

  const submit = async (event) => {
    event?.preventDefault();
    if (!input.trim()) return;
    const userMessage = input.trim();
    setMessages((current) => [...current, { role: "user", content: userMessage }]);
    setInput("");
    setBusy(true);
    try {
      const response = await sendChat({ message: userMessage, dataset_id: selectedDatasetId || null, use_rag: true });
      setMessages((current) => [...current, { role: "assistant", content: response.answer, ...response }]);
    } catch (error) {
      setMessages((current) => [...current, { role: "assistant", content: error?.response?.data?.detail || "No pude procesar la consulta." }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid gap-5 xl:grid-cols-[1fr_320px]">
      <Card hover={false} className="flex min-h-[760px] flex-col p-0">
        <div className="border-b border-slate-200 p-5 dark:border-white/10">
          <h2 className="text-2xl font-black">Chat IA analítico</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Pregunta libremente: el agente inspecciona el catálogo completo y calcula estadísticas en backend.</p>
        </div>
        <div className="flex-1 space-y-5 overflow-y-auto bg-slate-100/70 p-5 dark:bg-slate-950/30">
          {messages.map((message, index) => <MessageBubble key={index} message={message} />)}
          {busy && <div className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-bold shadow dark:bg-white/10"><Sparkles className="animate-pulse text-indigo-500" size={16} /> LATAM EduAgent está pensando...</div>}
        </div>
        <form onSubmit={submit} className="border-t border-slate-200 p-4 dark:border-white/10">
          <SuggestedPrompts onSelect={setInput} datasets={datasets} />
          <div className="mt-3 flex gap-2">
            <input className="input-premium flex-1" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Pregunta por resultados, brechas, metodología o evaluaciones..." />
            <Button disabled={busy}><Send size={18} /> Enviar</Button>
          </div>
        </form>
      </Card>
      <aside className="space-y-4">
        <Card>
          <h3 className="font-black">Contextos disponibles</h3>
          <div className="mt-3 space-y-2">
            {datasets.slice(0, 7).map((dataset) => (
              <div key={dataset.registry_id} className="rounded-2xl bg-slate-100 p-3 text-sm dark:bg-white/5">
                <p className="font-black">{dataset.name}</p>
                <p className="text-xs text-slate-500">{dataset.row_count.toLocaleString()} registros · {dataset.is_demo ? "demo" : "oficial"}</p>
              </div>
            ))}
          </div>
        </Card>
      </aside>
    </div>
  );
}
