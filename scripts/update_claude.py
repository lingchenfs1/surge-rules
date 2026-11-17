#!/usr/bin/env python3
"""Cross-check Claude lists; publish dedicated and opt-in shared rules separately."""
import concurrent.futures
import hashlib
import json
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from build_ai import parse, reduce_rules
from claude_rules import belongs_to_claude
from check_privacy import check_text
ROOT=Path(__file__).resolve().parents[1]

def parse_source(text,format):
    if format=='surge':return list(parse(text))
    rows=[]
    for line in text.splitlines():
        line=line.split('#',1)[0].strip()
        if not line:continue
        value=line.split()[0]
        if value.startswith('full:'):rows.append('DOMAIN,'+value[5:])
        elif ':' not in value:rows.append('DOMAIN-SUFFIX,'+value)
        else:raise ValueError('Unsupported geosite entry')
    return list(parse('\n'.join(rows)))

def fetch(source):
    u=urlparse(source['url'])
    if u.scheme!='https' or u.hostname!='raw.githubusercontent.com' or u.query or u.username:raise ValueError('Unexpected source')
    data=subprocess.check_output(['curl','-fLsS','--proto','=https','--proto-redir','=https','--max-time','45','--max-filesize','2000000','--retry','2',source['url']])
    text=data.decode('utf-8-sig')
    if check_text(text):raise ValueError('Privacy check failed: '+source['name'])
    rows=parse_source(text,source['format'])
    if not rows:raise ValueError('Empty Claude source')
    return source,data,rows

def select(config, snapshots, existing=()):
    approved=set(parse('\n'.join(config['core_rules'])))|set(existing)
    shared=set(parse('\n'.join(config['shared_rules'])))
    evidence={}
    for source,data,rows in snapshots:
        for r in rows:evidence.setdefault(r,set()).add(source['family'])
    pending=[]
    for r,families in sorted(evidence.items()):
        if r in approved or r in shared:continue
        if r[0] not in ('DOMAIN','DOMAIN-SUFFIX'):
            pending.append({'rule':','.join(r),'reason':'Non-domain rule not auto-adopted'});continue
        if r[1] in {v[1] for v in shared}:
            pending.append({'rule':','.join(r),'reason':'Shared dependency; not core'});continue
        # Never treat a shared platform root as Claude-specific based on votes.
        branded=any(r[1]==d[1] or r[1].endswith('.'+d[1]) for d in approved if d[0]=='DOMAIN-SUFFIX')
        if branded:approved.add(r)
        else:pending.append({'rule':','.join(r),'families':sorted(families),'reason':'New root or third-party host requires ownership review'})
    kept=sorted(reduce_rules(list(approved))[0])
    if len(set(kept)-set(existing)-set(parse('\n'.join(config['core_rules']))))>config['max_additions']:raise ValueError('Too many Claude additions')
    return kept,sorted(reduce_rules(list(shared))[0]),pending

def render(rows, name, policy=False):
    lines=[]
    for r in rows:
        lines.append(','.join(list(r[:2])+(['CLAUDE'] if policy else [])+list(r[2:])))
    return '# '+name+' | See docs/Claude.md\n'+'\n'.join(lines)+'\n'

def main():
    config=json.loads((ROOT/'config/claude.json').read_text())
    current=ROOT/'rules/Claude.list'
    existing=list(parse(current.read_text())) if current.exists() else []
    with concurrent.futures.ThreadPoolExecutor(5) as pool:snapshots=list(pool.map(fetch,config['sources']))
    core,shared,pending=select(config,snapshots,existing)
    outputs={'rules/Claude.list':render(core,'Claude dedicated rules'),
        'rules/Claude-Shared.list':render(shared,'OPTIONAL shared dependencies; may affect other apps'),
        'snippets/Claude.txt':render(core,'Claude dedicated rules',True),
        'snippets/Claude-Shared.txt':render(shared,'OPTIONAL shared dependencies',True)}
    report={'core_rule_count':len(core),'shared_rule_count':len(shared),'pending':pending,'sources':[]}
    for s,data,rows in snapshots:
        outputs['sources/claude/'+s['file']]=data.decode('utf-8-sig')
        report['sources'].append(dict(s,sha256=hashlib.sha256(data).hexdigest(),rule_count=len(rows)))
    outputs['docs/claude-sync.json']=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
    for file,text in outputs.items():
        if check_text(text):raise ValueError('Publication privacy check failed: '+file)
    for file,text in outputs.items():(ROOT/file).write_text(text)
    print(f'{len(core)} Claude core; {len(shared)} optional shared; {len(pending)} pending candidates')
if __name__=='__main__':main()
