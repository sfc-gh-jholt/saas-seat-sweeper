"use client"

import Image from "next/image"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { APP_TITLE, LOGO_SRC } from "@/lib/constants"
import { ThemeToggle } from "@/components/theme-toggle"
import { cn } from "@/lib/utils"
import { BadgeDollarSign, LayoutDashboard, MessageSquareText, PackageSearch } from "lucide-react"

const navItems = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/licenses", label: "Licenses", icon: BadgeDollarSign },
  { href: "/inventory", label: "Inventory", icon: PackageSearch },
  { href: "/ask", label: "Ask", icon: MessageSquareText },
]

export function AppHeader({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 dark:bg-slate-950 dark:text-slate-50">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-72 flex-col border-r border-white/10 bg-[#071f3a] text-white shadow-2xl lg:flex">
        <div className="flex h-20 items-center gap-3 border-b border-white/10 px-6">
          {LOGO_SRC && (
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10 ring-1 ring-white/15">
              <Image src={LOGO_SRC} alt={`${APP_TITLE} logo`} width={26} height={26} />
            </div>
          )}
          <div>
            <p className="text-sm font-semibold tracking-tight">{APP_TITLE}</p>
            <p className="text-xs text-sky-100/70">Spend command center</p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-4 py-5">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href)
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition",
                  active
                    ? "bg-sky-400 text-slate-950 shadow-lg shadow-sky-950/20"
                    : "text-sky-50/75 hover:bg-white/10 hover:text-white"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            )
          })}
        </nav>

        <div className="border-t border-white/10 p-4">
          <div className="rounded-2xl bg-white/10 p-4 ring-1 ring-white/10">
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-sky-100/70">Workshop Mode</p>
            <p className="mt-2 text-sm leading-5 text-white/90">Reference implementation for app, prompt, and lab parity.</p>
          </div>
        </div>
      </aside>

      <header className="sticky top-0 z-30 border-b border-border bg-background/95 backdrop-blur lg:hidden">
        <div className="flex h-14 items-center gap-3 px-4">
          {LOGO_SRC && <Image src={LOGO_SRC} alt={`${APP_TITLE} logo`} width={28} height={28} />}
          <span className="text-sm font-semibold tracking-tight">{APP_TITLE}</span>
          <div className="ml-auto">
            <ThemeToggle />
          </div>
        </div>
        <nav className="flex gap-1 overflow-x-auto px-3 pb-3">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href)
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex shrink-0 items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium",
                  active ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                )}
              >
                <Icon className="h-3.5 w-3.5" />
                {item.label}
              </Link>
            )
          })}
        </nav>
      </header>

      <main className="lg:pl-72">
        <div className="hidden justify-end px-8 pt-6 lg:flex">
          <ThemeToggle />
        </div>
        {children}
      </main>
    </div>
  )
}
