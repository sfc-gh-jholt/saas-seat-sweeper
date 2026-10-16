import { NextRequest } from "next/server"
import fs from "fs"
import { getServiceToken, querySnowflakeLongRunning } from "@/lib/snowflake"

export const dynamic = "force-dynamic"
export const runtime = "nodejs"

const AGENT_DATABASE = "SAAS_SEAT_SWEEPER"
const AGENT_SCHEMA = "APP"
const AGENT_NAME = "SEAT_SWEEPER_AGENT"
const AGENT_FQN = `${AGENT_DATABASE}.${AGENT_SCHEMA}.${AGENT_NAME}`

const PAT_SECRET_PATH = "/secrets/SEAT_SWEEPER_PAT/secret_string"

function getAccountHost(): string {
  if (process.env.SNOWFLAKE_ACCOUNT_URL) {
    return process.env.SNOWFLAKE_ACCOUNT_URL.replace(/^https?:\/\//, "")
  }
  if (process.env.SNOWFLAKE_HOST) {
    return process.env.SNOWFLAKE_HOST
  }
  throw new Error("SNOWFLAKE_ACCOUNT_URL or SNOWFLAKE_HOST not set")
}

function readPat(): string {
  try {
    return fs.readFileSync(PAT_SECRET_PATH, "utf8").trim()
  } catch {
    return ""
  }
}

interface FallbackContentItem {
  type: string
  text?: string
  tool_use?: { name?: string; input?: Record<string, unknown> }
  tool_result?: { name?: string; content?: Array<{ type: string; json?: { sql?: string }; text?: string }> }
}
interface FallbackResponse {
  content?: FallbackContentItem[]
  metadata?: { assistant_message_id?: number; thread_id?: number }
}

function extractFallbackText(resp: FallbackResponse): string {
  const parts: string[] = []
  for (const item of resp.content ?? []) {
    if (item.type === "text" && item.text) parts.push(item.text)
    else if (item.type === "tool_use" && item.tool_use?.name) {
      parts.push(`\n\n[Calling tool: ${item.tool_use.name}]`)
    } else if (item.type === "tool_result" && item.tool_result) {
      const sqlMatch = item.tool_result.content?.find((c) => c.json?.sql)
      if (sqlMatch?.json?.sql) {
        parts.push(`\n\n**SQL:**\n\`\`\`sql\n${sqlMatch.json.sql}\n\`\`\``)
      }
    }
  }
  return parts.join("").trim() || "No response received."
}

/**
 * Fallback when the PAT secret is not mounted (e.g. local dev without the secret).
 * Uses the SPCS OAuth token via the SQL function DATA_AGENT_RUN — non-streaming,
 * flat text — so the route still works without a PAT.
 */
async function fallbackDataAgentRun(
  question: string,
  threadId: number | null,
  parentMessageId: number
): Promise<Response> {
  const serviceToken = getServiceToken()
  if (!serviceToken) {
    return new Response(
      JSON.stringify({ error: "No PAT secret and no SPCS service token. Deploy to SPCS or mount the PAT secret." }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    )
  }

  const requestBody: Record<string, unknown> = {
    messages: [{ role: "user", content: [{ type: "text", text: question }] }],
  }
  if (threadId) {
    requestBody.thread_id = threadId
    requestBody.parent_message_id = parentMessageId
  }

  const bodyJson = JSON.stringify(requestBody).replace(/'/g, "''")
  const sql = `SELECT SNOWFLAKE.CORTEX.DATA_AGENT_RUN('${AGENT_FQN}', '${bodyJson}') AS resp`

  const rows = await querySnowflakeLongRunning(sql, {
    maxWaitMs: 120_000,
    pollIntervalMs: 2000,
    statusLogIntervalMs: 15_000,
  })

  if (!rows || rows.length === 0) {
    return new Response(JSON.stringify({ error: "Agent returned no rows" }), {
      status: 502, headers: { "Content-Type": "application/json" },
    })
  }

  let parsed: FallbackResponse
  try {
    parsed = JSON.parse(rows[0].RESP as string)
  } catch {
    return new Response(JSON.stringify({ error: "Failed to parse agent response" }), {
      status: 502, headers: { "Content-Type": "application/json" },
    })
  }

  return new Response(
    JSON.stringify({
      text: extractFallbackText(parsed),
      assistant_message_id: parsed.metadata?.assistant_message_id ?? null,
      thread_id: parsed.metadata?.thread_id ?? null,
      streamed: false,
    }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  )
}

export async function POST(request: NextRequest) {
  let body: { question?: string; thread_id?: number; parent_message_id?: number }
  try {
    body = await request.json()
  } catch {
    return new Response(JSON.stringify({ error: "invalid JSON body" }), {
      status: 400, headers: { "Content-Type": "application/json" },
    })
  }

  const { question, thread_id, parent_message_id } = body
  if (!question || typeof question !== "string") {
    return new Response(JSON.stringify({ error: "question is required" }), {
      status: 400, headers: { "Content-Type": "application/json" },
    })
  }

  const pat = readPat()
  if (!pat) {
    return fallbackDataAgentRun(question, thread_id ?? null, parent_message_id ?? 0)
  }

  const host = getAccountHost()
  const url = `https://${host}/api/v2/databases/${AGENT_DATABASE}/schemas/${AGENT_SCHEMA}/agents/${AGENT_NAME}:run`

  const payload: Record<string, unknown> = {
    messages: [{ role: "user", content: [{ type: "text", text: question }] }],
    stream: true,
  }
  if (thread_id) {
    payload.thread_id = thread_id
    payload.parent_message_id = parent_message_id ?? 0
  }

  let agentResponse: Response
  try {
    agentResponse = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${pat}`,
        "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify(payload),
    })
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    return new Response(JSON.stringify({ error: `Failed to reach agent: ${message}` }), {
      status: 502, headers: { "Content-Type": "application/json" },
    })
  }

  if (!agentResponse.ok) {
    const errorText = await agentResponse.text()
    return new Response(
      JSON.stringify({ error: `Agent returned ${agentResponse.status}: ${errorText.slice(0, 500)}` }),
      { status: 502, headers: { "Content-Type": "application/json" } }
    )
  }

  if (!agentResponse.body) {
    return new Response(JSON.stringify({ error: "Agent returned no response body" }), {
      status: 502, headers: { "Content-Type": "application/json" },
    })
  }

  // Pipe the raw SSE byte stream through to the client. The client hook parses
  // response.text.delta / response.thinking.delta / response.tool_result /
  // response.chart / response.text.annotation / response.status events.
  const upstream = agentResponse.body
  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const reader = upstream.getReader()
      const pump = async (): Promise<void> => {
        try {
          while (true) {
            const { done, value } = await reader.read()
            if (done) {
              controller.close()
              return
            }
            if (value) {
              controller.enqueue(value)
              // Backpressure: ReadableStream's default queue handles this;
              // for tighter control we could check desiredSize but Next.js
              // runtime buffers acceptably for this use case.
            }
          }
        } catch (err) {
          controller.error(err)
        }
      }
      // Cancel the upstream read if the client disconnects.
      request.signal.addEventListener("abort", () => {
        try { reader.cancel() } catch { /* already closed */ }
      })
      await pump()
    },
    cancel() {
      try { upstream.cancel() } catch { /* already closed */ }
    },
  })

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  })
}
