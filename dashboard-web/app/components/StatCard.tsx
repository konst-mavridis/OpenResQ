export default function StatCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string | number;
  sub?: string;
}) {
  return (
    <div className="bg-(--background) border border-border rounded-xl p-4 shadow-sm">
      <div className="text-sm text-foreground/60">{label}</div>
      <div className="text-2xl font-semibold mt-1">{value}</div>
      {sub && <div className="text-xs text-foreground/60 mt-1">{sub}</div>}
    </div>
  );
}
