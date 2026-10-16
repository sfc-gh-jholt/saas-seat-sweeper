"use client"

import { useRef, useState, useTransition } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { InactiveUsersTable, type InactiveUser } from "@/components/inactive-users-table"

export { InactiveUsersCardSkeleton } from "@/components/inactive-users-table"
export type { InactiveUser } from "@/components/inactive-users-table"

export function InactiveUsersCard({ users }: { users: InactiveUser[] }) {
  const router = useRouter()
  const inFlight = useRef(false)
  const [reclaiming, setReclaiming] = useState<string | null>(null)
  const [refreshing, startTransition] = useTransition()
  const [feedback, setFeedback] = useState<{ error: boolean; message: string } | null>(null)

  async function handleReclaim(user: InactiveUser) {
    if (inFlight.current || refreshing) return
    inFlight.current = true
    setReclaiming(`${user.emp_id}-${user.asset_id}`)
    setFeedback(null)
    try {
      const response = await fetch("/api/reclaim", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ emp_id: user.emp_id, asset_id: user.asset_id }),
      })
      if (!response.ok) throw new Error("Request failed")
      const result = await response.json()
      if (result?.success !== true || !Number.isSafeInteger(result.rows_affected) || result.rows_affected < 0) {
        throw new Error("Unknown result")
      }
      setFeedback({
        error: false,
        message: result.rows_affected > 0
          ? `${result.rows_affected} assignment(s) flagged for review. No vendor cancellation or realized savings.`
          : "No change: no inactive assignment matched. It may already be flagged.",
      })
      // Re-read all server-rendered KPIs and rows, including on a repeated no-op.
      // Never infer reduced spend or mark a row Flagged from HTTP 200 alone.
      startTransition(() => router.refresh())
    } catch {
      setFeedback({ error: true, message: "Unable to confirm reclamation. Refresh before retrying; the assignment may have changed." })
    } finally {
      inFlight.current = false
      setReclaiming(null)
    }
  }

  return <InactiveUsersTable
    users={users}
    notice={<>
      <p className="mb-3 text-sm text-muted-foreground">Flagging requests review only; it does not cancel a vendor license or reduce billed spend.</p>
      {feedback && <p role={feedback.error ? "alert" : "status"} className={`mb-3 text-sm ${feedback.error ? "text-red-500" : "text-muted-foreground"}`}>{feedback.message}</p>}
      {refreshing && <p role="status" className="mb-3 text-sm">Refreshing opportunity metrics...</p>}
    </>}
    renderAction={(user) => <Button
      size="sm"
      variant="outline"
      disabled={reclaiming !== null || refreshing}
      onClick={() => handleReclaim(user)}
    >{reclaiming === `${user.emp_id}-${user.asset_id}` ? "Flagging..." : "Reclaim"}</Button>}
  />
}