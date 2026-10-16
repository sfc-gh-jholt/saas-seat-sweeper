import { ContractProvider } from "@/components/contract-drawer"
import { InactiveUsersCard } from "@/components/inactive-users-card"
import { KpiRow } from "@/components/kpi-row"
import { computeMetrics, formatCurrency, getAssetInventory, getDepartmentSpend, getInactiveUsers } from "@/lib/seat-sweeper-data"

export const dynamic = "force-dynamic"

export default async function LicensesPage() {
  const [departments, inactiveUsers, inventory] = await Promise.all([
    getDepartmentSpend(),
    getInactiveUsers(),
    getAssetInventory(),
  ])
  const metrics = computeMetrics(departments, inactiveUsers, inventory)

  return (
    <ContractProvider>
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8 lg:pt-4">
        <div className="flex flex-col gap-2">
          <p className="text-sm font-medium uppercase tracking-[0.18em] text-sky-600 dark:text-sky-300">License command center</p>
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Reclaim inactive SaaS spend</h1>
          <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
            Review paid assignments with no activity for 30+ days, inspect their contract context, and flag waste for reclamation.
          </p>
        </div>
        <KpiRow
          metrics={[
            { label: "Annualized Opportunity", value: formatCurrency(metrics.annualizedSavings), accent: "#e11d48" },
            { label: "Monthly Waste", value: formatCurrency(metrics.monthlyWaste), accent: "#e11d48" },
            { label: "Inactive Assignments", value: metrics.inactiveCount.toLocaleString() },
            { label: "Departments", value: departments.length.toLocaleString() },
          ]}
        />
        <InactiveUsersCard users={inactiveUsers} />
      </div>
    </ContractProvider>
  )
}