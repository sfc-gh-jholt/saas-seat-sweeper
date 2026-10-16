import { beforeEach, expect, it, vi } from "vitest"
import { GET } from "@/app/api/contract/[id]/route"
import { querySnowflake } from "@/lib/snowflake"
vi.mock("@/lib/snowflake", () => ({ querySnowflake: vi.fn() }))
const get = (id: string) => GET(new Request("http://localhost"), { params: Promise.resolve({ id }) })
beforeEach(() => vi.clearAllMocks())

it.each(["0", "-1", "1.5", "1abc", "1e2", "", "9007199254740992"])("rejects contract id %s", async id => {
  expect((await get(id)).status).toBe(400)
  expect(querySnowflake).not.toHaveBeenCalled()
})
it("binds and normalizes contract rows", async () => {
  vi.mocked(querySnowflake).mockResolvedValue([{ ASSET_ID: 5, CONTRACT_TERMS_TEXT: "Terms" }])
  expect(await (await get("5")).json()).toEqual({ asset_id: 5, contract_terms_text: "Terms" })
  expect(querySnowflake).toHaveBeenCalledWith(expect.stringContaining("WHERE asset_id = ?"), { binds: [5] })
})
it("returns not found and safe errors", async () => {
  vi.mocked(querySnowflake).mockResolvedValueOnce([]).mockRejectedValueOnce(new Error("secret"))
  expect((await get("1")).status).toBe(404)
  const response = await get("1")
  expect(response.status).toBe(500)
  expect(await response.text()).not.toContain("secret")
})