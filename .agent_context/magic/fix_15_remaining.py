"""For each remaining fake doc: delete the fake whiteboard block, then insert a fixed real mermaid whiteboard after the 补充-section table."""
import json, os, sys, subprocess, re, time
env=dict(os.environ); env["LARKSUITE_CLI_NO_UPDATE_NOTIFIER"]="1"; env["LARKSUITE_CLI_NO_SKILLS_NOTIFIER"]="1"
design={r['token']:r for r in json.load(open('.agent_context/magic/design_results_283.json'))['results']}
# also redo + 229
for r in json.load(open('.agent_context/magic/redo_7_done.json'))['results']: design[r['token']]=r
r229=json.load(open('.agent_context/magic/redo229.json'))['results'][0]; design[r229['token']]=r229

scan=json.load(open('.agent_context/magic/scan_remote_fake.json'))
fakes=[r for r in scan['results'] if r['status']=='fake']
# 180 already done — skip
fakes=[r for r in fakes if r['token']!='Flz4daeKQoknccxEUlvmG9Rzy3b']
print("to fix:", len(fakes))

def fetch_full(tk):
    r=subprocess.run(["lark-cli","docs","+fetch","--doc",tk,"--detail","with-ids"],capture_output=True,text=True,env=env,timeout=60)
    if r.returncode!=0: return None
    return json.loads(r.stdout)['data']['document']['content']

results=[]
for f in fakes:
    tk=f['token']; name=f['name']
    c=fetch_full(tk)
    if not c: results.append({"file":name,"status":"fetch_fail"}); continue
    # find ALL fake whiteboard blocks (could be multiple)
    fake_blocks=[]
    for m in re.finditer(r'<whiteboard id="([^"]+)"[^>]*type="mermaid"[^>]*>([^<]*)</whiteboard>', c):
        bid=m.group(1); body=m.group(2).replace('&gt;','>').replace('&lt;','<')
        is_fake=('设计目的' in body or '设计动机' in body) and any(k in body for k in ['模块职责','解决的问题','阅读路径','理解方式'])
        if is_fake: fake_blocks.append((bid, m.start()))
    if not fake_blocks:
        results.append({"file":name,"status":"no_fake_found"}); continue
    # find the 补充 section table id to use as insert anchor (for the LAST fake block's section)
    # use the table that appears right before the last fake block
    last_bid, last_pos = fake_blocks[-1]
    before=c[:last_pos]
    tbl=re.findall(r'<table id="([^"]+)"', before)
    anchor=tbl[-1] if tbl else None
    if not anchor:
        results.append({"file":name,"status":"no_table_anchor"}); continue
    # get mermaid, fix unicode arrows
    merm=design.get(tk,{}).get('replacement_mermaid','')
    if not merm.strip(): results.append({"file":name,"status":"no_mermaid"}); continue
    merm=merm.replace('→','->').replace('←','<-').replace('↔','<->')
    merm=re.sub(r'^```mermaid\s*\n','',merm).strip()
    merm=re.sub(r'\n```\s*$','',merm).strip()
    esc=merm.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    content=f'<whiteboard type="mermaid">{esc}</whiteboard>'
    # delete all fake blocks
    del_ids=",".join(b for b,_ in fake_blocks)
    r1=subprocess.run(["lark-cli","docs","+update","--doc",tk,"--command","block_delete","--block-id",del_ids],capture_output=True,text=True,env=env,timeout=60)
    if r1.returncode!=0:
        results.append({"file":name,"status":"delete_fail","err":r1.stderr[:150]}); continue
    time.sleep(0.8)
    # re-fetch to get fresh table id (delete may have shifted ids? table id usually stable)
    c2=fetch_full(tk)
    tbl2=re.findall(r'<table id="([^"]+)"', c2)
    anchor2=tbl2[-1] if tbl2 else anchor
    r2=subprocess.run(["lark-cli","docs","+update","--doc",tk,"--command","block_insert_after","--block-id",anchor2,"--doc-format","xml","--content","-"],input=content,capture_output=True,text=True,env=env,timeout=90)
    if r2.returncode==0:
        j=json.loads(r2.stdout); res=j.get('data',{}).get('result'); warns=j.get('data',{}).get('warnings',[])
        results.append({"file":name,"status":res,"warnings":warns})
        print(f"  {name[:34]:36s} del={len(fake_blocks)} ins={res} warns={len(warns)}")
    else:
        results.append({"file":name,"status":"insert_fail","err":r2.stderr[:150]})
        print(f"  {name[:34]:36s} INSERT FAIL: {r2.stderr[:100]}")
    time.sleep(0.4)
json.dump(results, open('.agent_context/magic/fix_15_results.json','w'), ensure_ascii=False, indent=2)
from collections import Counter
print("\nSUMMARY:", dict(Counter(x['status'] for x in results)))
