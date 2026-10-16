/**
 * Snowflake returns unquoted column names in UPPERCASE by default (e.g. `NAME`,
 * `MONTHLY_COST_PER_SEAT`). This app's SQL and TypeScript both use lowercase
 * snake_case field names, so every query result must be normalized before use
 * — otherwise property access like `row.name` silently returns `undefined`
 * (rendering blank text, `$NaN` for numbers, etc. with no thrown error).
 *
 * Apply this to every row set returned from querySnowflake() or from an API
 * route's JSON response.
 */
export function lowercaseKeys<T = Record<string, any>>(rows: Record<string, any>[]): T[] {
  return rows.map((row) => {
    const out: Record<string, any> = {}
    for (const key of Object.keys(row)) {
      out[key.toLowerCase()] = row[key]
    }
    return out as unknown as T
  })
}
