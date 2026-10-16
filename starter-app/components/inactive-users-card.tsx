"use client"

import { Badge } from "@/components/ui/badge"
import { InactiveUsersTable, type InactiveUser } from "@/components/inactive-users-table"

export { InactiveUsersCardSkeleton } from "@/components/inactive-users-table"
export type { InactiveUser } from "@/components/inactive-users-table"

export function InactiveUsersCard({ users }: { users: InactiveUser[] }) {
  return <InactiveUsersTable
    users={users}
    notice={<p className="mb-3 text-sm text-muted-foreground">Read-only starter. Add reclamation during the write-back exercise after your first deployment.</p>}
    renderAction={() => <Badge variant="secondary">Review only</Badge>}
  />
}