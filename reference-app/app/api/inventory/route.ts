import { NextResponse } from "next/server"
import { querySnowflake } from "@/lib/snowflake"
import { lowercaseKeys } from "@/lib/snowflake-utils"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const rows = await querySnowflake(`
      SELECT
        asset_id,
        asset_name,
        monthly_cost_per_seat,
        asset_type,
        contract_id,
        vendor_name,
        renewal_date,
        auto_renew,
        assigned_count
      FROM SAAS_SEAT_SWEEPER.APP.V_ASSET_INVENTORY
      ORDER BY asset_name
    `)
    return NextResponse.json(lowercaseKeys(rows))
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
