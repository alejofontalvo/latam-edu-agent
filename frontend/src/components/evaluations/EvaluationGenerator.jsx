import { useState } from "react";
import { Eye, EyeOff, WandSparkles } from "lucide-react";
import { generateEvaluation } from "../../services/api.js";
import Button from "../ui/Button.jsx";
import Card from "../ui/Card.jsx";
import Badge from "../ui/Badge.jsx";

export default function EvaluationGenerator() {
  const [showAnswers, setShowAnswers] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [form, setForm] = useState({ area: "Lectura crítica", country: "Colombia", exam_reference: "Saber 11", difficulty: "media", number_of_questions: 5, topic: "comprensión lectora" });

  const submit = async (event) => {
    event.preventDefault();
    setEvaluation(await generateEvaluation({ ...form, number_of_questions: Number(form.number_of_questions) }));
  };

  return (
    <div className="space-y-5">
      <div><p className="text-sm font-bold uppercase tracking-[0.25em] text-indigo-500">Evaluaciones</p><h2 className="mt-2 text-3xl font-black">Generador tipo prueba estatal</h2></div>
      <Card hover={false}>
        <form onSubmit={submit} className="grid gap-3 md:grid-cols-3">
          {["area", "country", "exam_reference", "difficulty", "topic"].map((field) => <input key={field} className="input-premium" value={form[field]} onChange={(e) => setForm({ ...form, [field]: e.target.value })} />)}
          <input className="input-premium" type="number" min="1" max="20" value={form.number_of_questions} onChange={(e) => setForm({ ...form, number_of_questions: e.target.value })} />
          <Button className="md:col-span-2"><WandSparkles size={18} /> Generar evaluación</Button>
          <Button type="button" variant="secondary" onClick={() => setShowAnswers((v) => !v)}>{showAnswers ? <EyeOff size={18} /> : <Eye size={18} />} Respuestas</Button>
        </form>
      </Card>
      {evaluation && <div className="space-y-4">
        <h3 className="text-2xl font-black">{evaluation.title}</h3>
        {evaluation.questions.map((question) => (
          <Card key={question.number}>
            <div className="mb-3 flex flex-wrap gap-2"><Badge>{question.area}</Badge><Badge tone="amber">{question.difficulty}</Badge><Badge tone="slate">{question.exam_reference}</Badge></div>
            <p className="font-bold leading-7">{question.question}</p>
            <div className="mt-4 grid gap-2">
              {Object.entries(question.options).map(([key, value]) => <div key={key} className="rounded-2xl bg-slate-100 p-3 text-sm dark:bg-white/5"><strong>{key}.</strong> {value}</div>)}
            </div>
            {showAnswers && <div className="mt-4 rounded-2xl bg-emerald-50 p-4 text-sm text-emerald-900 dark:bg-emerald-500/10 dark:text-emerald-100"><strong>Respuesta {question.correct_answer}:</strong> {question.explanation}</div>}
          </Card>
        ))}
      </div>}
    </div>
  );
}
