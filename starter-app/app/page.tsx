import Link from "next/link"
import Image from "next/image"
import { ArrowRight, BadgeDollarSign, CalendarClock, MessageSquareText, PackageSearch, ShieldCheck } from "lucide-react"
import { DashboardCard } from "@/components/dashboard-card"
import { KpiRow } from "@/components/kpi-row"
import { ContractProvider } from "@/components/contract-drawer"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  computeMetrics,
  formatCurrency,
  getAssetInventory,
  getDepartmentSpend,
  getInactiveUsers,
} from "@/lib/seat-sweeper-data"

export const dynamic = "force-dynamic"

export default async function Home() {
  const [departments, inactiveUsers, inventory] = await Promise.all([
    getDepartmentSpend(),
    getInactiveUsers(),
    getAssetInventory(),
  ])
  const metrics = computeMetrics(departments, inactiveUsers, inventory)

  return (
    <ContractProvider>
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-8 sm:px-6 lg:px-8 lg:pt-4">
        <section className="overflow-hidden rounded-[2rem] bg-[#071f3a] text-white shadow-2xl shadow-slate-300/40 dark:shadow-black/30">
          <div className="grid gap-8 p-6 sm:p-8 lg:grid-cols-[1.45fr_0.55fr] lg:p-10">
            <div className="space-y-6">
              <Badge className="border-white/15 bg-white/10 text-sky-100 hover:bg-white/10">
                Finance, IT, and app engineering aligned
              </Badge>
              <div className="max-w-3xl space-y-3">
                <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl lg:text-6xl">
                  {formatCurrency(metrics.annualizedSavings)}
                </h1>
                <p className="text-lg font-medium text-sky-100 sm:text-xl">Annualized savings opportunity</p>
                <p className="max-w-2xl text-sm leading-6 text-slate-200 sm:text-base">
                  Seat Sweeper finds inactive SaaS seats, maps spend by department, and connects structured usage data to unstructured contract terms.
                </p>
              </div>
              <div className="flex flex-wrap gap-3">
                <Button asChild className="bg-sky-400 text-slate-950 hover:bg-sky-300">
                  <Link href="/licenses">
                    Review licenses
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline" className="border-white/30 bg-white/5 text-white hover:bg-white/10 hover:text-white">
                  <Link href="/ask">
                    Ask Seat Sweeper
                    <MessageSquareText className="h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </div>
            <div className="grid content-end gap-3">
              <div className="rounded-2xl bg-white/10 p-4 ring-1 ring-white/10">
                <p className="text-xs uppercase tracking-[0.18em] text-sky-100/70">Monthly waste</p>
                <p className="mt-2 text-3xl font-semibold">{formatCurrency(metrics.monthlyWaste)}</p>
              </div>
              <div className="rounded-2xl bg-white/10 p-4 ring-1 ring-white/10">
                <p className="text-xs uppercase tracking-[0.18em] text-sky-100/70">Annualized portfolio spend</p>
                <p className="mt-2 text-3xl font-semibold">{formatCurrency(metrics.annualizedSpend)}</p>
              </div>
            </div>
          </div>
        </section>

        <div className="flex flex-col gap-6">
          <KpiRow
            metrics={[
              {
                label: "Monthly Waste",
                value: formatCurrency(metrics.monthlyWaste),
                accent: "#e11d48",
              },
              {
                label: "Active Employees",
                value: metrics.employeeCount.toLocaleString(),
              },
              { label: "Active Assignments", value: metrics.assignmentCount.toLocaleString() },
              { label: "Tracked Assets", value: metrics.trackedAssets.toLocaleString() },
            ]}
          />
          <section className="overflow-hidden rounded-[1.75rem] border border-border bg-card shadow-sm">
            <div className="grid gap-6 p-5 lg:grid-cols-[0.82fr_1.18fr] lg:items-center lg:p-6">
              <div className="space-y-3">
                <Badge variant="secondary" className="w-fit">Reference architecture</Badge>
                <div className="space-y-2">
                  <h2 className="text-2xl font-semibold tracking-tight">Governed Data + AI app on Snowflake</h2>
                  <p className="text-sm leading-6 text-muted-foreground">
                    This diagram shows the completed facilitator reference. Your starter reads governed views and contract terms; agent functionality is demonstrated separately.
                  </p>
                </div>
              </div>
              <div className="overflow-hidden rounded-2xl border border-slate-200 bg-slate-950 shadow-lg dark:border-slate-800">
                <Image
                  src="/seat-sweeper-reference-architecture.png"
                  alt="SaaS Seat Sweeper governed Data and AI app reference architecture on Snowflake"
                  width={1600}
                  height={900}
                  className="h-auto w-full"
                  priority
                />
              </div>
            </div>
          </section>
          <div className="grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">
            <DashboardCard departments={departments} />
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Workflow Radar</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { href: "/licenses", icon: BadgeDollarSign, label: "License waste", value: `${metrics.inactiveCount} inactive paid assignments` },
                  { href: "/inventory", icon: PackageSearch, label: "Contract inventory", value: `${metrics.renewalRisks.length} auto-renewal risks surfaced` },
                  { href: "/ask", icon: MessageSquareText, label: "Ask your data", value: "Structured spend + contract terms" },
                ].map((item) => {
                  const Icon = item.icon
                  return (
                    <Link key={item.href} href={item.href} className="flex items-center justify-between rounded-2xl border border-border p-4 transition hover:border-sky-300 hover:bg-sky-50 dark:hover:bg-slate-900">
                      <div className="flex items-center gap-3">
                        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300">
                          <Icon className="h-5 w-5" />
                        </span>
                        <div>
                          <p className="text-sm font-semibold">{item.label}</p>
                          <p className="text-xs text-muted-foreground">{item.value}</p>
                        </div>
                      </div>
                      <ArrowRight className="h-4 w-4 text-muted-foreground" />
                    </Link>
                  )
                })}
              </CardContent>
            </Card>
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <CalendarClock className="h-5 w-5 text-sky-500" />
                  Renewal Watchlist
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {metrics.renewalRisks.map((item) => (
                  <Link key={item.asset_id} href="/inventory" className="flex items-center justify-between rounded-xl bg-muted/60 px-4 py-3 transition hover:bg-muted">
                    <div>
                      <p className="text-sm font-medium">{item.asset_name}</p>
                      <p className="text-xs text-muted-foreground">{item.vendor_name ?? "No vendor"}</p>
                    </div>
                    <Badge variant="secondary">{item.renewal_date ? new Date(item.renewal_date).toLocaleDateString() : "N/A"}</Badge>
                  </Link>
                ))}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <ShieldCheck className="h-5 w-5 text-emerald-500" />
                  App Runtime Story
                </CardTitle>
              </CardHeader>
              <CardContent className="grid gap-3 text-sm text-muted-foreground">
                <p>Deploy governed reads first, add write-back next, and observe the separate facilitator AI demonstration.</p>
                <p>This participant app needs no Ask credentials or agent objects.</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </ContractProvider>
  )
}
