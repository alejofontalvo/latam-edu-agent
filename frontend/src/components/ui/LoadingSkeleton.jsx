export default function LoadingSkeleton({ lines = 3 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: lines }).map((_, index) => (
        <div key={index} className="h-4 animate-pulse rounded-full bg-slate-200 dark:bg-white/10" style={{ width: `${92 - index * 14}%` }} />
      ))}
    </div>
  );
}
