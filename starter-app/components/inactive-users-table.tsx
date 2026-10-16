"use client"

import type { ReactNode } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Skeleton } from "@/components/ui/skeleton"
import { useContractDrawer } from "@/components/contract-drawer"

export interface InactiveUser {
  emp_id: number
  name: string
  department: string
  email: string
  asset_id: number
  asset_name: string
  monthly_cost_per_seat: number
  last_active_date: string
  days_inactive: number
  status: string
}

interface InactiveUsersTableProps {
  users: InactiveUser[]
  notice?: ReactNode
  renderAction: (user: InactiveUser) => ReactNode
}

const DEPARTMENT_COLORS: Record<string, string> = {
  Engineering: "#29b5e8",
  Sales: "#7c3aed",
  Marketing: "#f97316",
  Finance: "#16a34a",
  Operations: "#e11d48",
}

export function InactiveUsersTable({ users, notice, renderAction }: InactiveUsersTableProps) {
  const { openContract } = useContractDrawer()
  const totalWaste = users
    .reduce((sum, u) => sum + Number(u.monthly_cost_per_seat || 0), 0)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Inactive Users (30+ days)</CardTitle>
      </CardHeader>
      <CardContent>
        {notice}
        <div className="mb-3 flex items-baseline gap-2">
          <span className="text-xl font-bold text-red-500">
            ${totalWaste.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
          <span className="text-sm text-muted-foreground">monthly opportunity awaiting review</span>
          <span className="ml-auto text-sm font-medium text-muted-foreground">
            ${(totalWaste * 12).toLocaleString(undefined, { maximumFractionDigits: 0 })} annualized
          </span>
        </div>
        {users.length === 0 ? (
          <p className="text-sm text-muted-foreground">No inactive users found — nice and tidy.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employee</TableHead>
                <TableHead>Dept</TableHead>
                <TableHead>Asset</TableHead>
                <TableHead className="text-right">Cost/mo</TableHead>
                <TableHead className="text-right">Days</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((u) => {
                const key = `${u.emp_id}-${u.asset_id}`
                return (
                  <TableRow key={key}>
                    <TableCell className="font-medium">{u.name}</TableCell>
                    <TableCell>
                      <span
                        className="inline-flex items-center gap-1.5 text-xs font-medium"
                        style={{ color: DEPARTMENT_COLORS[u.department] ?? "#64748b" }}
                      >
                        <span
                          className="h-1.5 w-1.5 rounded-full"
                          style={{ backgroundColor: DEPARTMENT_COLORS[u.department] ?? "#64748b" }}
                        />
                        {u.department}
                      </span>
                    </TableCell>
                    <TableCell>
                      <button
                        className="underline-offset-2 hover:underline text-left"
                        onClick={() => openContract(u.asset_id)}
                      >
                        {u.asset_name}
                      </button>
                    </TableCell>
                    <TableCell className="text-right">
                      ${Number(u.monthly_cost_per_seat).toFixed(2)}
                    </TableCell>
                    <TableCell className="text-right">
                      <Badge variant={u.days_inactive >= 60 ? "destructive" : "secondary"}>
                        {u.days_inactive}d
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {renderAction(u)}
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  )
}

export function InactiveUsersCardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-48" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-6 w-40 mb-3" />
        <Skeleton className="h-48 w-full" />
      </CardContent>
    </Card>
  )
}
