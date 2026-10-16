import { AskChat } from "@/components/ask-chat"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { KpiRow } from "@/components/kpi-row"
import { computeMetrics, formatCurrency, getAssetInventory, getDepartmentSpend, getInactiveUsers } from "@/lib/seat-sweeper-data"
import { Sigma, Search } from "lucide-react"

export const dynamic = "force-dynamic"

const questions = [
  "Which department has the most inactive Figma licenses?",
  "What is the penalty for cancelling Datadog seats early?",
  "If I cancel all inactive Figma users today, will we be charged a true-up penalty?",
  "How are we doing?",
]

export default async function AskPage() {
  const [departments, inactiveUsers, inventory] = await Promise.all([
    getDepartmentSpend(),
    getInactiveUsers(50),
    getAssetInventory(),
  ])
  const metrics = computeMetrics(departments, inactiveUsers, inventory)

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8 lg:pt-4">
      <div className="flex flex-col gap-2">
        <p className="text-sm font-medium uppercase tracking-[0.18em] text-sky-600 dark:text-sky-300">Cortex Agent route</p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Ask Seat Sweeper</h1>
        <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
          Ask natural-language questions about SaaS spend, inactive licenses, and vendor contract terms. Cortex Analyst handles structured data; Cortex Search indexes contract text.
        </p>
      </div>
      <KpiRow
        metrics={[
          { label: "Annualized Savings", value: formatCurrency(metrics.annualizedSavings), accent: "#e11d48" },
          { label: "Departments", value: departments.length.toLocaleString() },
          { label: "Contract Sources", value: inventory.filter((item) => item.contract_id).length.toLocaleString() },
          { label: "Sample Prompts", value: questions.length.toLocaleString() },
        ]}
      />
      <AskChat />
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">How the agent works</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm text-muted-foreground">
          <div className="flex items-center gap-3 rounded-xl bg-background p-3 ring-1 ring-border">
            <Sigma className="h-4 w-4 text-violet-500" />
            <span>Structured spend and license questions are answered via Cortex Analyst over a semantic view with RBAC row access policies.</span>
          </div>
          <div className="flex items-center gap-3 rounded-xl bg-background p-3 ring-1 ring-border">
            <Search className="h-4 w-4 text-emerald-500" />
            <span>Contract terms questions (cancellation penalties, true-up clauses, auto-renewal) are answered via Cortex Search over vendor contract text.</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
