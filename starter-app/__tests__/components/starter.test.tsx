// @vitest-environment jsdom
import { act } from "react"
import { createRoot } from "react-dom/client"
import { expect, it, vi } from "vitest"
import { InactiveUsersCard } from "@/components/inactive-users-card"
import AskPage from "@/app/ask/page"
vi.mock("@/components/contract-drawer", () => ({ useContractDrawer: () => ({ openContract: vi.fn() }) }))

it("offers review and contract access without a write button or Ask form", async () => {
  Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true })
  const container = document.createElement("div")
  const root = createRoot(container)
  try {
    await act(async () => root.render(<><InactiveUsersCard users={[]} /><AskPage /></>))
    expect(container.textContent).toContain("Read-only starter")
    expect(container.textContent).toContain("no agent endpoint")
    expect(container.querySelector("form, textarea")).toBeNull()
    expect(Array.from(container.querySelectorAll("button")).some(button => button.textContent === "Reclaim")).toBe(false)
    expect(container.querySelector('a[href="/inventory"]')).not.toBeNull()
  } finally { await act(async () => root.unmount()) }
})