#!/usr/bin/env bash
# Push designed mermaid replacements to the 69 remote Lark docs via block_replace.
# Reads designs.json (filename -> {mermaid, approve}) + batch_mapping.json (filename -> token).
#
# IMPORTANT: block_replace changes the block_id each call, so we re-fetch the CURRENT tail
# whiteboard block_id right before each push (keyword "重点代码与阅读路径" or "设计目的" fallback).
# This is robust regardless of whether the stored block_id is stale.
#
# Safety:
#  - Only pushes docs where approve == true.
#  - block_replace on the tail whiteboard only; never overwrite.
#  - Records ok/result/warnings/new_block_id per doc; failures do not abort the batch.
#  - Serial (one API call at a time) to respect rate limits.
set -u
cd /Users/bytedance/deer-flow
export LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1 LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1
: "${CLAUDE_JOB_DIR:=/Users/bytedance/.claude/jobs/040a8e81}"
mkdir -p "$CLAUDE_JOB_DIR/tmp"

DESIGNS=".agent_context/magic/designs.json"
MAPPING=".agent_context/magic/batch_mapping.json"
RESULTS=".agent_context/magic/push_results.jsonl"
: > "$RESULTS"

# Build per-doc push plan as TSV: filename<TAB>token<TAB>mermaid
mapfile -t PLAN < <(python3 -c "
import json
designs=json.load(open('$DESIGNS'))
mapping=json.load(open('$MAPPING'))
for m in mapping:
    fn=m['file']; d=designs.get(fn,{})
    if not d.get('approve'): continue
    mm=(d.get('mermaid') or '').strip()
    if not mm: continue
    # mermaid is last field; it may contain tabs? mermaid never has literal tabs. safe.
    print(fn + '\t' + m['token'] + '\t' + mm)
")

total=${#PLAN[@]}
i=0
for line in "${PLAN[@]}"; do
  i=$((i+1))
  fn="${line%%$'\t'*}"; rest="${line#*$'\t'}"
  tok="${rest%%$'\t'*}"; mm="${rest#*$'\t'}"

  # 1. Resolve CURRENT tail whiteboard block_id by keyword fetch.
  #    Try "重点代码与阅读路径" first; fall back to "设计目的" (chapter-index doc).
  bid=""
  for kw in "重点代码与阅读路径" "设计目的"; do
    bid=$(lark-cli docs +fetch --doc "$tok" --scope keyword --keyword "$kw" --context-after 4 --detail with-ids 2>/dev/null \
      | python3 -c "
import sys,json,re
try: d=json.load(sys.stdin)
except: sys.exit()
c=d.get('data',{}).get('document',{}).get('content','')
ms=re.findall(r'<whiteboard id=\"([^\"]+)\"[^>]*type=\"mermaid\"[^>]*>(.*?)</whiteboard>', c, re.S)
# pick the last one whose body looks like the fake (or any mermaid) — we want the tail diagram
if ms:
    print(ms[-1][0])
" 2>/dev/null)
    [ -n "$bid" ] && break
  done

  if [ -z "$bid" ]; then
    python3 - "$fn" "$tok" <<'PYEOF' >> "$RESULTS"
import sys,json
fn,tok=sys.argv[1],sys.argv[2]
print(json.dumps({"file":fn,"token":tok,"ok":False,"error":"could not resolve current block_id"}, ensure_ascii=False))
PYEOF
    printf '[%d/%d] %s -> NO_BLOCK_ID\n' "$i" "$total" "${fn:0:28}" >&2
    continue
  fi

  # 2. block_replace with the new mermaid (via stdin to avoid escaping).
  content="<whiteboard type=\"mermaid\">${mm}</whiteboard>"
  out=$(printf '%s' "$content" | lark-cli docs +update --doc "$tok" --command block_replace --block-id "$bid" --content - 2>/tmp/push_err_${i}.txt)
  rc=$?
  python3 - "$fn" "$tok" "$bid" "$rc" "$out" <<'PYEOF' >> "$RESULTS"
import sys, json
fn, tok, bid, rc, out = sys.argv[1:6]
rec={"file":fn,"token":tok,"block_id_used":bid,"rc":rc}
try:
    d=json.loads(out)
    rec["ok"]=d.get("ok",False)
    if d.get("ok"):
        dd=d.get("data",{}); doc=dd.get("document",{})
        rec["result"]=dd.get("result")
        rec["warnings"]=dd.get("warnings",[])
        nb=doc.get("new_blocks",[])
        rec["new_block_id"]=nb[0]["block_id"] if nb else None
    else:
        rec["error"]=d.get("error",{})
except Exception as e:
    rec["ok"]=False; rec["parse_error"]=str(e); rec["raw"]=out[:300]
print(json.dumps(rec, ensure_ascii=False))
PYEOF
  status=$(python3 -c "import sys,json; d=json.loads(open('$RESULTS').read().strip().split(chr(10))[-1]); print('OK' if d.get('ok') else 'FAIL')" 2>/dev/null)
  printf '[%d/%d] %s -> %s\n' "$i" "$total" "${fn:0:28}" "$status" >&2
done

# Summary
python3 -c "
import json
oks=fails=warns=0
with open('$RESULTS') as f:
    for line in f:
        d=json.loads(line)
        if d.get('ok'): oks+=1
        else: fails+=1
        if d.get('warnings'): warns+=1
print(f'PUSHED: ok={oks} fail={fails} docs_with_warnings={warns} total={oks+fails}')
" >&2
echo "Results: $RESULTS" >&2
