import json, subprocess, pathlib, re, time, sys
root=pathlib.Path('.agent_context/reviewer_tmp')
files=json.load(open(root/'files.json'))['data']['files']
out=root/'docs_md'; out.mkdir(exist_ok=True)
def safe_name(s): return re.sub(r'[^0-9A-Za-z._\-\u4e00-\u9fff｜（）() ]+', '_', s)[:160]
missing=[x for x in files if not (out/(safe_name(x['name'])+'.md')).exists() or (out/(safe_name(x['name'])+'.md')).stat().st_size<=20]
print('missing', len(missing))
errors=[]
for idx,item in enumerate(missing,1):
    path=out/(safe_name(item['name'])+'.md')
    cmd=['lark-cli','docs','+fetch','--api-version','v2','--doc',item['token'],'--doc-format','markdown','--detail','simple','--as','user','--format','json']
    ok=False; last=''
    for attempt in range(5):
        p=subprocess.run(cmd, text=True, capture_output=True, timeout=90)
        if p.returncode==0:
            try:
                data=json.loads(p.stdout); content=data['data']['document']['content']; path.write_text(content, encoding='utf-8')
                print(f'{idx}/{len(missing)} ok {len(content)} {item["name"]}', flush=True); ok=True; break
            except Exception as e: last=f'parse {e}'
        else:
            last=(p.stderr or p.stdout)[:200].replace('\n',' ')
            if 'rate_limit' in p.stderr or 'frequency limit' in p.stderr:
                time.sleep(8+attempt*5)
            else:
                time.sleep(2)
    if not ok:
        print(f'{idx}/{len(missing)} ERR {last} {item["name"]}', flush=True); errors.append((item['name'],last))
    time.sleep(1.2)
print('DONE errors', len(errors))
if errors: sys.exit(2)
