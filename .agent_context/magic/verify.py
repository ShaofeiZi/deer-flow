#!/usr/bin/env python3
"""
Verify that local application + remote push actually replaced the fake mermaid.

Checks:
  LOCAL: for each approved doc in final_review/docs_md, the LAST mermaid block is
         NO LONGER the fake template, and matches the design's mermaid.
  REMOTE: re-fetch each pushed doc's tail whiteboard; confirm its body is no longer
          the fake template (and ideally matches the design). Reads push_results.jsonl
          to know what was pushed.

Usage: python3 verify.py [--local-only] [--remote-only]
"""
import os, sys, json, subprocess, re

ROOT = "/Users/bytedance/deer-flow"
DESIGNS = json.load(open(os.path.join(ROOT, ".agent_context/magic/designs.json"), encoding="utf-8"))
FAKE = json.load(open(os.path.join(ROOT, ".agent_context/magic/local_fake_docs.json"), encoding="utf-8"))
MAPPING = json.load(open(os.path.join(ROOT, ".agent_context/magic/batch_mapping.json"), encoding="utf-8"))

FAKE_VARIANTS = [
"flowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]",
"flowchart TD\n  A[设计动机] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[理解方式]",
"flowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[理解方式]",
"flowchart TD\n  A[设计动机] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]",
]
FAKE_NORM = set(v.strip() for v in FAKE_VARIANTS)

def last_mermaid_body(content):
    i = content.rfind("```mermaid\n")
    if i < 0: return None
    s = i + len("```mermaid\n")
    e = content.find("\n```", s)
    return content[s:e].strip() if e >= 0 else None

mode = sys.argv[1] if len(sys.argv) > 1 else "all"

def check_local():
    print("=== LOCAL verification (final_review/docs_md) ===")
    ok=fail=0; fails=[]
    for fn in FAKE:
        d = DESIGNS.get(fn, {})
        if not d.get("approve"): continue
        p = os.path.join(ROOT, ".agent_context/final_review/docs_md", fn)
        if not os.path.exists(p): continue
        body = last_mermaid_body(open(p, encoding="utf-8").read())
        if body is None:
            fail+=1; fails.append((fn,"no mermaid block")); continue
        if body in FAKE_NORM:
            fail+=1; fails.append((fn,"STILL FAKE")); continue
        if body.strip() != (d.get("mermaid") or "").strip():
            fail+=1; fails.append((fn,"body != design mermaid")); continue
        ok+=1
    print(f"  local OK={ok} FAIL={fail}")
    for fn,why in fails: print(f"    FAIL {fn[:40]}: {why}")
    return ok, fail

def check_remote():
    print("=== REMOTE verification (re-fetch tail whiteboard) ===")
    ok=fail=0; fails=[]
    map_by_file = {m["file"]: m for m in MAPPING}
    for fn, d in DESIGNS.items():
        if not d.get("approve"): continue
        m = map_by_file.get(fn)
        if not m: continue
        tok = m["token"]
        cmd = ["lark-cli","docs","+fetch","--doc",tok,"--scope","keyword","--keyword","重点代码与阅读路径","--context-after","3","--detail","with-ids"]
        env={"LARKSUITE_CLI_NO_UPDATE_NOTIFIER":"1","LARKSUITE_CLI_NO_SKILLS_NOTIFIER":"1","PATH":os.environ["PATH"]}
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
            j = json.loads(r.stdout)
            c = j["data"]["document"]["content"]
            ms = re.findall(r'<whiteboard id="([^"]+)"[^>]*type="mermaid"[^>]*>(.*?)</whiteboard>', c, re.S)
            if not ms:
                # maybe keyword missed the section; treat as need-manual-check
                fail+=1; fails.append((fn,"no whiteboard in keyword fetch")); continue
            bid, body_html = ms[-1]
            # body is HTML-escaped (&gt; etc); unescape minimally
            body = body_html.replace("&gt;",">").replace("&lt;","<").replace("&amp;","&").replace("&quot;",'"').strip()
            if body in FAKE_NORM:
                fail+=1; fails.append((fn,"STILL FAKE remote")); continue
            ok+=1
        except Exception as e:
            fail+=1; fails.append((fn, f"err {str(e)[:50]}"))
    print(f"  remote OK={ok} FAIL={fail}")
    for fn,why in fails: print(f"    FAIL {fn[:40]}: {why}")
    return ok, fail

if mode in ("all","--local-only"): check_local()
if mode in ("all","--remote-only"): check_remote()
