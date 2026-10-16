import type { Metadata } from "next"
import type React from "react"
import { AppHeader } from "@/components/app-header"
import { ThemeProvider } from "@/components/theme-provider"
import { QueryProvider } from "@/components/query-provider"
import { APP_TITLE, LOGO_SRC } from "@/lib/constants"
import "./globals.css"

export const metadata: Metadata = {
  title: APP_TITLE,
  description: "A premium internal app for SaaS license waste, asset inventory, and contract intelligence.",
  icons: { icon: LOGO_SRC },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased">
        <ThemeProvider>
          <QueryProvider>
            <AppHeader>
              <p role="note" className="mx-4 mt-3 rounded-lg border border-border p-3 text-sm text-muted-foreground">
                Workshop diagnosis fixture: data-read failures currently appear as empty data. If totals unexpectedly show zero, verify the connection and grants; zero is not proof of no spend.
              </p>
              {children}
            </AppHeader>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
