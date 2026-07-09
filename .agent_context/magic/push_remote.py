"""Push approved mermaid to remote Lark docs via block_replace.
Serial, idempotent (skip 'no changes'), retry on transient errors, record per-doc result.
"""
import json, os, sys, subprocess, time, re

def clean_body(b):
    b = b.strip()
    b = re.sub(r'^```mermaid\s*\n', '', b)
    b = re.sub(r'\n```\s*$', '', b)
    return b.strip()

def push_one(token, block_id, mermaid_body):
    body = clean_body(mermaid_body)
    esc = body.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    content = f'<whiteboard type="mermaid">{esc}</whiteboard>'
    env=dict(os.environ); env["LARKSUITE_CLI_NO_UPDATE_NOTIFIER"]="1"; env["LARKSUITE_CLI_NO_SKILLS_NOTIFIER"]="1"
    cmd=["lark-cli","docs","+update","--doc",token,"--command","block_replace",
         "--block-id",block_id,"--doc-format","xml","--content","-"]
    for attempt in range(3):
        try:
            r=subprocess.run(cmd, input=content, capture_output=True, text=True, env=env, timeout=90)
            out={"returncode":r.returncode,"stdout_head":r.stdout[:600],"stderr_head":r.stderr[:300]}
            if r.returncode==0:
                j=json.loads(r.stdout)
                out["ok"]=j.get("ok")
                dd=j.get("data",{})
                out["result"]=dd.get("result")
                out["warnings"]=dd.get("warnings",[])
                # success if ok and not the no-op 'failed' with no-changes warning
                noop = out["result"]=="failed" and any("no document changes" in str(w) for w in out["warnings"])
                out["noop"]=noop
                if out["ok"]: return out
            time.sleep(1.5*(attempt+1))
        except Exception as e:
            out={"returncode":-1,"exception":str(e)[:200]}
            time.sleep(1.5*(attempt+1))
    return out

if __name__ == "__main__":
    rf = sys.argv[1]
    data = json.load(open(rf, encoding='utf-8'))
    results = data.get('results', data)
    only = sys.argv[sys.argv.index("--only")+1] if "--only" in sys.argv else None
    dry = "--apply" not in sys.argv
    start = int(sys.argv[sys.argv.index("--start")+1]) if "--start" in sys.argv else 0
    push_results=[]
    okc=failc=noopc=0
    for i,r in enumerate(results):
        if i < start: continue
        if only and r.get('file') != only: continue
        token=r.get('token'); block_id=r.get('block_id'); mermaid=r.get('replacement_mermaid','')
        if not (token and block_id and mermaid.strip()):
            push_results.append({"file":r.get('file'),"status":"missing_data"}); continue
        if dry:
            push_results.append({"file":r.get('file'),"status":"dry_run"}); continue
        res = push_one(token, block_id, mermaid)
        st = "ok" if res.get("ok") and not res.get("noop") else ("noop" if res.get("noop") else "fail")
        if st=="ok": okc+=1
        elif st=="noop": noopc+=1
        else: failc+=1
        push_results.append({"file":r.get('file'),"token":token,"block_id":block_id,"status":st,
                             "result":res.get("result"),"warnings":res.get("warnings")})
        # progress every 10
        if (i+1)%10==0:
            sys.stderr.write(f"[{i+1}/{len(results)}] ok={okc} noop={noopc} fail={failc}\n"); sys.stderr.flush()
        json.dump(push_results, open('.agent_context/magic/push_results_live.json','w'), ensure_ascii=False)
        time.sleep(0.3)
    json.dump(push_results, open('.agent_context/magic/push_results.json','w'), ensure_ascii=False, indent=2)
    print(f"\nPUSH SUMMARY: ok={okc} noop={noopc} fail={failc} total_pushed={okc+noopc+failc} (dry_run={dry})")
