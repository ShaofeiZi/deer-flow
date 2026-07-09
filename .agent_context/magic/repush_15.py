"""For each remaining fake doc: fetch current last whiteboard block_id, then block_replace with the approved mermaid."""
import json, os, sys, subprocess, re, time
env=dict(os.environ); env["LARKSUITE_CLI_NO_UPDATE_NOTIFIER"]="1"; env["LARKSUITE_CLI_NO_SKILLS_NOTIFIER"]="1"
todo=json.load(open('.agent_context/magic/repush_15.json'))
def clean(b):
    import re as _re
    b=b.strip()
    b=_re.sub(r'^```mermaid\s*\n','',b); b=_re.sub(r'\n```\s*$','',b)
    return b.strip()
def cur_block(tk):
    r=subprocess.run(["lark-cli","docs","+fetch","--doc",tk,"--scope","keyword","--keyword","重点代码与阅读路径","--context-after","4","--detail","with-ids"],capture_output=True,text=True,env=env,timeout=45)
    if r.returncode!=0: return None,None
    c=json.loads(r.stdout)['data']['document']['content']
    bids=re.findall(r'<whiteboard id="([^"]+)"[^>]*type="mermaid"', c)
    bodies=re.findall(r'<whiteboard[^>]*type="mermaid"[^>]*>([^<]*)</whiteboard>', c)
    if not bids: return None,None
    return bids[-1], (bodies[-1] if bodies else '')
results=[]
for t in todo:
    tk=t['token']; mermaid=clean(t['mermaid'])
    bid,body=cur_block(tk)
    if not bid:
        results.append({"file":t['file'],"status":"fetch_fail"}); print(f"  FETCH FAIL {t['file'][:30]}"); continue
    esc=mermaid.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    content=f'<whiteboard type="mermaid">{esc}</whiteboard>'
    r=subprocess.run(["lark-cli","docs","+update","--doc",tk,"--command","block_replace","--block-id",bid,"--doc-format","xml","--content","-"],input=content,capture_output=True,text=True,env=env,timeout=90)
    st="fail"
    if r.returncode==0:
        j=json.loads(r.stdout); dd=j.get("data",{})
        noop=dd.get("result")=="failed" and any("no document changes" in str(w) for w in dd.get("warnings",[]))
        st="noop" if noop else ("ok" if j.get("ok") else "fail")
        # if noop, the content might already match — check if it's already the real mermaid
        if noop:
            cur_body=body.replace('&gt;','>').replace('&lt;','<').replace('&amp;','&')
            if mermaid.splitlines()[0] in cur_body: st="already_real"
    results.append({"file":t['file'],"token":tk,"block_id":bid,"status":st,"warnings":j.get("data",{}).get("warnings",[]) if r.returncode==0 else r.stderr[:200]})
    print(f"  {t['file'][:36]:38s} bid={bid[:16]}.. -> {st}")
    time.sleep(0.3)
json.dump(results, open('.agent_context/magic/repush_15_results.json','w'), ensure_ascii=False, indent=2)
from collections import Counter
print("\nSUMMARY:", dict(Counter(x['status'] for x in results)))
