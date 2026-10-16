import { AssetInventoryCard } from "@/components/asset-inventory-card"
import { ContractProvider } from "@/components/contract-drawer"
import { KpiRow } from "@/components/kpi-row"
import { computeMetrics, formatCurrency, getAssetInventory, getDepartmentSpend, getInactiveUsers } from "@/lib/seat-sweeper-data"

export const dynamic = "force-dynamic"

export default async function InventoryPage() {
  const [departments, inactiveUsers, inventory] = await Promise.all([
    getDepartmentSpend(),
    getInactiveUsers(),
    getAssetInventory(),
  ])
  const metrics = computeMetrics(departments, inactiveUsers, inventory)
  const assignedSeats = inventory.reduce((sum, item) => sum + Number(item.assigned_count || 0), 0)
  const contractBacked = inventory.filter((item) => item.contract_id).length

  return (
    <ContractProvider>
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8 lg:pt-4">
        <div className="flex flex-col gap-2">
          <p className="text-sm font-medium uppercase tracking-[0.18em] text-sky-600 dark:text-sky-300">Asset intelligence</p>
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Inventory and contract terms</h1>
          <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
            Connect assigned assets to vendor terms, renewal windows, auto-renewal obligations, and unstructured contract language.
          </p>
        </div>
        <KpiRow
          metrics={[
            { label: "Tracked Assets", value: metrics.trackedAssets.toLocaleString() },
            { label: "Assigned Seats", value: assignedSeats.toLocaleString() },
            { label: "Contract Backed", value: contractBacked.toLocaleString() },
            { label: "Annualized Spend", value: formatCurrency(metrics.annualizedSpend) },
          ]}
        />
        <AssetInventoryCard inventory={inventory} />
      </div>
    </ContractProvider>
  )
}