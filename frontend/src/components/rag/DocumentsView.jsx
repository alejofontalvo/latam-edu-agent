import { useEffect, useState } from "react";
import { BookOpen, Search } from "lucide-react";
import { getDocuments, queryRag } from "../../services/api.js";
import Button from "../ui/Button.jsx";
import Card from "../ui/Card.jsx";
import Badge from "../ui/Badge.jsx";
import EmptyState from "../ui/EmptyState.jsx";

export default function DocumentsView() {
  const [documents, setDocuments] = useState([]);
  const [question, setQuestion] = useState("¿Cómo interpretar brechas educativas?");
  const [answer, setAnswer] = useState(null);

  useEffect(() => { getDocuments().then(setDocuments).catch(() => setDocuments([])); }, []);

  const ask = async () => setAnswer(await queryRag({ question, top_k: 5 }));

  return (
    <div className="space-y-5">
      <div><p className="text-sm font-bold uppercase tracking-[0.25em] text-indigo-500">Documentos RAG</p><h2 className="mt-2 text-3xl font-black">Biblioteca metodológica indexada</h2></div>
      <Card hover={false}>
        <div className="flex flex-col gap-3 md:flex-row">
          <input className="input-premium flex-1" value={question} onChange={(e) => setQuestion(e.target.value)} />
          <Button onClick={ask}><Search size={18} /> Consultar</Button>
        </div>
        {answer && <div className="mt-4 rounded-3xl bg-slate-100 p-4 text-sm leading-7 dark:bg-white/5"><p className="whitespace-pre-wrap">{answer.answer}</p></div>}
      </Card>
      {!documents.length ? <EmptyState title="Sin documentos visibles" text="Ejecuta scripts/index_documents.py para indexar documentos internos." /> : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {documents.map((doc) => (
            <Card key={doc.id}>
              <BookOpen className="text-indigo-500" />
              <h3 className="mt-3 font-black">{doc.title}</h3>
              <p className="mt-1 text-sm text-slate-500">{doc.filename}</p>
              <div className="mt-4 flex flex-wrap gap-2"><Badge>{doc.source || "interno"}</Badge><Badge tone="slate">{doc.chunk_count} chunks</Badge></div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
