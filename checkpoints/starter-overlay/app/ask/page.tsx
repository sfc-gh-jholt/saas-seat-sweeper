import Link from "next/link"

export default function AskPage() {
  return <section className="mx-auto max-w-3xl space-y-4 px-6 py-8">
    <p className="text-sm font-medium uppercase tracking-wide text-muted-foreground">Facilitator demonstration</p>
    <h1 className="text-3xl font-semibold">Ask Seat Sweeper</h1>
    <p>The facilitator demonstrates structured spend questions and contract-text retrieval in the completed reference app.</p>
    <p>This participant app has no agent endpoint and needs no Ask PAT secret or AI objects. Adding write-back does not enable Ask.</p>
    <p>The reference demo uses a separately prepared service or PAT identity, not automatic per-visitor authorization.</p>
    <Link className="underline" href="/inventory">Inspect contract terms in Inventory</Link>
  </section>
}