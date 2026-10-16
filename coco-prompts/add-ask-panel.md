# CoCo Prompt: Wire the Ask Route to Cortex Agent

Use this prompt in CoCo to wire the existing `/ask` route to the Cortex Agent. The workshop itself keeps this facilitator-led — the reference app ships with the wiring already done. This prompt is for rebuilding it on your own account afterward.

## Prerequisite

This is optional take-home work, not a participant prerequisite. Follow `admin-preflight.md` and the separately reviewed AI setup path to prepare:

1. A semantic view over the `SAAS_SEAT_SWEEPER` schema
2. A Cortex Search service over contract terms text
3. A Cortex Agent with both Cortex Analyst and Cortex Search as tools

The agent should be named `SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_AGENT`.

Review `sql/05_ai_objects.sql` before running it in an isolated target. Its setup and replacement behavior must not be used indiscriminately against existing objects.

## Prompt

```text
Wire the existing /ask route in this Seat Sweeper app to the Cortex Agent named SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_AGENT with SSE streaming and rich content widgets.

The /ask route should:

1. Accept a user question in a text input.
2. Call the agent from a Next.js Route Handler (app/api/ask/route.ts) via the Cortex Agent REST API:
   POST https://{host}/api/v2/databases/SAAS_SEAT_SWEEPER/schemas/APP/agents/SEAT_SWEEPER_AGENT:run
   with headers:
     Authorization: Bearer <PAT>
     X-Snowflake-Authorization-Token-Type: PROGRAMMATIC_ACCESS_TOKEN
     Accept: text/event-stream
   and body: { messages: [{role:"user", content:[{type:"text", text: question}]}], stream: true, thread_id?, parent_message_id? }
   Read the PAT from /secrets/SEAT_SWEEPER_PAT/secret_string (mounted via the app.yml secrets block from a Snowflake generic-string secret).
3. Pipe the raw SSE byte stream through to the client; do NOT parse it server-side. The client hook parses the events.
4. If the PAT secret is missing, the reference fallback requires a Snowflake runtime service token. Ordinary local TOML credentials do not make that fallback work. If neither supported credential is available, show a clear configuration error; do not weaken authentication policies or silently invent an answer.
5. Client hook (components/use-ask-chat.ts): parse each SSE event type and build a rich message model:
   - response.text.delta → append to the answer text (streamed, token-by-token)
   - response.status → show a status line ("Executing SQL…", "Analyzing data…") with a spinner while streaming
   - response.thinking / response.thinking.delta → collect thinking steps into a collapsed <details> block
   - response.tool_result → if the result content includes a `sql` field, render it in a ```sql block with a copy button
   - response.chart → collect chart specs (render with react-vega if charts appear)
   - response.text.annotation → collect citations into a footer list with the doc title and text
   - metadata / done / response → capture thread_id and assistant_message_id for multi-turn follow-ups
6. Render the answer text with react-markdown + remark-gfm so the agent's markdown (lists, bold, code) renders.
7. If the agent returns clarifying suggestions instead of an answer (ambiguous question), the suggestions render as the markdown text — no special handling needed.
8. Thread the conversation: pass thread_id and parent_message_id from the prior response into follow-up requests.
9. Preserve the existing curated starter questions on the /ask route:
   - Which department has the most inactive Figma licenses?
   - What is the penalty for cancelling Datadog seats early?
   - If I cancel all inactive Figma users today, will we be charged a true-up penalty?
   - How are we doing?

Keep Snowflake row handling consistent with the rest of the app: in the DATA_AGENT_RUN fallback path, normalize querySnowflakeLongRunning() rows with lowercaseKeys() or equivalent before reading column values (the REST/SSE path does not use querySnowflake).
```

## Notes for facilitators

- Prepare and test the semantic view, search service, agent, approved credential, and secret before the facilitator demonstration. Review `sql/05_ai_objects.sql` and `sql/06_ask_pat_secret.sql` with the administrator. Never put secret values into source, logs, prompts, or the participant package.
- The route already exists in the premium app structure. The task is to wire `/ask`, not create a disconnected chat panel elsewhere.
- **Reference credential choice.** This reference sends a mounted PAT to the REST API and uses the runtime service token for its SQL fallback. Past testing rejected the runtime token on the REST path; that observation is not a claim that PAT is the only authentication method supported by the product. Revalidate the selected method in the target account.
- **Network policy boundary.** A credential may be rejected by network policy even when it is valid. Have the security administrator establish an approved path; do not disable policy evaluation to rescue a demonstration. Use prepared evidence or omit the live Ask call if the approved path is unavailable.
- **Cortex Search grant.** The PAT's role (SAAS_SWEEPER_MANAGER) needs `USAGE` on the Cortex Search service or the agent returns `399502`. `sql/06_ask_pat_secret.sql` includes the grant.
- `DATA_AGENT_RUN` is the fallback path (non-streaming, single JSON). The SSE/REST path is primary because it gives token-by-token streaming and the rich event model (thinking, SQL, charts, citations).
- Tool event names can change. Verify the actual event stream and rendered SQL/citations during the facilitator rehearsal rather than relying on an old event name.
- Demonstrate a structured question, a contract-text question, and a combined question. Inspect generated SQL and citations when supplied. Ambiguity handling is an evaluation exercise, not a guaranteed output.
- The agent's credential identity is separate from the visitor identity. A fixed facilitator PAT does not demonstrate per-visitor filtering. Evaluate tool permissions, retrieval scope, answer quality, and prompt-injection exposure separately.