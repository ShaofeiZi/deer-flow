export const meta = {
  name: 'deerflow-js-learner-doc-review',
  description: 'Review uncommitted Markdown docs and propose improvements for a JS frontend learner studying DeerFlow',
  phases: [
    { title: 'Inventory', detail: 'Map changed markdown files and detect doc-set structure' },
    { title: 'Focused Review', detail: 'Parallel review from repo, frontend, backend, and learner perspectives' },
    { title: 'Synthesis', detail: 'Turn findings into concrete edit plan' },
  ],
}

const REVIEW_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['role', 'summary', 'strengths', 'gaps', 'recommendedEdits', 'mustInspectFiles', 'confidence'],
  properties: {
    role: { type: 'string' },
    summary: { type: 'string' },
    strengths: { type: 'array', items: { type: 'string' } },
    gaps: { type: 'array', items: { type: 'string' } },
    recommendedEdits: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['target', 'change', 'reason', 'priority'],
        properties: {
          target: { type: 'string' },
          change: { type: 'string' },
          reason: { type: 'string' },
          priority: { type: 'string', enum: ['P0', 'P1', 'P2'] },
        },
      },
    },
    mustInspectFiles: { type: 'array', items: { type: 'string' } },
    confidence: { type: 'string' },
  },
}

const SYNTHESIS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['executiveSummary', 'editPlan', 'learningPath', 'sourceGaps', 'verificationPlan'],
  properties: {
    executiveSummary: { type: 'string' },
    editPlan: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['target', 'edit', 'why', 'priority'],
        properties: {
          target: { type: 'string' },
          edit: { type: 'string' },
          why: { type: 'string' },
          priority: { type: 'string', enum: ['P0', 'P1', 'P2'] },
        },
      },
    },
    learningPath: { type: 'array', items: { type: 'string' } },
    sourceGaps: { type: 'array', items: { type: 'string' } },
    verificationPlan: { type: 'array', items: { type: 'string' } },
  },
}

phase('Inventory')
const inventory = await agent(`
You are the inventory agent for /Users/bytedance/deer-flow.
Goal: identify the uncommitted Markdown docs relevant to teaching DeerFlow to a JS-only frontend developer.
Run read-only shell commands as needed. Prefer concise evidence.
Inspect:
- git status --short -- '*.md'
- representative files in .agent_context/final_review/docs_md, .agent_context/visual_review/docs_md, .agent_context/reviewer_tmp/docs_md
- root README.md, frontend/README.md, backend/README.md when useful
Return: what changed, which files look like entry/navigation/quality docs, which docs should be edited first, and any duplication risks.
`, { schema: REVIEW_SCHEMA, label: 'inventory', sandbox: 'read-only', timeoutMs: 600000 })

phase('Focused Review')
const reviewers = await parallel([
  () => agent(`
You are the repo architecture reviewer. In /Users/bytedance/deer-flow, inspect changed Markdown plus source tree enough to judge whether the new docs explain the whole project accurately.
Focus on: backend/frontend/runtime boundaries, where a JS frontend learner will get lost, and source-backed corrections.
Do not modify files. Return concrete edit suggestions with paths.
Inventory context: ${JSON.stringify(inventory)}
`, { schema: REVIEW_SCHEMA, label: 'architecture', sandbox: 'read-only', timeoutMs: 600000 }),
  () => agent(`
You are the frontend learning-path reviewer for a learner who only knows JavaScript.
Inspect changed docs and frontend source/readmes in /Users/bytedance/deer-flow.
Focus on: how to bridge JS knowledge to this repo's frontend stack, what to read first, terms to define, and exercises to add.
Do not modify files. Return concrete edit suggestions with paths.
Inventory context: ${JSON.stringify(inventory)}
`, { schema: REVIEW_SCHEMA, label: 'frontend-learner', sandbox: 'read-only', timeoutMs: 600000 }),
  () => agent(`
You are the backend-for-frontend explainer. Inspect changed docs and backend entry points in /Users/bytedance/deer-flow.
Focus on: explaining Python/LangGraph/backend concepts using analogies a JS frontend developer understands, without dumbing down.
Do not modify files. Return concrete edit suggestions with paths.
Inventory context: ${JSON.stringify(inventory)}
`, { schema: REVIEW_SCHEMA, label: 'backend-bff', sandbox: 'read-only', timeoutMs: 600000 }),
  () => agent(`
You are the documentation quality reviewer. Inspect changed Markdown files in /Users/bytedance/deer-flow.
Focus on: duplication, navigation, naming, visual/readability consistency, broken relative links, and whether generated docs need a maintainer guide.
Do not modify files. Return concrete edit suggestions with paths.
Inventory context: ${JSON.stringify(inventory)}
`, { schema: REVIEW_SCHEMA, label: 'doc-quality', sandbox: 'read-only', timeoutMs: 600000 }),
  () => agent(`
You are the source-backed claim checker. Inspect representative changed docs and verify high-level claims against source files.
Focus on: claims likely to mislead a learner, missing caveats, and uncertain areas that should be labeled as such.
Do not modify files. Return concrete edit suggestions with paths.
Inventory context: ${JSON.stringify(inventory)}
`, { schema: REVIEW_SCHEMA, label: 'claim-checker', sandbox: 'read-only', timeoutMs: 600000 }),
])

phase('Synthesis')
const synthesis = await agent(`
Synthesize the inventory and reviewer findings into a practical edit plan for the main agent.
Goal: improve uncommitted Markdown so a JS-only frontend developer can learn DeerFlow.
Prioritize a small number of high-leverage docs: navigation/index, reading path, module coverage matrix, source-walk checklist, final acceptance/evidence.
Separate confirmed source-backed advice from uncertainty.
Inventory: ${JSON.stringify(inventory)}
Reviewer findings: ${JSON.stringify(reviewers)}
`, { schema: SYNTHESIS_SCHEMA, label: 'synthesis', sandbox: 'read-only', timeoutMs: 600000 })

return { inventory, reviewers, synthesis }
