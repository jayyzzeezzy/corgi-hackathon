import type { GraphData } from '../types/graph'

const API_URL = '/pipeshift-api/api/v0/chat/completions'
const MODEL = 'deepseek-ai/DeepSeek-R1'

const PARSE_SYSTEM_PROMPT = `You are a code architecture analyzer. Given source code, extract its structure and data flows as JSON.
Return ONLY valid JSON — no markdown, no explanation, no code fences.

Schema:
{
  "nodes": [
    { "id": "string", "label": "string", "type": "component|function|class|hook|util", "description": "string" }
  ],
  "edges": [
    { "source": "string", "target": "string", "relationship": "imports|calls|extends|uses" }
  ],
  "dataFlows": [
    {
      "id": "string",
      "label": "string",
      "origin": "string",
      "type": "user_input|api_call|db_read|prop|state",
      "path": ["string"],
      "description": "string"
    }
  ]
}

Rules:
- node id must be unique and camelCase, matching the label exactly
- Only include named, meaningful entities — skip anonymous helpers
- Infer edges from imports, function calls, and class inheritance
- For dataFlows: identify key data flows. A data flow starts at an origin point (user input, API call, db read, prop, or state) and traces the exact path that data takes through components or functions until it reaches its final consumer.
- Identify all key data flows in the code. A data flow starts at an origin point (user input, API call, db read, prop, state) and traces the exact path that data takes through components or functions until it reaches its final consumer. Only trace flows you are confident about. Return each flow with an ordered array of node IDs it passes through. Node IDs must exactly match the node IDs in the nodes array.
- Focus data flow detection on: useState/useReducer declarations, useEffect with dependencies, props passed between components, fetch()/axios calls, direct function calls that pass data
- path must contain ordered node IDs that exactly match those in the nodes array
- Return empty arrays if nothing applicable is found`

const EXPLAIN_SYSTEM_PROMPT = `You are a senior engineer explaining code to a smart non-expert. Given a component name and its one-line description, write 3-5 sentences explaining: what it does, why it exists, and what depends on it. Be concrete, not generic. Flowing prose only — no bullet points, no headers.`

async function callAPI(messages: { role: string; content: string }[]): Promise<string> {
  const apiKey = import.meta.env.VITE_PIPESHIFT_API_KEY
  if (!apiKey) throw new Error('VITE_PIPESHIFT_API_KEY is not set')

  const res = await fetch(API_URL, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ model: MODEL, messages, temperature: 0.2, stream: false, max_tokens: 8000 }),
  })

  if (!res.ok) {
    const body = await res.text()
    throw new Error(`Pipeshift API error ${res.status}: ${body}`)
  }

  const data = await res.json()
  const choice = data.choices[0]
  if (choice.finish_reason === 'length') throw new Error('Model hit token limit — try a shorter file')
  const content = choice.message.content ?? choice.message.reasoning_content ?? ''
  if (!content) throw new Error('Empty response from Pipeshift API')
  return content as string
}

export async function parseCode(code: string): Promise<GraphData> {
  const content = await callAPI([
    { role: 'system', content: PARSE_SYSTEM_PROMPT },
    { role: 'user', content: `Analyze this code:\n\n${code}` },
  ])

  // Strip markdown fences if the model wraps the JSON anyway
  const cleaned = content.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '').trim()
  const parsed = JSON.parse(cleaned) as GraphData

  // Normalize — ensure dataFlows exists
  if (!parsed.dataFlows) parsed.dataFlows = []
  return parsed
}

export async function explainNode(label: string, description: string): Promise<string> {
  return callAPI([
    { role: 'system', content: EXPLAIN_SYSTEM_PROMPT },
    { role: 'user', content: `Component: ${label}\nDescription: ${description}` },
  ])
}
