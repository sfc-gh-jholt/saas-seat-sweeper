import { NextResponse } from "next/server"
import { querySnowflake } from "@/lib/snowflake"
import { lowercaseKeys } from "@/lib/snowflake-utils"

export const dynamic = "force-dynamic"

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    const assetId = Number(id)
    if (!/^\d+$/.test(id) || !Number.isSafeInteger(assetId) || assetId <= 0) {
      return NextResponse.json({ error: "Invalid asset_id" }, { status: 400 })
    }

    const rows = await querySnowflake(`
      SELECT
        asset_id,
        asset_name,
        contract_id,
        vendor_name,
        renewal_date,
        auto_renew,
        contract_terms_text
      FROM SAAS_SEAT_SWEEPER.APP.V_CONTRACT_TERMS
      WHERE asset_id = ?
    `, { binds: [assetId] })

    if (!rows || rows.length === 0) {
      return NextResponse.json({ error: "Contract not found" }, { status: 404 })
    }
    return NextResponse.json(lowercaseKeys(rows)[0])
  } catch {
    return NextResponse.json({ error: "Unable to load contract" }, { status: 500 })
  }
}
