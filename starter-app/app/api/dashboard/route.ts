import { NextResponse } from "next/server"
import { querySnowflake } from "@/lib/snowflake"
import { lowercaseKeys } from "@/lib/snowflake-utils"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const rows = await querySnowflake(`
      SELECT
        department,
        total_monthly_spend,
        employee_count,
        assignment_count
      FROM SAAS_SEAT_SWEEPER.APP.V_SPEND_BY_DEPARTMENT_RLS
      ORDER BY total_monthly_spend DESC
    `)
    return NextResponse.json(lowercaseKeys(rows))
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
