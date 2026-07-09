#!/usr/bin/env bash
# Fetch the remote tail whiteboard (fake-mermaid) block_id for every fake doc.
# Reads all_tokens.json (filename -> docx token), writes block_ids.json (filename -> block_id or null).
set -u
cd /Users/bytedance/deer-flow
export LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1 LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1

TOKENS_FILE=".agent_context/magic/all_tokens.json"
OUT=".agent_context/magic/block_ids.json"
TMPF="$CLAUDE_JOB_DIR/tmp/blockids_out.jsonl"
: "${CLAUDE_JOB_DIR:=/Users/bytedance/.claude/jobs/040a8e81}"
mkdir -p "$CLAUDE_JOB_DIR/tmp"

# Build the list of (filename token) pairs via python
mapfile -t PAIRS < <(python3 -c "
import json
d=json.load(open('$TOKENS_FILE'))
for k,v in d.items():
    print(k + '\t' + v)
")

: > "$TMPF"
total=${#PAIRS[@]}
i=0
for line in "${PAIRS[@]}"; do
  i=$((i+1))
  fn="${line%%$'\t'*}"
  tok="${line##*$'\t'}"
  bid=$(lark-cli docs +fetch --doc "$tok" --scope keyword --keyword "重点代码与阅读路径" \
        --context-after 3 --detail with-ids 2>/dev/null \
    | python3 -c "
import sys,json,re
try: d=json.load(sys.stdin)
except: print(''); sys.exit()
c=d.get('data',{}).get('document',{}).get('content','')
m=re.search(r'<whiteboard id=\"([^\"]+)\"[^>]*type=\"mermaid\"[^>]*>([^<]*)</whiteboard>', c)
if m and '设计目的' in m.group(2): print(m.group(1))
else: print('')
")
  printf '%s\t%s\n' "$fn" "$bid" >> "$TMPF"
  printf '[%d/%d] %s -> %s\n' "$i" "$total" "${fn:0:30}" "${bid:-NONE}" >&2
done

# Convert tab-separated to json
python3 -c "
import json
out={}
with open('$TMPF') as f:
    for line in f:
        line=line.rstrip('\n')
        if not line: continue
        k,v=line.split('\t',1)
        out[k]=v if v else None
json.dump(out, open('$OUT','w'), ensure_ascii=False, indent=2)
ok=sum(1 for x in out.values() if x)
print('WROTE', '$OUT', 'count=',len(out),'with_block_id=',ok)
"
