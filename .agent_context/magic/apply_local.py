"""Apply approved mermaid replacements to local copies.

Reads .agent_context/magic/designs.json (filename -> {mermaid, approve, ...}).
For each approved doc, replaces the LAST ```mermaid...``` block (the fake template)
in all 6 local snapshot dirs with the new source-backed mermaid.

Safety: backs up, pre-checks the last block is a fake variant, post-verifies,
dry-run by default (pass --apply to write).
"""
import json, os, sys, shutil, re

ROOT = "/Users/bytedance/deer-flow"
DESIGNS = os.path.join(ROOT, ".agent_context/magic/designs.json")
FAKE_DOCS = os.path.join(ROOT, ".agent_context/magic/local_fake_docs.json")

CANON_DIRS = [
    ".agent_context/final_review/docs_md",
    ".agent_context/final_review2/docs_md",
    ".agent_context/reviewer_tmp/docs_md",
    ".agent_context/visual_review/docs_md",
    ".agent_context/lark_remote/current/docs_md",
    ".agent_context/lark_remote/docs_md",
]

FAKE_VARIANTS = [
"""flowchart TD
  A[设计目的] --> B[模块职责]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]""",
"""flowchart TD
  A[设计动机] --> B[模块职责]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[理解方式]""",
"""flowchart TD
  A[设计目的] --> B[模块职责]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[理解方式]""",
"""flowchart TD
  A[设计动机] --> B[模块职责]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]""",
]
FAKE_NORM = set(v.strip() for v in FAKE_VARIANTS)

def last_mermaid_span(content):
    """Return (start_idx_of_fence, end_idx_after_close, body) for last ```mermaid block, or None."""
    idx = content.rfind("```mermaid\n")
    if idx < 0:
        # some variants might use ```mermaid (no trailing newline check) — also try without \n
        idx = content.rfind("```mermaid")
        if idx < 0: return None
    body_start = idx + len("```mermaid\n")
    # if the match was without \n (shouldn't happen), adjust
    if content[idx:idx+len("```mermaid\n")] != "```mermaid\n":
        body_start = idx + len("```mermaid")
    close = content.find("\n```", body_start)
    if close < 0: return None
    body = content[body_start:close]
    end = close + len("\n```")
    return (idx, end, body)

def main():
    dry = "--apply" not in sys.argv
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only")+1]

    designs = json.load(open(DESIGNS, encoding="utf-8"))
    fake_docs = json.load(open(FAKE_DOCS, encoding="utf-8"))
    backup_dir = os.path.join(ROOT, ".agent_context/magic/backup")
    os.makedirs(backup_dir, exist_ok=True)

    applied = []; skipped = []
    for fname in fake_docs:
        if only and fname != only: continue
        d = designs.get(fname)
        if not d:
            skipped.append((fname, "no design")); continue
        if not d.get("approve"):
            skipped.append((fname, "not approved")); continue
        mm = (d.get("mermaid") or "").strip()
        if not mm:
            skipped.append((fname, "empty mermaid")); continue
        # strip accidental fences
        mm = re.sub(r'^```mermaid\s*\n', '', mm)
        mm = re.sub(r'\n```\s*$', '', mm).strip()
        new_block = "```mermaid\n" + mm + "\n```"

        for reldir in CANON_DIRS:
            p = os.path.join(ROOT, reldir, fname)
            if not os.path.exists(p):
                skipped.append((fname, f"missing in {os.path.basename(os.path.dirname(reldir))}/{os.path.basename(reldir)}")); continue
            c = open(p, encoding="utf-8").read()
            span = last_mermaid_span(c)
            if span is None:
                skipped.append((fname, f"no mermaid in {os.path.basename(reldir)}")); continue
            _, _, body = span
            if body.strip() not in FAKE_NORM:
                skipped.append((fname, f"last block not fake in {os.path.basename(reldir)}: {body.strip()[:30]}")); continue
            if dry:
                applied.append((fname, os.path.basename(reldir), "DRY-RUN ok")); continue
            # backup
            slug = reldir.replace("/", "_")
            shutil.copy2(p, os.path.join(backup_dir, slug + "__" + fname.replace("/", "_") + ".bak"))
            idx, end, _ = span
            c2 = c[:idx] + new_block + c[end:]
            # post-verify
            span2 = last_mermaid_span(c2)
            if not span2 or span2[2].strip() != mm:
                skipped.append((fname, f"post-verify failed in {os.path.basename(reldir)}")); continue
            open(p, "w", encoding="utf-8").write(c2)
            applied.append((fname, os.path.basename(reldir), "applied"))

    print(f"APPLIED (dry_run={dry}): {len(applied)}")
    for a in applied: print("  +", a)
    print(f"SKIPPED: {len(skipped)}")
    for s in skipped: print("  -", s)

if __name__ == "__main__":
    main()
