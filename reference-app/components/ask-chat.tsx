"use client"

import { useState } from "react"
import { useAskChat, type AskMessage } from "@/components/use-ask-chat"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MessageSquareText, Send, Loader2, Brain, Code2, Quote, ChevronDown, Copy } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

const STARTER_QUESTIONS = [
  "Which department has the most inactive Figma licenses?",
  "What is the penalty for cancelling Datadog seats early?",
  "If I cancel all inactive Figma users today, will we be charged a true-up penalty?",
  "How are we doing?",
]

function copyToClipboard(text: string) {
  try {
    void navigator.clipboard?.writeText(text)
  } catch { /* clipboard not available */ }
}

function SqlBlock({ sql }: { sql: string }) {
  return (
    <div className="rounded-xl border border-border bg-slate-950/95 dark:bg-slate-950 overflow-hidden">
      <div className="flex items-center justify-between border-b border-slate-800 px-3 py-1.5">
        <span className="flex items-center gap-1.5 text-xs font-medium text-slate-300">
          <Code2 className="h-3 w-3" /> SQL
        </span>
        <button
          onClick={() => copyToClipboard(sql)}
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200"
          title="Copy SQL"
        >
          <Copy className="h-3 w-3" /> Copy
        </button>
      </div>
      <pre className="overflow-x-auto p-3 text-xs leading-relaxed text-slate-100">
        <code>{sql}</code>
      </pre>
    </div>
  )
}

function ThinkingBlock({ texts }: { texts: string[] }) {
  if (texts.length === 0) return null
  return (
    <details className="rounded-xl border border-border bg-muted/30">
      <summary className="flex cursor-pointer items-center gap-1.5 px-3 py-2 text-xs font-medium text-muted-foreground">
        <Brain className="h-3 w-3" />
        <span>Thinking ({texts.length})</span>
        <ChevronDown className="ml-auto h-3 w-3" />
      </summary>
      <div className="space-y-2 px-3 pb-3 text-xs italic text-muted-foreground">
        {texts.map((t, i) => (
          <p key={i} className="whitespace-pre-wrap">{t}</p>
        ))}
      </div>
    </details>
  )
}

function CitationsBlock({ citations }: { citations: AskMessage["citations"] }) {
  if (citations.length === 0) return null
  return (
    <div className="rounded-xl border border-border bg-muted/30 p-3">
      <p className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
        <Quote className="h-3 w-3" /> Citations
      </p>
      <ol className="space-y-1 text-xs text-muted-foreground">
        {citations.map((c, i) => (
          <li key={i} className="flex gap-1.5">
            <span className="font-mono text-slate-400">{i + 1}.</span>
            <span>
              {c.docTitle && <span className="font-medium">{c.docTitle}: </span>}
              {c.text}
            </span>
          </li>
        ))}
      </ol>
    </div>
  )
}

function AssistantMessage({ msg }: { msg: AskMessage }) {
  return (
    <div className="flex flex-col gap-3">
      {msg.status && msg.isStreaming && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Loader2 className="h-3 w-3 animate-spin" />
          <span>{msg.status}</span>
        </div>
      )}
      <ThinkingBlock texts={msg.thinkingTexts} />
      {msg.sqlQueries.map((q, i) => (
        <SqlBlock key={i} sql={q.sql} />
      ))}
      {msg.charts.length > 0 && (
        <div className="rounded-xl border border-border p-3">
          {msg.charts.length} chart(s) generated. (Vega rendering wired in build.)
        </div>
      )}
      {msg.text && (
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
        </div>
      )}
      {msg.isStreaming && msg.text && (
        <span className="ml-1 inline-block h-3 w-1.5 animate-pulse bg-current opacity-50" />
      )}
      {!msg.isStreaming && msg.text === "" && !msg.error && (
        <span className="text-xs text-muted-foreground">No response received.</span>
      )}
      {msg.error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-300">
          {msg.error}
        </div>
      )}
      <CitationsBlock citations={msg.citations} />
    </div>
  )
}

export function AskChat() {
  const { messages, isLoading, sendMessage, clearMessages } = useAskChat()
  const [input, setInput] = useState("")

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    const q = input
    setInput("")
    void sendMessage(q)
  }

  function handleStarter(question: string) {
    if (isLoading) return
    void sendMessage(question)
  }

  return (
    <Card className="flex flex-col" style={{ minHeight: "600px" }}>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2 text-xl">
          <MessageSquareText className="h-5 w-5 text-sky-500" />
          Ask Seat Sweeper
        </CardTitle>
        {messages.length > 0 && (
          <Button variant="ghost" size="sm" onClick={clearMessages} className="text-xs">
            Clear
          </Button>
        )}
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-4">
        {messages.length === 0 && (
          <div className="flex flex-1 flex-col items-center justify-center gap-4 rounded-2xl border border-dashed border-border p-8">
            <p className="text-center text-sm text-muted-foreground">
              Ask a question about SaaS license spend, inactive users, or contract terms.
              The agent uses Cortex Analyst for structured data and Cortex Search for unstructured contract text,
              streaming the answer with the generated SQL.
            </p>
            <div className="grid w-full gap-2 sm:grid-cols-2">
              {STARTER_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => handleStarter(q)}
                  className="rounded-xl border border-border p-3 text-left text-sm transition hover:border-sky-300 hover:bg-sky-50 dark:hover:bg-slate-900"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.length > 0 && (
          <div className="flex-1 space-y-4 overflow-y-auto">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "user" ? (
                  <div className="max-w-[85%] rounded-2xl bg-sky-400 px-4 py-3 text-sm text-slate-950">
                    <p className="whitespace-pre-wrap">{msg.text}</p>
                  </div>
                ) : (
                  <div className="max-w-[90%] rounded-2xl bg-muted px-4 py-3 text-sm">
                    <AssistantMessage msg={msg} />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about spend, inactive licenses, or contract terms..."
            disabled={isLoading}
            className="flex-1 rounded-xl border border-input bg-background px-4 py-2.5 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:opacity-50"
          />
          <Button type="submit" disabled={isLoading || !input.trim()} className="rounded-xl px-4">
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
