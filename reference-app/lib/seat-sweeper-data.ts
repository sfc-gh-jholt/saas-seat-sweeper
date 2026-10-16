import { querySnowflake } from "@/lib/snowflake"
import { lowercaseKeys } from "@/lib/snowflake-utils"

export interface DepartmentSpend {
  department: string
  total_monthly_spend: number
  employee_count: number
  assignment_count: number
}

export interface InactiveUser {
  emp_id: number
  name: string
  department: string
  email: string
  asset_id: number
  asset_name: string
  monthly_cost_per_seat: number
  last_active_date: string
  days_inactive: number
  status: string
}

export interface AssetInventoryItem {
  asset_id: number
  asset_name: string
  monthly_cost_per_seat: number
  asset_type: string
  contract_id: number | null
  vendor_name: string | null
  renewal_date: string | null
  auto_renew: boolean | null
  assigned_count: number
}

export interface SeatSweeperMetrics {
  monthlySpend: number
  annualizedSpend: number
  monthlyWaste: number
  annualizedSavings: number
  employeeCount: number
  assignmentCount: number
  inactiveCount: number
  trackedAssets: number
  renewalRisks: AssetInventoryItem[]
}

// Workshop diagnosis fixture: these reads intentionally return [] on failure.
// Empty data is not proof of zero spend; the app displays a warning about this.
export async function getDepartmentSpend(): Promise<DepartmentSpend[]> {
  try {
    const rows = await querySnowflake(`
      SELECT department, total_monthly_spend, employee_count, assignment_count
      FROM SAAS_SEAT_SWEEPER.APP.V_SPEND_BY_DEPARTMENT_RLS
      ORDER BY total_monthly_spend DESC
    `)
    return lowercaseKeys<DepartmentSpend>(rows)
  } catch {
    return []
  }
}

export async function getInactiveUsers(limit?: number): Promise<InactiveUser[]> {
  try {
    const rows = await querySnowflake(`
      SELECT
        emp_id, name, department, email, asset_id, asset_name,
        monthly_cost_per_seat, last_active_date, days_inactive, status
      FROM SAAS_SEAT_SWEEPER.APP.V_INACTIVE_USERS_RLS
      WHERE monthly_cost_per_seat > 0
      ORDER BY days_inactive DESC, monthly_cost_per_seat DESC
      ${limit ? `LIMIT ${limit}` : ""}
    `)
    return lowercaseKeys<InactiveUser>(rows)
  } catch {
    return []
  }
}

export async function getAssetInventory(): Promise<AssetInventoryItem[]> {
  try {
    const rows = await querySnowflake(`
      SELECT
        asset_id, asset_name, monthly_cost_per_seat, asset_type,
        contract_id, vendor_name, renewal_date, auto_renew, assigned_count
      FROM SAAS_SEAT_SWEEPER.APP.V_ASSET_INVENTORY
      ORDER BY asset_name
    `)
    return lowercaseKeys<AssetInventoryItem>(rows)
  } catch {
    return []
  }
}

export function computeMetrics(
  departments: DepartmentSpend[],
  inactiveUsers: InactiveUser[],
  inventory: AssetInventoryItem[]
): SeatSweeperMetrics {
  const monthlySpend = departments.reduce((sum, d) => sum + Number(d.total_monthly_spend || 0), 0)
  const monthlyWaste = inactiveUsers.reduce((sum, u) => sum + Number(u.monthly_cost_per_seat || 0), 0)
  const employeeCount = departments.reduce((sum, d) => sum + Number(d.employee_count || 0), 0)
  const assignmentCount = departments.reduce((sum, d) => sum + Number(d.assignment_count || 0), 0)
  const renewalRisks = inventory
    .filter((item) => item.renewal_date && item.auto_renew)
    .sort((a, b) => String(a.renewal_date).localeCompare(String(b.renewal_date)))
    .slice(0, 4)

  return {
    monthlySpend,
    annualizedSpend: monthlySpend * 12,
    monthlyWaste,
    annualizedSavings: monthlyWaste * 12,
    employeeCount,
    assignmentCount,
    inactiveCount: inactiveUsers.length,
    trackedAssets: inventory.length,
    renewalRisks,
  }
}

export function formatCurrency(value: number, maximumFractionDigits = 0): string {
  return `$${value.toLocaleString(undefined, { maximumFractionDigits })}`
}