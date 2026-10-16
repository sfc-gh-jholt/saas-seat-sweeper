import { NextResponse } from "next/server"
import { querySnowflake } from "@/lib/snowflake"
import { isPositiveSafeInteger, updatedRowCount } from "@/lib/reclaim"

export const dynamic = "force-dynamic"

export async function POST(request: Request) {
  let body: unknown
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 })
  }
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return NextResponse.json({ error: "Expected a JSON object" }, { status: 400 })
  }
  const { emp_id, asset_id } = body as Record<string, unknown>
  if (!isPositiveSafeInteger(emp_id) || !isPositiveSafeInteger(asset_id)) {
    return NextResponse.json(
      { error: "emp_id and asset_id must be positive safe integers" },
      { status: 400 }
    )
  }
  try {
    const rows = await querySnowflake(`
      UPDATE SAAS_SEAT_SWEEPER.RAW.EMPLOYEE_ASSETS
      SET status = 'Flagged'
      WHERE emp_id = ?
        AND asset_id = ?
        AND status = 'Inactive'
    `, { binds: [emp_id, asset_id] })

    // Snowflake returns a single SUMMARY row for DML, not one row per affected row:
    //   [{ "number of rows updated": 1, "number of multi-joined rows updated": 0 }]
    // So `rows.length` is 1 whether the UPDATE matched one row or none, which makes
    // it useless as an affected-row count. Read the count out of the summary row.
    const updated = updatedRowCount(rows)

    return NextResponse.json({
      success: true,
      emp_id,
      asset_id,
      rows_affected: updated,
      outcome: updated > 0 ? "flagged" : "no-op",
      message:
        updated > 0
          ? `${updated} assignment(s) flagged for review. No vendor cancellation or realized savings.`
          : `No inactive license matched (emp_id=${emp_id}, asset_id=${asset_id}) — it may already be flagged`
    })
  } catch {
    return NextResponse.json(
      { error: "Unable to confirm reclamation. Refresh before retrying; the assignment may have changed." },
      { status: 500 }
    )
  }
}
