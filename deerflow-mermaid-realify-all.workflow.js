export const meta = {
  name: 'deerflow-mermaid-realify-all',
  description: 'Design source-backed Mermaid replacements for the fake generic tail diagram in all 69 DeerFlow docs; review; return for local+remote apply.',
  phases: [
    { title: 'Design', detail: 'one agent per doc reads doc + source, emits source-backed mermaid' },
    { title: 'Review', detail: 'batch reviewer rejects any still-generic / non-source-backed diagram' },
  ],
}

// Each item: { file, token, block_id }. The doc filename is the only thing the
// agent strictly needs; token/block_id are carried through so the main loop can
// apply directly without re-joining.
// Robustly coerce args into an array. args may arrive as a real array OR as a
// JSON-encoded string (depending on how the harness passes it) — normalize both.
let items = Array.isArray(args) ? args
  : (typeof args === 'string' && args.trim().startsWith('[')) ? (() => { try { return JSON.parse(args) } catch { return [] } })()
  : (args && typeof args === 'object' && Array.isArray(args.items)) ? args.items
  : []
if (!Array.isArray(items) || items.length === 0) items = []

const MermaidSchema = {
  type: 'object',
  additionalProperties: false,
  properties: {
    file: { type: 'string', description: 'the doc filename, echoed back' },
    found_fake: { type: 'boolean', description: 'true if the fake template block was located at the doc tail' },
    replacement_mermaid: {
      type: 'string',
      description: 'Complete Mermaid source ONLY (no fences). Must be specific to this doc+code, source-backed.',
    },
    diagram_kind: { type: 'string', description: 'flowchart TD | flowchart LR | sequenceDiagram | stateDiagram-v2' },
    evidence_paths: {
      type: 'array',
      items: { type: 'string' },
      description: 'repo-relative source paths actually inspected to build the diagram',
    },
    one_line_summary: { type: 'string', description: 'one sentence: what real flow this diagram depicts' },
    risks: { type: 'array', items: { type: 'string' }, description: 'uncertainties or unverifiable claims, if any' },
  },
  required: ['file', 'found_fake', 'replacement_mermaid', 'diagram_kind', 'evidence_paths', 'one_line_summary', 'risks'],
}

const ReviewSchema = {
  type: 'object',
  additionalProperties: false,
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          file: { type: 'string' },
          approve: { type: 'boolean' },
          reason: { type: 'string' },
        },
        required: ['file', 'approve', 'reason'],
      },
    },
  },
  required: ['verdicts'],
}

phase('Design')
const results = await pipeline(
  items,
  (item) => agent(`
You are fixing ONE DeerFlow documentation diagram by replacing a fake generic placeholder with a real, source-backed diagram.

Repo cwd: /Users/bytedance/deer-flow
Doc title: ${item.file}
Remote Lark doc token: ${item.token}

IMPORTANT — the LOCAL markdown copies of these docs are POLLUTED/out of sync. Do NOT read local .md files for this doc's content. Read the REMOTE doc via lark-cli instead.

TASK:
1. Fetch the remote doc content (XML) by running:
   lark-cli docs +fetch --doc "${item.token}"
   This returns the doc as XML. Read it to understand what THIS module/subsystem explains. (lark-cli is already authenticated.)
2. The doc ends with a section whose title contains "设计取舍、重点代码与阅读路径" (or similar). In that section there is a table whose "重点代码" row lists real repo-relative source paths inside backticks. Extract those source paths. (There may also be a trailing generic mermaid whiteboard block — that is the FAKE one you are replacing; ignore its content, it is a placeholder.)
3. Open and READ those source files in the repo (they are the doc's stated 重点代码). If a path is a glob/short fragment that doesn't exist as-is, find the actual file(s) it refers to and read those. Use the doc body (it explains the module) PLUS the real code.
4. Design a replacement Mermaid diagram SPECIFIC to THIS doc and THIS code. It must depict a REAL flow: request path, state transitions, module dependencies, data flow, or lifecycle — grounded in the code you read. Do NOT duplicate a diagram that already appears earlier in the doc; make something complementary.

HARD RULES:
- replacement_mermaid = raw Mermaid source ONLY, NO triple-backtick fences, starts with the diagram keyword (flowchart / sequenceDiagram / stateDiagram-v2).
- Node labels must name CONCRETE modules/functions/routes/components/files from THIS doc's code. NEVER use generic labels 设计目的/模块职责/收益/代价/重点代码/阅读路径/设计动机/理解方式/解决的问题 or any other placeholder.
- Keep node text SHORT (a few words). NO special characters in node labels that break whiteboard parsing: do not put ( ) [ ] { } < > & | : ；、 as literal text inside labels; the only [ ] allowed is mermaid's own label syntax like NodeID[short label]. Use double-quoted labels like X["short label"] if you need spaces. Use plain words; hyphen - and slash / are OK sparingly.
- Choose diagram_kind per content: sequenceDiagram for request/response chains; flowchart TD or LR for module deps / topology; stateDiagram-v2 only for genuine state machines. Keep under ~16 nodes.
- evidence_paths = ONLY repo-relative paths you actually opened and read. If a cited path does not exist or you did not read it, do NOT list it.
- Be conservative: if you cannot verify a relationship from code, do NOT assert it; note it in risks instead.
- found_fake = true (we already confirmed the remote doc has a fake trailing mermaid; you are replacing it).
- Do NOT edit any files. Do NOT push to lark. Only design and return the structured result.
`, { schema: MermaidSchema, label: item.file.slice(0, 22), phase: 'Design', timeoutMs: 600000 })
)

const clean = results.filter(Boolean)

phase('Review')
const review = await agent(`
You are reviewing ${clean.length} proposed Mermaid replacements for DeerFlow docs. Each is meant to replace a fake generic tail diagram with a source-backed, doc-specific one.

REJECT (approve=false) a proposal ONLY if it is clearly:
- Still generic / templated (labels like 设计目的/模块职责/收益/代价/重点代码/阅读路径 or bare synonyms), OR
- Not source-backed (evidence_paths empty or obviously not read), OR
- Uses special characters in node labels that would break whiteboard parsing (e.g. ( ) : ；｜ as literal label text), OR
- A duplicate of a diagram that already exists earlier in the same doc.

Otherwise approve=true. Give a one-line reason each. Be lenient on style; be strict on genericness and source-backing.

Proposals (JSON):
${JSON.stringify(clean.map(r => ({ file: r.file, kind: r.diagram_kind, evidence: r.evidence_paths, summary: r.one_line_summary, mermaid: r.replacement_mermaid })))}
`, { schema: ReviewSchema, label: 'batch-review', phase: 'Review', timeoutMs: 600000 })

// Attach reviewer verdicts to results
const vmap = {}
for (const v of (review.verdicts || [])) vmap[v.file] = v
const final = clean.map(r => ({ ...r, review: vmap[r.file] || { approve: true, reason: 'not reviewed' } }))

return { count: final.length, results: final }
