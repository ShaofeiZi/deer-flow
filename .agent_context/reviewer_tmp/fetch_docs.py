import json, subprocess, pathlib, concurrent.futures, time, re, sys
root=pathlib.Path('.agent_context/reviewer_tmp')
files=json.load(open(root/'files.json'))['data']['files']
out=root/'docs_md'; out.mkdir(exist_ok=True)
err=[]

def safe_name(s):
    return re.sub(r'[^0-9A-Za-z._\-\u4e00-\u9fff｜（）() ]+', '_', s)[:160]

def fetch(item):
    path=out/(safe_name(item['name'])+'.md')
    if path.exists() and path.stat().st_size>20:
        return item['name'], 'cached', path.stat().st_size
    cmd=['lark-cli','docs','+fetch','--api-version','v2','--doc',item['token'],'--doc-format','markdown','--detail','simple','--as','user','--format','json']
    for attempt in range(3):
        p=subprocess.run(cmd, text=True, capture_output=True, timeout=90)
        if p.returncode==0:
            try:
                data=json.loads(p.stdout)
                content=data['data']['document']['content']
                path.write_text(content, encoding='utf-8')
                return item['name'], 'ok', len(content)
            except Exception as e:
                last=f'parse {e} stdout={p.stdout[:200]}'
        else:
            last=f'rc={p.returncode} stderr={p.stderr[:300]} stdout={p.stdout[:200]}'
        time.sleep(1+attempt)
    return item['name'], 'ERR '+last, 0

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    futs=[ex.submit(fetch,x) for x in files]
    for i,f in enumerate(concurrent.futures.as_completed(futs),1):
        name,status,size=f.result()
        if status.startswith('ERR'):
            err.append((name,status))
        if i%25==0 or status.startswith('ERR'):
            print(f'{i}/{len(files)} {status} {size} {name}', flush=True)
print('DONE', len(files), 'errors', len(err))
if err:
    for e in err[:20]: print('ERRITEM', e[0], e[1])
    sys.exit(2)
