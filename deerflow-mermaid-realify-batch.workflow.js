export const meta = {
  name: 'deerflow-mermaid-realify-batch',
  description: 'Generate source-backed Mermaid replacements for fake generic DeerFlow doc diagrams, one doc at a time.',
  phases: [{ title: 'Per-doc source-backed diagram design' }, { title: 'Batch review' }],
}

const DocDiagramSchema = {
  type: 'object',
  additionalProperties: false,
  properties: {
    doc: { type: 'string' },
    has_fake_diagram: { type: 'boolean' },
    replacement_mermaid: { type: 'string' },
    insertion_note: { type: 'string' },
    evidence_paths: { type: 'array', items: { type: 'string' } },
    source_backing_summary: { type: 'string' },
    risks_or_uncertainty: { type: 'array', items: { type: 'string' } }
  },
  required: ['doc','has_fake_diagram','replacement_mermaid','insertion_note','evidence_paths','source_backing_summary','risks_or_uncertainty']
}

const ReviewSchema = {
  type: 'object',
  additionalProperties: false,
  properties: {
    approved: { type: 'boolean' },
    unsafe_docs: { type: 'array', items: { type: 'string' } },
    notes: { type: 'array', items: { type: 'string' } }
  },
  required: ['approved','unsafe_docs','notes']
}

const docs = args.docs || args.batch
phase('Per-doc source-backed diagram design')
const results = []
for (const doc of docs) {
  const result = await agent(`
You are fixing one DeerFlow Markdown documentation diagram.

Repo cwd: /Users/bytedance/deer-flow
Target doc: .agent_context/final_review/docs_md/${doc}

Task:
1. Read the target Markdown doc.
2. Locate the exact fake generic Mermaid block if present:
   flowchart TD
     A[设计目的] --> B[模块职责]
     B --> C[收益]
     B --> D[代价]
     C --> E[重点代码]
     D --> E
     E --> F[阅读路径]
3. Inspect the source files referenced by the doc's "重点代码", tables, module maps, and surrounding sections. If paths are broad/globs, inspect representative files that actually exist.
4. Produce a replacement Mermaid diagram that is specific to THIS doc and THIS code. It should show real runtime flow, state transitions, module relationships, request/data flow, or lifecycle logic from the code. Do not create a generic design-purpose graph.

Hard rules:
- Output a complete Mermaid fenced block in replacement_mermaid, starting with a Mermaid fence and ending with a closing fence.
- Prefer flowchart TD or LR, stateDiagram-v2 only when the code/doc is state-machine-like.
- Node labels should name concrete modules/functions/routes/components from the doc/code, not generic labels like 设计目的/模块职责/收益/代价/重点代码/阅读路径.
- Cite repo-relative evidence paths that you actually inspected.
- If you cannot verify a source path, include uncertainty and keep the graph conservative.
- Do not edit files.
`, { schema: DocDiagramSchema, label: doc.slice(0, 24), timeoutMs: 600000 })
  results.push(result)
}

phase('Batch review')
const review = await agent(`
Review these proposed Mermaid replacements. Reject only if a replacement is clearly generic/fake or not source-backed.

${JSON.stringify(results)}

Return approved=true only if all safe to apply. List unsafe docs otherwise.
`, { schema: ReviewSchema, label: 'batch-review', timeoutMs: 600000 })

return { results, review }
