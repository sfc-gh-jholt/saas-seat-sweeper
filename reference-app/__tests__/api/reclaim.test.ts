import { beforeEach, describe, expect, it, vi } from "vitest"
import { POST } from "@/app/api/reclaim/route"
import { querySnowflake } from "@/lib/snowflake"

vi.mock("@/lib/snowflake", () => ({ querySnowflake: vi.fn() }))
const request = (body: unknown) => new Request("http://localhost/api/reclaim", { method: "POST", body: JSON.stringify(body) })
beforeEach(() => vi.clearAllMocks())

describe("reclamation", () => {
  it("binds identifiers and returns one update followed by a repeated no-op", async () => {
    vi.mocked(querySnowflake)
      .mockResolvedValueOnce([{ "number of rows updated": 1 }])
      .mockResolvedValueOnce([{ "NUMBER OF ROWS UPDATED": "0" }])
    for (const [count, outcome] of [[1, "flagged"], [0, "no-op"]]) {
      const response = await POST(request({ emp_id: 12345, asset_id: 67890 }))
      expect(response.status).toBe(200)
      expect(await response.json()).toMatchObject({ success: true, rows_affected: count, outcome })
    }
    const [sql, options] = vi.mocked(querySnowflake).mock.calls[0]
    expect(sql).toContain("WHERE emp_id = ?")
    expect(sql).toContain("AND asset_id = ?")
    expect(sql).toContain("AND status = 'Inactive'")
    expect(sql).not.toContain("12345")
    expect(options).toEqual({ binds: [12345, 67890] })
  })

  it.each([null, [], true, "body", {}, { emp_id: 1 }, ...[0, -1, 1.5, "1", "1; DELETE", null, true, Number.MAX_SAFE_INTEGER + 1].flatMap(value => [
    { emp_id: value, asset_id: 1 }, { emp_id: 1, asset_id: value },
  ])])("rejects invalid body %j without querying", async body => {
    expect((await POST(request(body))).status).toBe(400)
    expect(querySnowflake).not.toHaveBeenCalled()
  })

  it("rejects malformed JSON", async () => {
    expect((await POST(new Request("http://localhost/api/reclaim", { method: "POST", body: "{" }))).status).toBe(400)
    expect(querySnowflake).not.toHaveBeenCalled()
  })

  it.each([
    [], [{}], [{ "number of rows updated": null }], [{ "number of rows updated": -1 }],
    [{ "number of rows updated": "bad" }], [{ "number of rows updated": 1.5 }],
    [{ "number of rows updated": Number.MAX_SAFE_INTEGER + 1 }],
    [{ "number of rows updated": true }], [{ "number of rows updated": "" }],
    [{ "number of rows updated": 1 }, { "number of rows updated": 0 }],
    [{ "number of rows updated": 1, "NUMBER OF ROWS UPDATED": 0 }],
  ].map(rows => ({ rows })))("does not turn unknown summary $rows into no-op", async ({ rows }) => {
    vi.mocked(querySnowflake).mockResolvedValue(rows)
    expect((await POST(request({ emp_id: 1, asset_id: 2 }))).status).toBe(500)
  })

  it.each([1, "1", 2, "2", 0, "0"])("reports exact DML count %j rather than summary length", async count => {
    vi.mocked(querySnowflake).mockResolvedValue([{ "NuMbEr Of RoWs UpDaTeD": count }])
    const response = await POST(request({ emp_id: Number.MAX_SAFE_INTEGER, asset_id: 1 }))
    expect(response.status).toBe(200)
    expect(await response.json()).toMatchObject({ rows_affected: Number(count), outcome: Number(count) > 0 ? "flagged" : "no-op" })
    expect(vi.mocked(querySnowflake).mock.calls[0][1]?.binds).toEqual([Number.MAX_SAFE_INTEGER, 1])
  })

  it("does not leak database errors", async () => {
    vi.mocked(querySnowflake).mockRejectedValue(new Error("secret token SQL internal-account"))
    const response = await POST(request({ emp_id: 1, asset_id: 2 }))
    expect(response.status).toBe(500)
    expect(await response.text()).not.toMatch(/secret|token|internal-account/)
  })
})