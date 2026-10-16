"use client"

import { createContext, useCallback, useContext, useEffect, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { X } from "lucide-react"

interface ContractDetail {
  asset_id: number
  asset_name: string
  contract_id: number | null
  vendor_name: string | null
  renewal_date: string | null
  auto_renew: boolean | null
  contract_terms_text: string | null
}

interface ContractContextValue {
  openContract: (assetId: number) => void
}

const ContractContext = createContext<ContractContextValue | null>(null)

export function useContractDrawer(): ContractContextValue {
  const ctx = useContext(ContractContext)
  if (!ctx) throw new Error("useContractDrawer must be used within a ContractProvider")
  return ctx
}

export function ContractProvider({ children }: { children: React.ReactNode }) {
  const [assetId, setAssetId] = useState<number | null>(null)
  const [detail, setDetail] = useState<ContractDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const openContract = useCallback((id: number) => {
    setAssetId(id)
  }, [])

  const close = useCallback(() => setAssetId(null), [])

  useEffect(() => {
    if (assetId === null) return
    setLoading(true)
    setError(null)
    setDetail(null)
    fetch(`/api/contract/${assetId}`)
      .then(async (res) => {
        if (!res.ok) throw new Error((await res.json()).error || "Failed to load contract")
        return res.json()
      })
      .then((data) => setDetail(data))
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false))
  }, [assetId])

  const isOpen = assetId !== null

  return (
    <ContractContext.Provider value={{ openContract }}>
      {children}

      {/* Overlay */}
      <div
        aria-hidden={!isOpen}
        onClick={close}
        className={`fixed inset-0 z-40 bg-black/40 transition-opacity duration-200 ${
          isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        }`}
      />

      {/* Drawer */}
      <div
        role="dialog"
        aria-modal="true"
        aria-hidden={!isOpen}
        className={`fixed inset-y-0 right-0 z-50 w-full sm:w-[420px] bg-card border-l border-border shadow-2xl transition-transform duration-200 overflow-y-auto ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex items-start justify-between p-5 border-b border-border">
          <div>
            <h3 className="text-lg font-semibold">{detail?.asset_name ?? "Contract Terms"}</h3>
            <p className="text-sm text-muted-foreground mt-0.5">
              {detail?.vendor_name ? `Vendor: ${detail.vendor_name}` : "Unstructured contract terms"}
            </p>
          </div>
          <button
            onClick={close}
            aria-label="Close"
            className="rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {loading && (
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          )}
          {error && <p className="text-sm text-red-500">{error}</p>}
          {detail && !loading && (
            <>
              <div className="flex flex-wrap gap-2">
                {detail.renewal_date && (
                  <Badge variant="secondary">
                    Renews {new Date(detail.renewal_date).toLocaleDateString()}
                  </Badge>
                )}
                {detail.auto_renew !== null && (
                  <Badge variant={detail.auto_renew ? "default" : "secondary"}>
                    {detail.auto_renew ? "Auto-renews" : "No auto-renew"}
                  </Badge>
                )}
                {!detail.contract_id && <Badge variant="outline">No contract on file</Badge>}
              </div>
              {detail.contract_terms_text ? (
                <p className="text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap">
                  {detail.contract_terms_text}
                </p>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No unstructured contract terms recorded for this asset (likely a free tool or internal
                  hardware pool with no enterprise agreement).
                </p>
              )}
            </>
          )}
        </div>
      </div>
    </ContractContext.Provider>
  )
}
