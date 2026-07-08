export const meta = {
  name: 'deerflow-doc-path-normalize-audit',
  description: 'Audit DeerFlow local docs for source path references that should be repo-relative, especially bare filenames in module maps.',
  phases: [{ title: 'Canonical path audit' }, { title: 'Verification plan' }],
}

const FindingSchema = {
  type: 'object',
  additionalProperties: false,
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          doc: { type: 'string' },
          line: { type: 'integer' },
          current: { type: 'string' },
          suggested: { type: 'string' },
          evidence_path_exists: { type: 'boolean' },
          reason: { type: 'string' },
          priority: { type: 'string', enum: ['P0', 'P1', 'P2'] }
        },
        required: ['doc','line','current','suggested','evidence_path_exists','reason','priority']
      }
    },
    commands_run: { type: 'array', items: { type: 'string' } },
    notes: { type: 'array', items: { type: 'string' } }
  },
  required: ['findings','commands_run','notes']
}

phase('Canonical path audit')
const audit = await agent(`
You are auditing DeerFlow documentation path references.

Repo cwd: /Users/bytedance/deer-flow
Canonical docs: .agent_context/final_review/docs_md
Mirrors: .agent_context/final_review2/docs_md, .agent_context/reviewer_tmp/docs_md, .agent_context/visual_review/docs_md, .agent_context/JS_FRONTEND_LEARNER_GUIDE.md

Goal: identify documentation source-code path references that should be repo-relative from the deer-flow root. Do not edit files. Produce exact suggested replacements.

Focus especially on:
1. Absolute local paths like /Users/bytedance/deer-flow/... or /Users/bytedance/...
2. Bare filenames in code spans/tables that are ambiguous or too short when a real repo-relative path exists.
3. The known case in doc 02 Gateway map: app.py, deps.py, services.py, thread_runs.py, runs.py, threads.py, router group should become repo-relative paths.
4. Similar router/module maps in docs 11, 21, 22, 23, 49, 68, 109, 204, 290, 326, 327, 346, 347 if they contain bare filenames.

Rules:
- Verify suggested paths exist using rg --files / test -f.
- Ignore runtime data paths such as deer-flow/users/{user_id}/... unless they are presented as local source paths.
- Ignore .agent_context/lark_remote audit artifacts; canonical docs only.
- Return only actionable findings.
`, { schema: FindingSchema, label: 'path-auditor', timeoutMs: 600000 })

phase('Verification plan')
const plan = await agent(`
Given this JSON audit result, write a concise implementation and verification plan. Do not add new findings unless you can evidence them from the JSON.

${JSON.stringify(audit)}

The plan must include:
- docs to patch
- exact validation commands
- Feishu sync approach using .agent_context/lark_remote/current/drive_files.jsonl
- risks / no-go areas
`, {
  schema: {
    type: 'object',
    additionalProperties: false,
    properties: {
      summary: { type: 'string' },
      docs_to_patch: { type: 'array', items: { type: 'string' } },
      validation_commands: { type: 'array', items: { type: 'string' } },
      feishu_sync: { type: 'string' },
      risks: { type: 'array', items: { type: 'string' } }
    },
    required: ['summary','docs_to_patch','validation_commands','feishu_sync','risks']
  },
  label: 'patch-plan',
  timeoutMs: 600000
})

return { audit, plan }
