import { afterEach, beforeEach, expect, it, vi } from "vitest"
import fs from "fs"
import snowflake from "snowflake-sdk"
import { headers } from "next/headers"
import { closePool, querySnowflake, resetTomlConfigCache } from "@/lib/snowflake"

vi.mock("fs")
vi.mock("next/headers", () => ({ headers: vi.fn() }))
vi.mock("snowflake-sdk", () => ({ default: { configure: vi.fn(), createPool: vi.fn(), normalizeConnectionOptions: (value: unknown) => value } }))

const execute = vi.fn()
beforeEach(() => {
  vi.clearAllMocks()
  resetTomlConfigCache()
  for (const key of ["SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_CONNECTION_NAME", "SNOWFLAKE_DEFAULT_CONNECTION_NAME"]) vi.stubEnv(key, "")
  vi.stubEnv("SNOWFLAKE_SDK_QUIET", "1")
  vi.mocked(fs.existsSync).mockReturnValue(false)
  vi.mocked(fs.readFileSync).mockImplementation(() => { throw new Error("No file") })
  execute.mockImplementation(options => options.complete(null, null, [{ count: 1 }]))
  vi.mocked(snowflake.createPool).mockReturnValue({
    use: (fn: (connection: unknown) => unknown) => fn({ execute }), drain: async () => {},
  } as unknown as ReturnType<typeof snowflake.createPool>)
})
afterEach(async () => { await closePool(); vi.unstubAllEnvs() })

it.each(["owner", "caller", "password", "toml"])("passes binds to SDK on %s normal execution path", async mode => {
  if (mode === "owner" || mode === "caller") {
    vi.mocked(fs.readFileSync).mockReturnValue("service-token")
    vi.mocked(headers).mockResolvedValue(new Headers({ "sf-context-current-user-token": "caller-token" }) as Awaited<ReturnType<typeof headers>>)
  } else if (mode === "password") {
    vi.stubEnv("SNOWFLAKE_USER", "user")
    vi.stubEnv("SNOWFLAKE_PASSWORD", "password")
  } else {
    vi.mocked(fs.existsSync).mockImplementation(file => String(file).endsWith("connections.toml"))
    vi.mocked(fs.readFileSync).mockImplementation(file => {
      if (String(file).endsWith("connections.toml")) return '[workshop]\naccount="test"\nuser="test"'
      throw new Error("No token")
    })
  }
  const binds = [123, "quoted ' value"]
  await querySnowflake("SELECT ?, ?", { binds, callersRights: mode === "caller" })
  expect(execute).toHaveBeenCalledWith(expect.objectContaining({ sqlText: "SELECT ?, ?", binds }))
})

it("propagates SDK failures rather than empty results", async () => {
  vi.stubEnv("SNOWFLAKE_USER", "user")
  vi.stubEnv("SNOWFLAKE_PASSWORD", "password")
  execute.mockImplementation(options => options.complete(new Error("failure")))
  await expect(querySnowflake("SELECT ?", { binds: [1] })).rejects.toThrow("Query failed")
})