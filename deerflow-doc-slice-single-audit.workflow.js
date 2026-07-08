export const meta = {
  name: 'deerflow-doc-slice-single-audit',
  description: 'Single-slice low-concurrency audit of DeerFlow docs against source code for remaining fixes and visual tasks',
  phases: [{ title: 'Single Slice Audit' }],
}
const SCHEMA={type:'object',additionalProperties:false,required:['slice','summary','docFindings','visualTasks','nextVerification'],properties:{slice:{type:'string'},summary:{type:'string'},docFindings:{type:'array',items:{type:'object',additionalProperties:false,required:['seq','doc','priority','issue','evidence','patch'],properties:{seq:{type:'string'},doc:{type:'string'},priority:{type:'string',enum:['P0','P1','P2']},issue:{type:'string'},evidence:{type:'array',items:{type:'string'}},patch:{type:'string'}}}},visualTasks:{type:'array',items:{type:'object',additionalProperties:false,required:['seq','doc','diagram','spec'],properties:{seq:{type:'string'},doc:{type:'string'},diagram:{type:'string'},spec:{type:'string'}}}},nextVerification:{type:'array',items:{type:'string'}}}}
phase('Single Slice Audit')
const slice=args.slice
const result=await agent(`
Low-concurrency source-backed doc audit. Slice: ${JSON.stringify(slice)}.
Workspace /Users/bytedance/deer-flow.
Inspect:
- .agent_context/final_review/docs_md docs in range
- .agent_context/lark_remote/docs_md remote snapshots in range
- .agent_context/lark_remote/static_cleanup_verify_report.json
- source files relevant to slice focus
Goal: identify ONLY remaining issues after prior P0/P1/static cleanup. Omit docs that are now acceptable.
Focus on source inaccuracies, missing state transitions, missing runtime diagrams, or strong Magic/HTML Box/interactive visualization opportunities.
Return exact patches and diagram specs. Do not edit files.
`,{schema:SCHEMA,label:slice.id,sandbox:'read-only',timeoutMs:900000})
return result
