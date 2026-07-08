export const meta = {
  name: 'deerflow-lark-doc-sync-audit',
  description: 'Compare Lark folder docs, local generated Markdown, and DeerFlow source, then plan high-fidelity JS-frontend learner documentation updates',
  phases: [
    { title: 'Inventory', detail: 'Remote/local manifest comparison and canonical tree decision' },
    { title: 'Source Truth Review', detail: 'Parallel source-backed review of frontend/backend/runtime/doc quality' },
    { title: 'Sync Plan', detail: 'Synthesize local and Lark update plan with priority, exact files, and verification' },
  ],
}

const REVIEW_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['role','summary','confirmedFacts','gaps','recommendedEdits','filesToUpdate','larkDocsToUpdate','verification'],
  properties: {
    role: {type:'string'},
    summary: {type:'string'},
    confirmedFacts: {type:'array', items:{type:'string'}},
    gaps: {type:'array', items:{type:'string'}},
    recommendedEdits: {type:'array', items:{type:'object', additionalProperties:false, required:['priority','target','change','reason'], properties:{priority:{type:'string', enum:['P0','P1','P2']}, target:{type:'string'}, change:{type:'string'}, reason:{type:'string'}}}},
    filesToUpdate: {type:'array', items:{type:'string'}},
    larkDocsToUpdate: {type:'array', items:{type:'string'}},
    verification: {type:'array', items:{type:'string'}},
  }
}

const PLAN_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['executiveSummary','canonicalPolicy','updateBatches','larkSyncPlan','visualizationPlan','verificationPlan','risks'],
  properties: {
    executiveSummary: {type:'string'},
    canonicalPolicy: {type:'string'},
    updateBatches: {type:'array', items:{type:'object', additionalProperties:false, required:['batch','priority','localFiles','remoteDocs','edits','why'], properties:{batch:{type:'string'}, priority:{type:'string', enum:['P0','P1','P2']}, localFiles:{type:'array',items:{type:'string'}}, remoteDocs:{type:'array',items:{type:'string'}}, edits:{type:'array',items:{type:'string'}}, why:{type:'string'}}}},
    larkSyncPlan: {type:'array', items:{type:'string'}},
    visualizationPlan: {type:'array', items:{type:'string'}},
    verificationPlan: {type:'array', items:{type:'string'}},
    risks: {type:'array', items:{type:'string'}},
  }
}

phase('Inventory')
const inventory = await agent(`
You are the inventory auditor for /Users/bytedance/deer-flow.
Goal: compare remote Lark docs and local generated Markdown for a documentation sync project.
Inputs to inspect:
- .agent_context/lark_remote/drive_files.jsonl (355 remote docx files)
- .agent_context/lark_remote/docs_md/*.md (remote fetched Markdown snapshots)
- .agent_context/lark_remote/compare_manifest.json
- .agent_context/lark_remote/local_final_review_manifest.json
- .agent_context/final_review/docs_md/*.md (canonical local candidate, 356 docs)
- prior workflow output in /tmp/deerflow-js-learner-doc-review.resume.result.json if present
Tasks:
1. Summarize remote/local counts and mismatches.
2. Identify canonical local tree and whether remote is missing the JS guide 355.
3. Identify top 10 local-vs-remote content drift docs.
4. Return exact files/docs to update first.
Do not modify files.`, {schema: REVIEW_SCHEMA, label:'inventory', sandbox:'read-only', timeoutMs:900000})

phase('Source Truth Review')
const reviews = await parallel([
  () => agent(`Frontend source-truth reviewer. Inspect the remote/local docs and source code. Focus on making docs accurate and useful for a JS-only frontend learner. Verify submit/stream/message/artifact/settings routes against source. Inputs: ${JSON.stringify(inventory)}. Do not modify files.`, {schema: REVIEW_SCHEMA, label:'frontend-source', sandbox:'read-only', timeoutMs:900000}),
  () => agent(`Backend/runtime source-truth reviewer. Inspect docs and backend source. Focus on Gateway, LangGraph-compatible stream route, RunManager, StreamBridge, lead_agent, middleware, tools/sandbox/skills/memory. Inputs: ${JSON.stringify(inventory)}. Do not modify files.`, {schema: REVIEW_SCHEMA, label:'backend-runtime', sandbox:'read-only', timeoutMs:900000}),
  () => agent(`Lark/visual documentation reviewer. Inspect remote fetched docs and local docs. Focus on Feishu-ready style: rich callouts, tables, Mermaid diagrams, navigation, visual learning path, and avoiding unverified claims. Inputs: ${JSON.stringify(inventory)}. Do not modify files.`, {schema: REVIEW_SCHEMA, label:'lark-visual', sandbox:'read-only', timeoutMs:900000}),
  () => agent(`Coverage and maintainability reviewer. Inspect all manifests and representative docs. Focus on all-doc comparison, generated mirror drift, stale absolute paths, boilerplate, missing local/remote docs, and scalable sync strategy. Inputs: ${JSON.stringify(inventory)}. Do not modify files.`, {schema: REVIEW_SCHEMA, label:'coverage-maint', sandbox:'read-only', timeoutMs:900000}),
  () => agent(`Adversarial claim checker. Verify the highest-risk doc claims against source. Default to unsupported unless you find file evidence. Prioritize JS learner guide, 01, 06, 07, 349-355, and README/frontend/backend README. Inputs: ${JSON.stringify(inventory)}. Do not modify files.`, {schema: REVIEW_SCHEMA, label:'claim-check', sandbox:'read-only', timeoutMs:900000}),
])

phase('Sync Plan')
const plan = await agent(`
Synthesize a concrete execution plan to update local Markdown and Lark docs so a JS-only frontend developer can learn DeerFlow fully.
Use all findings below. The main agent will execute the plan after this workflow.
Constraints:
- Do not recommend rewriting all 355 docs unless necessary; use high-leverage canonical docs first, plus exact source-backed corrections.
- Remote folder currently has 355 docs; local canonical candidate may have 356 including JS guide 355.
- Plan must include which Lark docs need create/update, local files, visual diagrams to add, and verification commands.
- Prefer detailed, beautiful, visual docs, but source accuracy beats decoration.
Inventory: ${JSON.stringify(inventory)}
Reviews: ${JSON.stringify(reviews)}
`, {schema: PLAN_SCHEMA, label:'sync-plan', sandbox:'read-only', timeoutMs:900000})

return { inventory, reviews, plan }
