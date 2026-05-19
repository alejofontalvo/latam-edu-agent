import { CheckCircle2 } from "lucide-react";

export default function Toast({ message }) {
  if (!message) return null;
  return (
    <div className="fixed bottom-5 right-5 z-50 flex items-center gap-2 rounded-2xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white shadow-2xl">
      <CheckCircle2 size={18} className="text-emerald-300" />
      {message}
    </div>
  );
}
