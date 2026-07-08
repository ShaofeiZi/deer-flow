import json, pathlib, subprocess, re, sys, time
root=pathlib.Path('.agent_context/visual_review')
out=root/'docs_md'; out.mkdir(exist_ok=True)
files=json.load(open(root/'files.json'))['data']['files']
prefixes=['DeerFlow 2.0 源码分层详解：章节目录']+[f'{i:02d}｜' for i in range(1,9)]+['88｜','90｜','91｜','95｜','98｜','100｜','132｜','133｜']+[f'{i}｜' for i in range(349,355)]
selected=[]
for pref in prefixes:
    m=[f for f in files if f['name']==pref or f['name'].startswith(pref)]
    if not m:
        print('MISS',pref)
    else:
        selected.append(m[0])
print('selected',len(selected),[x['name'] for x in selected])
def safe(s): return re.sub(r'[^0-9A-Za-z._\-\u4e00-\u9fff｜（）() ]+','_',s)[:180]
errs=[]
for idx,item in enumerate(selected,1):
    path=out/(safe(item['name'])+'.md')
    cmd=['lark-cli','docs','+fetch','--api-version','v2','--doc',item['token'],'--doc-format','markdown','--detail','simple','--as','user','--format','json']
    ok=False; last=''
    for attempt in range(5):
        p=subprocess.run(cmd,text=True,capture_output=True,timeout=120)
        if p.returncode==0:
            try:
                data=json.loads(p.stdout); content=data['data']['document']['content']; path.write_text(content,encoding='utf-8')
                print(idx,'ok',item['name'],len(content)); ok=True; break
            except Exception as e: last=f'parse {e} {p.stdout[:200]}'
        else:
            last=(p.stderr or p.stdout)[:300].replace('\n',' ')
        time.sleep(5+attempt*5)
    if not ok: errs.append((item['name'],last)); print('ERR',item['name'],last)
if errs:
    print('ERRORS',errs); sys.exit(2)
