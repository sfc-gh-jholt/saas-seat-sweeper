export function isPositiveSafeInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isSafeInteger(value) && value > 0
}

/** Missing or malformed summaries are unknown outcomes, never successful no-ops. */
export function updatedRowCount(rows: Record<string, unknown>[]): number {
  if (rows.length !== 1 || !rows[0]) throw new Error("Invalid DML summary")
  const entries = Object.entries(rows[0]).filter(([key]) => key.toLowerCase() === "number of rows updated")
  const value = entries.length === 1 ? entries[0][1] : undefined
  const count = typeof value === "string" && /^\d+$/.test(value) ? Number(value) : value
  if (typeof count !== "number" || !Number.isSafeInteger(count) || count < 0) {
    throw new Error("Invalid DML count")
  }
  return count
}