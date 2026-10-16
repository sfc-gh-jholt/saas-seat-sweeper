import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

export interface DepartmentSpend {
  department: string
  total_monthly_spend: number
  employee_count: number
  assignment_count: number
}

const DEPARTMENT_COLORS: Record<string, string> = {
  Engineering: "#29b5e8",
  Sales: "#7c3aed",
  Marketing: "#f97316",
  Finance: "#16a34a",
  Operations: "#e11d48",
}

function colorFor(department: string): string {
  return DEPARTMENT_COLORS[department] ?? "#64748b"
}

export function DashboardCard({ departments }: { departments: DepartmentSpend[] }) {
  const maxSpend = Math.max(1, ...departments.map((d) => Number(d.total_monthly_spend || 0)))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Monthly Spend by Department</CardTitle>
      </CardHeader>
      <CardContent>
        {departments.length === 0 ? (
          <p className="text-sm text-muted-foreground">No active license assignments found.</p>
        ) : (
          <div className="space-y-4">
            {departments.map((d) => {
              const spend = Number(d.total_monthly_spend || 0)
              const pct = Math.max(4, Math.round((spend / maxSpend) * 100))
              return (
                <div key={d.department} className="space-y-1">
                  <div className="flex items-baseline justify-between text-sm">
                    <span className="font-medium">{d.department}</span>
                    <span className="text-muted-foreground">
                      ${spend.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      <span className="ml-2 text-xs">
                        · {d.employee_count} {Number(d.employee_count) === 1 ? "employee" : "employees"}
                      </span>
                    </span>
                  </div>
                  <div className="h-2.5 w-full rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{ width: `${pct}%`, backgroundColor: colorFor(d.department) }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function DashboardCardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-48" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-8 w-32 mb-4" />
        <Skeleton className="h-32 w-full" />
      </CardContent>
    </Card>
  )
}
