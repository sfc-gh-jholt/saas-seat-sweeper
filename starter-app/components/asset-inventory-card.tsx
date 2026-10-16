"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Skeleton } from "@/components/ui/skeleton"
import { useContractDrawer } from "@/components/contract-drawer"
import { FileText } from "lucide-react"

export interface AssetInventoryItem {
  asset_id: number
  asset_name: string
  monthly_cost_per_seat: number
  asset_type: string
  contract_id: number | null
  vendor_name: string | null
  renewal_date: string | null
  auto_renew: boolean | null
  assigned_count: number
}

export function AssetInventoryCard({ inventory }: { inventory: AssetInventoryItem[] }) {
  const { openContract } = useContractDrawer()

  return (
    <Card>
      <CardHeader>
        <CardTitle>Asset Inventory</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Asset</TableHead>
              <TableHead>Type</TableHead>
              <TableHead className="text-right">Cost/seat</TableHead>
              <TableHead className="text-right">Assigned</TableHead>
              <TableHead>Renewal</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {inventory.map((a) => (
              <TableRow
                key={a.asset_id}
                className="cursor-pointer hover:bg-accent/50"
                onClick={() => openContract(a.asset_id)}
              >
                <TableCell className="font-medium">{a.asset_name}</TableCell>
                <TableCell>
                  <Badge variant={a.asset_type === "License" ? "default" : "secondary"}>
                    {a.asset_type}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  {Number(a.monthly_cost_per_seat) > 0
                    ? `$${Number(a.monthly_cost_per_seat).toFixed(2)}`
                    : "—"}
                </TableCell>
                <TableCell className="text-right">{a.assigned_count}</TableCell>
                <TableCell className="text-muted-foreground">
                  {a.renewal_date ? new Date(a.renewal_date).toLocaleDateString() : "N/A"}
                </TableCell>
                <TableCell>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <p className="text-xs text-muted-foreground mt-3">Click a row to view its contract terms.</p>
      </CardContent>
    </Card>
  )
}

export function AssetInventoryCardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-40" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-48 w-full" />
      </CardContent>
    </Card>
  )
}
