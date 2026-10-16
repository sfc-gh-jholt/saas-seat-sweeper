# 09 - Ask the same business question

Watch an agent answer questions about licenses and contracts, then check what supports its answers.

**Time limit:** 10 minutes, 02:30-02:40. Use 2 minutes for setup/identity, 2 each for three questions, and 2 for evidence review.

## Action

The facilitator will open a separately prepared Cortex Agent. You don't need to create an agent or add credentials to your app. CoCo helps you build software; this agent answers business questions.

The facilitator identifies the semantic view, contract-text Search service and agent, then asks:

1. Structured: "Which department has the most inactive Figma licenses?" Check SQL and people-versus-assignments counting.
2. Contract text: "What does the Datadog contract say about cancelling seats early?" Check passage and citation when returned.
3. Combined: "How many inactive Figma assignments could we review, and what contract terms should we check before cancelling them?" Separate SQL result, retrieved clause and interpretation.

[Prompt CoCo: Help me check these agent answers](../coco-prompts/review-agent-demo.md)

## Your decision

Give CoCo the demo outputs without secrets. Look for SQL behind the numbers and a contract passage behind the contract answer. If either is missing, say so. Responses can vary, and these sample contracts are not legal advice.

The reference REST route uses a mounted PAT principal/role, not visitor identity; its fallback requires a service token. Ordinary credential-free local development does not automatically enable Ask. Never copy PATs into source, downloads or browser requests. No agent construction or authentication/network relaxation in this slot.

## Expected evidence

Note one SQL-backed answer, one contract citation if shown, and one unanswered question. Mark this as a facilitator demo, not something you built.

## Why this matters

The reference agent uses its configured credential identity, not automatically the browser visitor. Never copy its token into a prompt or your source files. The [FAQ](12-honest-faq.md) explains the identity differences.

## Recovery

If the first live question cannot finish by minute 154, use rehearsal outputs labeled with capture date/account. Record the known failure and missing proof; do not rotate credentials or rebuild services. End at minute 160.

## Checklist

- [ ] Three question types observed or labeled as captured fallbacks.
- [ ] Returned SQL/citations inspected; gaps retained.
- [ ] CoCo and the runtime agent's purposes/identities distinguished.
- [ ] No deterministic-answer or per-visitor AI authorization claim.

Next: [Compare your actual stack](10-scorecard.md).
