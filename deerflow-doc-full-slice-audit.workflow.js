export const meta = {
  name: 'deerflow-doc-full-slice-audit',
  description: 'Slice-by-slice audit of DeerFlow remote docs against source code; produce exact update and visualization tasks',
  phases: [
    { title: 'Slice Audit', detail: 'Parallel agents inspect document ranges against source code and remote snapshots' },
    { title: 'Synthesis', detail: 'Aggregate remaining per-doc fixes and Magic/visualization update plan' },
  ],
}

const FINDING_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['slice','summary','docFindings','visualTasks','sourceGaps','verification'],
  properties: {
    slice: {type:'string'},
    summary: {type:'string'},
    docFindings: {type:'array', items:{type:'object', additionalProperties:false, required:['seq','doc','priority','issue','sourceEvidence','recommendedPatch'], properties:{seq:{type:'string'}, doc:{type:'string'}, priority:{type:'string', enum:['P0','P1','P2']}, issue:{type:'string'}, sourceEvidence:{type:'array', items:{type:'string'}}, recommendedPatch:{type:'string'}}}},
    visualTasks: {type:'array', items:{type:'object', additionalProperties:false, required:['seq','doc','diagramType','content','why'], properties:{seq:{type:'string'}, doc:{type:'string'}, diagramType:{type:'string'}, content:{type:'string'}, why:{type:'string'}}}},
    sourceGaps: {type:'array', items:{type:'string'}},
    verification: {type:'array', items:{type:'string'}},
  }
}
const PLAN_SCHEMA = {
  type:'object', additionalProperties:false,
  required:['executiveSummary','mustFix','visualEnhancements','batchOrder','verificationPlan','stopCriteria'],
  properties:{
    executiveSummary:{type:'string'},
    mustFix:{type:'array',items:{type:'object',additionalProperties:false,required:['seq','doc','priority','patch'],properties:{seq:{type:'string'},doc:{type:'string'},priority:{type:'string',enum:['P0','P1','P2']},patch:{type:'string'}}}},
    visualEnhancements:{type:'array',items:{type:'object',additionalProperties:false,required:['seq','doc','diagramType','spec'],properties:{seq:{type:'string'},doc:{type:'string'},diagramType:{type:'string'},spec:{type:'string'}}}},
    batchOrder:{type:'array',items:{type:'string'}},
    verificationPlan:{type:'array',items:{type:'string'}},
    stopCriteria:{type:'array',items:{type:'string'}},
  }
}

const slices = [
  {id:'001-050-core-backend-frontend', range:'1-50', focus:'core architecture, gateway/runtime, lead agent, middleware, frontend entry, settings, MCP/skills/memory'},
  {id:'051-100-api-config-providers', range:'51-100', focus:'routers, community providers, channels, config files, model/sandbox/memory/tool config'},
  {id:'101-150-ui-ai-elements-skills', range:'101-150', focus:'AI Elements, UI primitives, workspace components, public skills'},
  {id:'151-220-skills-tests-docs', range:'151-220', focus:'public skills, backend/frontend tests, workflows, docs/specs/plans'},
  {id:'221-290-runtime-persistence-tools', range:'221-290', focus:'docs/pr evidence, persistence, runtime providers, subagents, tools, tracing, auth/channels'},
  {id:'291-355-frontend-scripts-maintenance', range:'291-355', focus:'frontend core/routes, scripts, docker, i18n, landing, maintenance docs, JS learner guide'},
]

phase('Slice Audit')
const findings = await parallel(slices.map((s) => () => agent(`
You are a source-backed documentation auditor for DeerFlow.
Slice: ${s.id} (${s.range}); focus: ${s.focus}.
Workspace: /Users/bytedance/deer-flow.
Inspect these inputs:
- .agent_context/lark_remote/drive_files.jsonl
- .agent_context/lark_remote/docs_md/*.md remote snapshots
- .agent_context/final_review/docs_md/*.md canonical local docs
- DeerFlow source files matching the slice focus
- .agent_context/lark_remote/verify_core/report.full.json and sync_ledger.jsonl
Task:
1. For every document in your slice, sample/read enough of local doc, remote snapshot, and source to identify remaining source inaccuracies, stale paths, missing state transitions, or weak visual explanations.
2. Do not fabricate. If a doc is acceptable, omit it from findings.
3. Prefer concise, exact patches and diagram specs, not broad prose.
4. Include Magic Builder / HTML Box / Mermaid visualization opportunities only where they add real learning value.
Return strict JSON. Do not edit files.
`, {schema:FINDING_SCHEMA, label:s.id, sandbox:'read-only', timeoutMs:900000})))

phase('Synthesis')
const plan = await agent(`
Synthesize all slice findings into an execution plan for the main agent.
Goal: finish remote/local DeerFlow docs so a JS frontend learner can follow them, with detailed runtime logic, state transitions, and visual diagrams.
Constraints:
- The main agent can edit local Markdown and update Lark docs via lark-cli.
- Use Magic Builder only where appropriate for HTML Box/interactive visual outputs; otherwise Mermaid/whiteboard in docs is acceptable.
- Prioritize remaining source inaccuracies and missing state-transition diagrams over cosmetic rewrites.
- Provide a stop criteria list suitable for Goal-Driven verification.
Findings: ${JSON.stringify(findings)}
`, {schema:PLAN_SCHEMA, label:'full-slice-synthesis', sandbox:'read-only', timeoutMs:900000})

return { findings, plan }
