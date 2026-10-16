// @vitest-environment jsdom
import { act } from "react"
import { createRoot, type Root } from "react-dom/client"
import { afterEach, beforeEach, expect, it, vi } from "vitest"
import { InactiveUsersCard } from "@/components/inactive-users-card"
import { computeMetrics } from "@/lib/seat-sweeper-data"
import { KpiRow } from "@/components/kpi-row"
import LicensesPage from "@/app/licenses/page"
import { POST } from "@/app/api/reclaim/route"
import { querySnowflake } from "@/lib/snowflake"

const { refresh } = vi.hoisted(() => ({ refresh: vi.fn() }))
vi.mock("next/navigation", () => ({ useRouter: () => ({ refresh }) }))
vi.mock("@/lib/snowflake", () => ({ querySnowflake: vi.fn() }))
vi.mock("@/components/contract-drawer", () => ({
  useContractDrawer: () => ({ openContract: vi.fn() }),
  ContractProvider: ({ children }: { children: import("react").ReactNode }) => children,
}))
const user = { emp_id: 1, asset_id: 2, name: "Example", department: "Finance", email: "test@example.com", asset_name: "Tool", monthly_cost_per_seat: 20, days_inactive: 45, last_active_date: "2026-01-01", status: "Inactive" }
let container: HTMLDivElement
let root: Root
beforeEach(() => {
  vi.clearAllMocks()
  Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })
  container = document.createElement("div")
  document.body.appendChild(container)
  root = createRoot(container)
})
afterEach(async () => { await act(async () => root.unmount()); container.remove(); vi.unstubAllGlobals() })
async function render(users = [user]) {
  const metrics = computeMetrics([], users, [])
  await act(async () => root.render(<><KpiRow metrics={[{ label: "Annualized Opportunity", value: String(metrics.annualizedSavings) }]} /><InactiveUsersCard users={users} /></>))
}
async function click() {
  await act(async () => Array.from(container.querySelectorAll("button")).find(button => button.textContent === "Reclaim")!.click())
}

it("shows success and refreshes authoritative rows and opportunity KPIs", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json({ success: true, rows_affected: 1 })))
  await render()
  expect(container.textContent).toContain("240")
  await click()
  expect(container.querySelector('[role="status"]')?.textContent).toContain("1 assignment(s) flagged")
  expect(refresh).toHaveBeenCalledOnce()
  await render([])
  expect(container.textContent).not.toContain("240")
  expect(container.textContent).not.toContain("Reclaim")
  expect(container.textContent).toContain("1 assignment(s) flagged")
})
it("shows no-op without claiming a successful flag or optimistic savings", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json({ success: true, rows_affected: 0 })))
  await render(); await click()
  expect(container.textContent).toContain("No change")
  expect(container.textContent).toContain("240")
  expect(container.textContent).not.toContain("1 assignment(s) flagged")
  expect(refresh).toHaveBeenCalledOnce()
})
it.each(["http", "network", "json", "summary"])("shows safe %s failure without changing metrics", async kind => {
  const fetcher = kind === "network" ? vi.fn().mockRejectedValue(new Error("secret")) : vi.fn().mockResolvedValue(
    kind === "http" ? Response.json({ error: "secret" }, { status: 500 }) : kind === "json" ? new Response("bad") : Response.json({ success: true })
  )
  vi.stubGlobal("fetch", fetcher)
  await render(); await click()
  expect(container.querySelector('[role="alert"]')?.textContent).toContain("Unable to confirm")
  expect(container.textContent).not.toContain("secret")
  expect(container.textContent).toContain("240")
  expect(refresh).not.toHaveBeenCalled()
})
it("blocks duplicate clicks while the request is pending", async () => {
  let finish!: (response: Response) => void
  const fetcher = vi.fn().mockReturnValue(new Promise<Response>(resolve => { finish = resolve }))
  vi.stubGlobal("fetch", fetcher)
  await render(); await click()
  expect(container.querySelector<HTMLButtonElement>("button:disabled")?.textContent).toBe("Flagging...")
  expect(fetcher).toHaveBeenCalledOnce()
  await act(async () => container.querySelector<HTMLButtonElement>("button:disabled")!.click())
  expect(fetcher).toHaveBeenCalledOnce()
  await act(async () => finish(Response.json({ success: true, rows_affected: 1 })))
})

it("refreshes the actual Licenses page from mocked server data after the real POST handler", async () => {
  let inactive = true
  vi.mocked(querySnowflake).mockImplementation(async (sql, options) => {
    if (sql.includes("UPDATE SAAS_SEAT_SWEEPER.RAW.EMPLOYEE_ASSETS")) {
      expect(options?.binds).toEqual([user.emp_id, user.asset_id])
      const count = inactive ? 1 : 0
      inactive = false
      return [{ "number of rows updated": count }]
    }
    if (sql.includes("V_INACTIVE_USERS_RLS")) return inactive ? [Object.fromEntries(Object.entries(user).map(([key, value]) => [key.toUpperCase(), value]))] : []
    if (sql.includes("V_SPEND_BY_DEPARTMENT_RLS")) return [{ DEPARTMENT: "Finance", TOTAL_MONTHLY_SPEND: 20, EMPLOYEE_COUNT: 1, ASSIGNMENT_COUNT: 1 }]
    if (sql.includes("V_ASSET_INVENTORY")) return []
    throw new Error("Unexpected query")
  })
  vi.stubGlobal("fetch", vi.fn().mockImplementation((_url, options) => POST(new Request("http://localhost/api/reclaim", options))))
  let refreshed: ReturnType<typeof LicensesPage> | undefined
  refresh.mockImplementation(() => { refreshed = LicensesPage() })
  await act(async () => root.render(await LicensesPage()))
  expect(container.textContent).toContain("Annualized Opportunity$240")
  expect(container.textContent).toContain("Monthly Waste$20")
  expect(container.textContent).toContain("Inactive Assignments1")
  await click()
  expect(refresh).toHaveBeenCalledOnce()
  await act(async () => root.render(await refreshed!))
  expect(container.textContent).toContain("Annualized Opportunity$0")
  expect(container.textContent).toContain("Monthly Waste$0")
  expect(container.textContent).toContain("Inactive Assignments0")
  expect(container.textContent).toContain("1 assignment(s) flagged for review")
  expect(Array.from(container.querySelectorAll("button")).some(button => button.textContent === "Reclaim")).toBe(false)
  const repeated = await POST(new Request("http://localhost/api/reclaim", { method: "POST", body: JSON.stringify({ emp_id: user.emp_id, asset_id: user.asset_id }) }))
  expect(await repeated.json()).toMatchObject({ rows_affected: 0, outcome: "no-op" })
})