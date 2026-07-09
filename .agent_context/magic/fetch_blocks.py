import subprocess, json, os, sys, time, re

# read tokens
tokens={}
with open('.agent_context/magic/all_tokens.txt') as fh:
    for line in fh:
        tk,name=line.rstrip('\n').split('\t',1)
        tokens[name]=tk

results={}  # name -> {token, block_id, status, raw}
cache_dir=".agent_context/magic/fetch_cache"

for name,tk in tokens.items():
    cache=os.path.join(cache_dir, tk+".json")
    if os.path.exists(cache):
        try:
            data=json.load(open(cache))
            results[name]=data
            continue
        except: pass
    env=dict(os.environ); env["LARKSUITE_CLI_NO_UPDATE_NOTIFIER"]="1"; env["LARKSUITE_CLI_NO_SKILLS_NOTIFIER"]="1"
    ok=False
    for attempt in range(3):
        try:
            r=subprocess.run(["lark-cli","docs","+fetch","--doc",tk,
                "--scope","keyword","--keyword","重点代码与阅读路径",
                "--context-after","4","--detail","with-ids"],
                capture_output=True,text=True,env=env,timeout=60)
            if r.returncode==0:
                j=json.loads(r.stdout)
                content=j['data']['document']['content']
                m=re.search(r'<whiteboard id="([^"]+)"[^>]*type="mermaid"[^>]*>([^<]*)</whiteboard>', content)
                if m:
                    rec={"token":tk,"block_id":m.group(1),"body_head":m.group(2)[:40],
                         "status":"ok","raw_len":len(content)}
                    results[name]=rec
                    json.dump(rec,open(cache,'w'),ensure_ascii=False)
                    ok=True
                    break
                else:
                    rec={"token":tk,"block_id":None,"status":"no_whiteboard_match","stderr":r.stderr[:200]}
            else:
                rec={"token":tk,"block_id":None,"status":"fetch_fail","stderr":r.stderr[:200]}
        except Exception as e:
            rec={"token":tk,"block_id":None,"status":"exception","err":str(e)[:200]}
        time.sleep(1)
    if not ok:
        results[name]=rec
        json.dump(rec,open(cache,'w'),ensure_ascii=False)
    sys.stdout.write(f"{name[:30]:32s} {results[name].get('status')} {results[name].get('block_id','')}\n"); sys.stdout.flush()

ok_count=sum(1 for v in results.values() if v.get('status')=='ok')
json.dump(results,open('.agent_context/magic/all_block_ids.json','w'),ensure_ascii=False,indent=2)
print(f"\nDONE: {ok_count}/{len(results)} got block_id")
