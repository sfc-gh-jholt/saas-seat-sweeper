# 09 - Ask the same business question

Use CoCo to critique the evidence from a runtime business-question agent, keeping the two assistants' roles and identities distinct.

**Time limit:** 10 minutes, 02:30-02:40. Use 2 minutes for setup/identity, 2 each for three questions, and 2 for evidence review.

## Action

Observe the facilitator's separately prepared Cortex Agent at the supplied demo account/URL; no fixed destination is in this package. CoCo is your development/operator assistant, not that runtime agent. The participant Ask landing page does not mean you built AI objects or mounted credentials.

The facilitator identifies the semantic view, contract-text Search service and agent, then asks:

1. Structured: "Which department has the most inactive Figma licenses?" Check SQL and people-versus-assignments counting.
2. Contract text: "What does the Datadog contract say about cancelling seats early?" Check passage and citation when returned.
3. Combined: "How many inactive Figma assignments could we review, and what contract terms should we check before cancelling them?" Separate SQL result, retrieved clause and interpretation.

[Prompt CoCo: Critique the agent outputs without inventing evidence](../coco-prompts/review-agent-demo.md)

## Your decision

Supply only redacted observed outputs. Decide which conclusions the actual SQL/citations support; mark missing evidence rather than accepting a plausible answer. Tool routing, responses, latency and clarification behavior can vary. Contracts are synthetic, not legal advice.

The reference REST route uses a mounted PAT principal/role, not visitor identity; its fallback requires a service token. Ordinary credential-free local development does not automatically enable Ask. Never copy PATs into source, downloads or browser requests. No agent construction or authentication/network relaxation in this slot.

## Expected evidence

Record one structured result and its SQL, one supporting contract passage/citation if returned, and the distinction between browser, SQL service and agent credential identities. Mark this **observed**, not participant-built. CoCo's critique is not additional proof of a tool call you did not see.

## Recovery

If the first live question cannot finish by minute 154, use rehearsal outputs labeled with capture date/account. Record the known failure and missing proof; do not rotate credentials or rebuild services. End at minute 160.

## Checklist

- [ ] Three question types observed or labeled as captured fallbacks.
- [ ] Returned SQL/citations inspected; gaps retained.
- [ ] CoCo and the runtime agent's purposes/identities distinguished.
- [ ] No deterministic-answer or per-visitor AI authorization claim.

Next: [Compare your actual stack](10-scorecard.md).
