"""Authoritative scan: for every doc in the Lark folder, fetch the tail section
and classify the LAST whiteboard mermaid as fake-template vs real.
A 'fake' = the mermaid body is a generic design-purpose chain (any of these node labels
appear together as the template skeleton): contains 设计目的 OR 设计动机, AND contains 阅读路径.
Real diagrams use concrete names (Nginx/Gateway/ChatPage...) and lack this template skeleton.
"""
import subprocess, json, os, re, sys, time

env=dict(os.environ); env["LARKSUITE_CLI_NO_UPDATE_NOTIFIER"]="1"; env["LARKSUITE_CLI_NO_SKILLS_NOTIFIER"]="1"
files=json.load(open('.agent_context/magic/lark_folder_files.json'))
cache_dir=".agent_context/magic/scan_cache"
os.makedirs(cache_dir, exist_ok=True)

def fetch_tail(token):
    cache=os.path.join(cache_dir, token+".json")
    if os.path.exists(cache):
        try: return json.load(open(cache))
        except: pass
    for attempt in range(3):
        try:
            r=subprocess.run(["lark-cli","docs","+fetch","--doc",token,
                "--scope","keyword","--keyword","重点代码与阅读路径",
                "--context-after","5","--detail","with-ids"],
                capture_output=True,text=True,env=env,timeout=45)
            if r.returncode==0:
                j=json.loads(r.stdout)
                rec={"ok":True,"content":j['data']['document']['content']}
                json.dump(rec,open(cache,'w'),ensure_ascii=False)
                return rec
            else:
                time.sleep(1.0*(attempt+1))
        except Exception:
            time.sleep(1.0*(attempt+1))
    rec={"ok":False}
    json.dump(rec,open(cache,'w'))
    return rec

def classify(content):
    # find ALL whiteboard mermaid blocks; take the LAST one
    blocks=re.findall(r'<whiteboard[^>]*type="mermaid"[^>]*>([^<]*)</whiteboard>', content)
    if not blocks:
        return "no_mermaid", None
    body=blocks[-1]
    # unescape
    body=body.replace('&gt;','>').replace('&lt;','<').replace('&amp;','&')
    # extract block id of last block
    m=re.search(r'<whiteboard id="([^"]+)"[^>]*type="mermaid"[^>]*>[^<]*</whiteboard>\s*$', content)
    bid=None
    # get last whiteboard tag with id
    bids=re.findall(r'<whiteboard id="([^"]+)"[^>]*type="mermaid"', content)
    bid=bids[-1] if bids else None
    is_template = (("设计目的" in body) or ("设计动机" in body)) and ("阅读路径" in body)
    return ("fake" if is_template else "real"), (bid, body)

results=[]
counts={"fake":0,"real":0,"no_mermaid":0,"fetch_fail":0}
for i,f in enumerate(files):
    rec=fetch_tail(f['token'])
    if not rec.get('ok'):
        counts["fetch_fail"]+=1
        results.append({"name":f['name'],"token":f['token'],"status":"fetch_fail","block_id":None,"body":None})
    else:
        status,info=classify(rec['content'])
        counts[status]+=1
        results.append({"name":f['name'],"token":f['token'],"status":status,
                         "block_id":info[0] if info else None,
                         "body":info[1] if info else None})
    if (i+1)%20==0 or i==len(files)-1:
        sys.stderr.write(f"[{i+1}/{len(files)}] fake={counts['fake']} real={counts['real']} none={counts['no_mermaid']} fail={counts['fetch_fail']}\n")
        sys.stderr.flush()
json.dump({"counts":counts,"results":results}, open('.agent_context/magic/scan_remote_fake.json','w'), ensure_ascii=False, indent=2)
print("\nFINAL:", counts, "total:", len(results))
