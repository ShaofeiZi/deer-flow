import json, subprocess, pathlib, re, time, sys, random
root=pathlib.Path('.agent_context/final_review')
out=root/'docs_md'
out.mkdir(exist_ok=True)
files=json.load(open(root/'files.json'))['data']['files']

def safe_name(s):
    return re.sub(r'[^0-9A-Za-z._\-\u4e00-\u9fff｜（）() ]+', '_', s)[:180]

errors=[]
for idx,item in enumerate(files,1):
    path=out/(safe_name(item['name'])+'.md')
    cmd=['lark-cli','docs','+fetch','--api-version','v2','--doc',item['token'],'--doc-format','markdown','--detail','simple','--as','user','--format','json']
    ok=False; last=''
    for attempt in range(6):
        p=subprocess.run(cmd, text=True, capture_output=True, timeout=120)
        if p.returncode==0:
            try:
                data=json.loads(p.stdout)
                content=data['data']['document']['content']
                path.write_text(content, encoding='utf-8')
                ok=True
                break
            except Exception as e:
                last=f'parse {e} stdout={p.stdout[:200]}'
        else:
            last=(p.stderr or p.stdout)[:400].replace('\n',' ')
        if 'rate_limit' in (p.stderr+p.stdout) or 'frequency limit' in (p.stderr+p.stdout):
            time.sleep(8 + attempt*6)
        else:
            time.sleep(2 + attempt)
    if not ok:
        errors.append((item['name'], last))
        print(f'{idx}/{len(files)} ERR {item["name"]}: {last}', flush=True)
    elif idx % 25 == 0:
        print(f'{idx}/{len(files)} ok', flush=True)
    time.sleep(1.0)
print('DONE fetched', len(files)-len(errors), 'errors', len(errors))
if errors:
    (root/'fetch_errors.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2), encoding='utf-8')
    sys.exit(2)
