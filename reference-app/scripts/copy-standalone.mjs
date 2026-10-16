import { cpSync } from "node:fs"

// Next standalone tracing does not copy static assets automatically.
cpSync("public", ".next/standalone/public", { recursive: true })
cpSync(".next/static", ".next/standalone/.next/static", { recursive: true })