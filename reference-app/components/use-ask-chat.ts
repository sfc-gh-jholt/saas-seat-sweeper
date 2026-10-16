"use client"

import { useState, useCallback, useRef } from "react"

export interface SqlQuery {
  sql: string
  explanation?: string
}

export interface ChartContent {
  type: "vega-lite"
  spec: object
}

export interface Citation {
  type: string
  text: string
  docTitle?: string
  docId?: string
  index?: number
}

export interface AskMessage {
  id: string
  role: "user" | "assistant"
  text: string
  isStreaming: boolean
  status?: string
  thinkingTexts: string[]
  sqlQueries: SqlQuery[]
  charts: ChartContent[]
  citations: Citation[]
  error?: string
}

interface UseAskChatReturn {
  messages: AskMessage[]
  isLoading: boolean
  sendMessage: (question: string) => Promise<void>
  cancelRequest: () => void
  clearMessages: () => void
  threadId: number | null
  parentMessageId: number
}

function extractSqlFromToolResult(data: Record<string, unknown>): string | undefined {
  const delta = (data as { delta?: Record<string, unknown> }).delta
  if (delta && typeof delta === "object" && "sql" in delta) {
    const sql = (delta as { sql?: unknown }).sql
    if (typeof sql === "string") return sql
  }
  return undefined
}

/**
 * Hook that posts a question to /api/ask and parses the SSE stream into a rich
 * AskMessage. Falls back to a single JSON response (non-streaming) when the
 * route returns application/json (the DATA_AGENT_RUN fallback path).
 */
export function useAskChat(): UseAskChatReturn {
  const [messages, setMessages] = useState<AskMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [threadId, setThreadId] = useState<number | null>(null)
  const [parentMessageId, setParentMessageId] = useState<number>(0)
  const abortRef = useRef<AbortController | null>(null)

  const sendMessage = useCallback(
    async (question: string) => {
      if (!question.trim() || isLoading) return

      const baseId = Date.now().toString()
      const userMsg: AskMessage = {
        id: `${baseId}_user`,
        role: "user",
        text: question.trim(),
        isStreaming: false,
        thinkingTexts: [],
        sqlQueries: [],
        charts: [],
        citations: [],
      }
      const assistantId = `${baseId}_assistant`
      const assistantMsg: AskMessage = {
        id: assistantId,
        role: "assistant",
        text: "",
        isStreaming: true,
        status: "Thinking…",
        thinkingTexts: [],
        sqlQueries: [],
        charts: [],
        citations: [],
      }
      setMessages((prev) => [...prev, userMsg, assistantMsg])
      setIsLoading(true)

      const controller = new AbortController()
      abortRef.current = controller

      const updateAssistant = (patch: Partial<AskMessage>) => {
        setMessages((prev) =>
          prev.map((m) => (m.id === assistantId ? { ...m, ...patch } : m))
        )
      }

      try {
        const response = await fetch("/api/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            question: question.trim(),
            thread_id: threadId,
            parent_message_id: parentMessageId,
          }),
          signal: controller.signal,
        })

        if (!response.ok) {
          let errorMessage = `Request failed: ${response.status} ${response.statusText}`
          try {
            const errorData = await response.json()
            errorMessage = errorData.error || errorMessage
          } catch { /* keep default */ }
          updateAssistant({ isStreaming: false, status: undefined, error: errorMessage })
          return
        }

        const contentType = response.headers.get("content-type") ?? ""

        // --- Fallback path: non-streaming JSON (DATA_AGENT_RUN) ---
        if (contentType.includes("application/json")) {
          const data = await response.json()
          if (data.assistant_message_id) setParentMessageId(data.assistant_message_id)
          if (data.thread_id) setThreadId(data.thread_id)
          updateAssistant({
            text: data.text || "No response received.",
            isStreaming: false,
            status: undefined,
          })
          return
        }

        // --- Primary path: SSE stream (PAT + agent:run REST API) ---
        const reader = response.body?.getReader()
        if (!reader) {
          updateAssistant({ isStreaming: false, status: undefined, error: "No response stream" })
          return
        }

        const decoder = new TextDecoder()
        let buffer = ""
        let currentEvent = ""
        let assistantText = ""

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split("\n")
          buffer = lines.pop() ?? ""

          for (const line of lines) {
            if (line.startsWith("event: ")) {
              currentEvent = line.slice(7).trim()
            } else if (line.startsWith("data: ")) {
              const dataStr = line.slice(6).trim()
              if (!dataStr || dataStr === "[DONE]") continue
              let data: Record<string, unknown>
              try {
                data = JSON.parse(dataStr)
              } catch {
                continue
              }

              if (currentEvent === "response.text.delta") {
                const text = (data as { text?: string }).text ?? ""
                if (text) {
                  assistantText += text
                  updateAssistant({ text: assistantText })
                }
              } else if (currentEvent === "response.status") {
                const message = (data as { message?: string }).message
                if (message) updateAssistant({ status: message })
              } else if (currentEvent === "response.thinking") {
                const thinking = (data as { thinking?: { text?: string } }).thinking
                const text = thinking?.text?.trim()
                if (text) {
                  setMessages((prev) =>
                    prev.map((m) =>
                      m.id === assistantId
                        ? { ...m, thinkingTexts: [...m.thinkingTexts, text] }
                        : m
                    )
                  )
                }
              } else if (currentEvent === "response.thinking.delta") {
                const deltaText = (data as { text?: string }).text ?? ""
                if (deltaText) {
                  setMessages((prev) =>
                    prev.map((m) => {
                      if (m.id !== assistantId) return m
                      const current = m.thinkingTexts
                      const lastIndex = current.length - 1
                      if (lastIndex >= 0) {
                        const updated = [...current]
                        updated[lastIndex] = updated[lastIndex] + deltaText
                        return { ...m, thinkingTexts: updated }
                      }
                      return { ...m, thinkingTexts: [deltaText] }
                    })
                  )
                }
              } else if (currentEvent === "response.tool_result") {
                const sql = extractSqlFromToolResult(data)
                if (sql) {
                  setMessages((prev) =>
                    prev.map((m) =>
                      m.id === assistantId
                        ? { ...m, sqlQueries: [...m.sqlQueries, { sql }] }
                        : m
                    )
                  )
                }
              } else if (currentEvent === "response.chart") {
                const chartSpec = (data as { chart_spec?: string }).chart_spec
                if (chartSpec) {
                  try {
                    const spec = JSON.parse(chartSpec)
                    setMessages((prev) =>
                      prev.map((m) =>
                        m.id === assistantId
                          ? { ...m, charts: [...m.charts, { type: "vega-lite", spec }] }
                          : m
                      )
                    )
                  } catch { /* skip malformed chart */ }
                }
              } else if (currentEvent === "response.text.annotation") {
                const annotation = (data as { annotation?: Record<string, unknown> }).annotation ?? data
                const text = (annotation as { text?: string }).text
                const docTitle = (annotation as { doc_title?: string }).doc_title
                const docId = (annotation as { doc_id?: string }).doc_id
                const index = (annotation as { index?: number }).index
                if (text) {
                  setMessages((prev) =>
                    prev.map((m) =>
                      m.id === assistantId
                        ? {
                            ...m,
                            citations: [
                              ...m.citations,
                              { type: "cortex_search_citation", text, docTitle, docId, index },
                            ],
                          }
                        : m
                    )
                  )
                }
              } else if (currentEvent === "metadata") {
                const meta = (data as { metadata?: { role?: string; message_id?: number; thread_id?: number } }).metadata
                if (meta?.message_id && meta.role === "assistant") {
                  setParentMessageId(meta.message_id)
                }
                if (meta?.thread_id) setThreadId(meta.thread_id)
              } else if (currentEvent === "done") {
                const meta = (data as { assistant_message_id?: number; thread_id?: number })
                if (meta.assistant_message_id) setParentMessageId(meta.assistant_message_id)
                if (meta.thread_id) setThreadId(meta.thread_id)
              } else if (currentEvent === "response") {
                const meta = (data as { metadata?: { assistant_message_id?: number; thread_id?: number } }).metadata
                if (meta?.assistant_message_id) setParentMessageId(meta.assistant_message_id)
                if (meta?.thread_id) setThreadId(meta.thread_id)
              } else if (currentEvent === "error") {
                const errMsg = (data as { message?: string }).message ?? "Agent error"
                updateAssistant({ isStreaming: false, status: undefined, error: errMsg })
              }
            }
          }
        }

        updateAssistant({ isStreaming: false, status: undefined })
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          updateAssistant({ isStreaming: false, status: undefined, text: assistantTextPlaceholder() })
        } else {
          const message = err instanceof Error ? err.message : String(err)
          updateAssistant({ isStreaming: false, status: undefined, error: message })
        }
      } finally {
        setIsLoading(false)
        abortRef.current = null
      }
    },
    [isLoading, threadId, parentMessageId]
  )

  const cancelRequest = useCallback(() => {
    if (abortRef.current && isLoading) {
      abortRef.current.abort()
    }
  }, [isLoading])

  const clearMessages = useCallback(() => {
    if (abortRef.current && isLoading) {
      abortRef.current.abort()
    }
    setMessages([])
    setIsLoading(false)
    setThreadId(null)
    setParentMessageId(0)
    abortRef.current = null
  }, [isLoading])

  return { messages, isLoading, sendMessage, cancelRequest, clearMessages, threadId, parentMessageId }
}

function assistantTextPlaceholder(): string {
  return ""
}
