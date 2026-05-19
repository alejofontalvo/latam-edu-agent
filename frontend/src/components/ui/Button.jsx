export default function Button({ children, className = "", variant = "primary", ...props }) {
  const variants = {
    primary: "bg-indigo-600 text-white shadow-lg shadow-indigo-500/20 hover:bg-indigo-500",
    secondary: "bg-white/70 text-slate-900 ring-1 ring-slate-200 hover:bg-white dark:bg-white/10 dark:text-white dark:ring-white/10",
    ghost: "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-white/10",
    danger: "bg-rose-600 text-white hover:bg-rose-500"
  };
  return (
    <button className={`inline-flex min-h-10 items-center justify-center gap-2 rounded-2xl px-4 text-sm font-semibold transition ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}
