"""Insert fixed mermaid for the 14 docs whose fake block was deleted but insert failed.
Fix: remove / and other risky chars from labels, transform |edge| to -- edge --.
"""
import json, os, subprocess, re, time
env=dict(os.environ); env["LARKSUITE_CLI_NO_UPDATE_NOTIFIER"]="1"; env["LARKSUITE_CLI_NO_SKILLS_NOTIFIER"]="1"
design={r['token']:r for r in json.load(open('.agent_context/magic/design_results_283.json'))['results']}
for r in json.load(open('.agent_context/magic/redo_7_done.json'))['results']: design[r['token']]=r
r229=json.load(open('.agent_context/magic/redo229.json'))['results'][0]; design[r229['token']]=r229

# the 14 docs (146 already inserted manually above — skip it)
done_tk="IzzLdAE3voY4ZKxyipcm8xKpyPh"
scan=json.load(open('.agent_context/magic/scan_remote_fake.json'))
fakes=[r for r in scan['results'] if r['status']=='fake' and r['token'] not in ('Flz4daeKQoknccxEUlvmG9Rzy3b', done_tk)]
print("to insert:", len(fakes))

def sanitize(m):
    m=m.replace('→','->').replace('←','<-').replace('↔','<->')
    # transform |edge| and |"edge"| to -- "edge" --
    m=re.sub(r'-->\|"([^"]*)"\|', r'-- "\1" -->', m)
    m=re.sub(r'-->\|([^|]*)\|', r'-- "\1" -->', m)
    # inside [..] and "..." labels: remove/replace risky chars including /
    def fix_inner(s):
        s=s.replace('/',' ').replace('(',' ').replace(')',' ')
        return re.sub(r'\s+',' ',s).strip()
    def repl_bracket(mm):
        inner=mm.group(1)
        if inner.startswith('"') and inner.endswith('"'):
            return '["'+fix_inner(inner[1:-1])+'"]'
        return '['+fix_inner(inner)+']'
    m=re.sub(r'\[([^\[\]]*)\]', repl_bracket, m)
    def repl_quoted(mm):
        return '"'+fix_inner(mm.group(1))+'"'
    m=re.sub(r'"([^"]*)"', repl_quoted, m)
    return m

results=[]
for f in fakes:
    tk=f['token']; name=f['name']
    merm=design.get(tk,{}).get('replacement_mermaid','')
    if not merm.strip(): results.append({"file":name,"status":"no_mermaid"}); continue
    merm=re.sub(r'^```mermaid\s*\n','',merm).strip()
    merm=re.sub(r'\n```\s*$','',merm).strip()
    merm=sanitize(merm)
    esc=merm.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    content=f'<whiteboard type="mermaid">{esc}</whiteboard>'
    # fetch fresh anchor (table in 补充)
    r=subprocess.run(["lark-cli","docs","+fetch","--doc",tk,"--detail","with-ids"],capture_output=True,text=True,env=env,timeout=60)
    if r.returncode!=0: results.append({"file":name,"status":"fetch_fail"}); continue
    c=json.loads(r.stdout)['data']['document']['content']
    # verify no fake whiteboard remains (should be deleted already)
    fake_remaining=[m.group(1) for m in re.finditer(r'<whiteboard id="([^"]+)"[^>]*type="mermaid"[^>]*>([^<]*设计目的[^<]*|[^<]*设计动机[^<]*)</whiteboard>', c)]
    if fake_remaining:
        # delete them first
        rd=subprocess.run(["lark-cli","docs","+update","--doc",tk,"--command","block_delete","--block-id",",".join(fake_remaining)],capture_output=True,text=True,env=env,timeout=60)
        time.sleep(0.8)
        r=subprocess.run(["lark-cli","docs","+fetch","--doc",tk,"--detail","with-ids"],capture_output=True,text=True,env=env,timeout=60)
        c=json.loads(r.stdout)['data']['document']['content']
    tbl=re.findall(r'<table id="([^"]+)"', c)
    anchor=tbl[-1] if tbl else None
    if not anchor: results.append({"file":name,"status":"no_anchor"}); continue
    r2=subprocess.run(["lark-cli","docs","+update","--doc",tk,"--command","block_insert_after","--block-id",anchor,"--doc-format","xml","--content","-"],input=content,capture_output=True,text=True,env=env,timeout=90)
    if r2.returncode==0:
        j=json.loads(r2.stdout); res=j.get('data',{}).get('result'); warns=j.get('data',{}).get('warnings',[])
        results.append({"file":name,"status":res,"warnings_count":len(warns)})
        print(f"  {name[:34]:36s} -> {res} warns={len(warns)}")
        if warns: print(f"      {str(warns)[:120]}")
    else:
        results.append({"file":name,"status":"insert_fail","err":r2.stderr[:150]})
    time.sleep(0.4)
json.dump(results, open('.agent_context/magic/insert_14_results.json','w'), ensure_ascii=False, indent=2)
from collections import Counter
print("\nSUMMARY:", dict(Counter(x['status'] for x in results)))
