import { Card, CardContent } from "@/components/ui/card"

interface Metric {
  label: string
  value: string
  accent?: string
}

export function KpiRow({ metrics }: { metrics: Metric[] }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {metrics.map((m) => (
        <Card key={m.label}>
          <CardContent className="py-4">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{m.label}</p>
            <p
              className="text-2xl font-bold mt-1"
              style={m.accent ? { color: m.accent } : undefined}
            >
              {m.value}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
