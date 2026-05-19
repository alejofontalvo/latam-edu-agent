import { ArrowRight } from "lucide-react";
import Card from "../ui/Card.jsx";

export default function QuickActionCard({ icon: Icon, title, text, onClick }) {
  return (
    <Card className="cursor-pointer" onClick={onClick}>
      <div className="flex items-start gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-950 text-white dark:bg-white dark:text-slate-950">
          <Icon size={20} />
        </div>
        <div className="flex-1">
          <h3 className="font-black">{title}</h3>
          <p className="mt-1 text-sm leading-6 text-slate-500 dark:text-slate-400">{text}</p>
        </div>
        <ArrowRight className="mt-1 text-slate-400" size={18} />
      </div>
    </Card>
  );
}
