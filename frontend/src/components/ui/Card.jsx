import { motion } from "framer-motion";

export default function Card({ children, className = "", hover = true, ...props }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={hover ? { y: -4 } : undefined}
      transition={{ duration: 0.25 }}
      className={`rounded-3xl border border-white/60 bg-white/80 p-5 shadow-xl shadow-slate-200/60 backdrop-blur dark:border-white/10 dark:bg-slate-900/70 dark:shadow-black/20 ${className}`}
      {...props}
    >
      {children}
    </motion.div>
  );
}
