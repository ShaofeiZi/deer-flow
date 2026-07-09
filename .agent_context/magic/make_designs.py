#!/usr/bin/env python3
"""
Convert a workflow result file (the JSON returned by the workflow) into the
designs.json format expected by apply_local.py / push_remote.sh.

Workflow returns: {"count": N, "results": [ {file, found_fake, replacement_mermaid,
  diagram_kind, evidence_paths, one_line_summary, risks, review:{approve,reason}} ...]}

designs.json format: { "<filename>": {"mermaid": "...", "approve": bool, "kind":..., "summary":..., "evidence":[...], "reason":...} }

Usage: python3 make_designs.py <workflow_result.json>
"""
import json, sys

src = sys.argv[1]
data = json.load(open(src, encoding="utf-8"))
results = data["results"] if isinstance(data, dict) and "results" in data else data
out = {}
for r in results:
    fn = r.get("file")
    if not fn: continue
    rev = r.get("review") or {}
    out[fn] = {
        "mermaid": (r.get("replacement_mermaid") or "").strip(),
        "approve": bool(rev.get("approve", False)),
        "reason": rev.get("reason", ""),
        "kind": r.get("diagram_kind", ""),
        "summary": r.get("one_line_summary", ""),
        "evidence": r.get("evidence_paths", []),
        "risks": r.get("risks", []),
        "found_fake": r.get("found_fake", False),
    }
with open("/Users/bytedance/deer-flow/.agent_context/magic/designs.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
approved = sum(1 for v in out.values() if v["approve"])
print(f"wrote designs.json: {len(out)} docs, {approved} approved, {len(out)-approved} rejected")
for fn, v in out.items():
    if not v["approve"]:
        print(f"  REJECTED: {fn[:40]} — {v['reason'][:60]}")
