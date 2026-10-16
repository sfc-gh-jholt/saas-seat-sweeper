import { NextResponse } from "next/server"
import { querySnowflake } from "@/lib/snowflake"
import { lowercaseKeys } from "@/lib/snowflake-utils"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const rows = await querySnowflake(`
      SELECT
        emp_id,
        name,
        department,
        email,
        asset_id,
        asset_name,
        monthly_cost_per_seat,
        last_active_date,
        days_inactive,
        status
      FROM SAAS_SEAT_SWEEPER.APP.V_INACTIVE_USERS_RLS
      ORDER BY days_inactive DESC
    `)
    return NextResponse.json(lowercaseKeys(rows))
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
