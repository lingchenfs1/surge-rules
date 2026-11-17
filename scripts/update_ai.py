#!/usr/bin/env python3
"""Download all fixed AI sources, build in isolation, then publish validated files."""
import concurrent.futures
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse
import build_ai
from check_privacy import check_text
ROOT=Path(__file__).resolve().parents[1]

def fetch(source):
    url=source['url'];u=urlparse(url)
    if u.scheme!='https' or u.hostname not in ('raw.githubusercontent.com','ruleset.skk.moe') or u.username or u.password or u.query:
        raise ValueError('Unexpected upstream URL')
    if not re.fullmatch(r'\d{2}\.list',source['file']):raise ValueError('Invalid snapshot filename')
    result=subprocess.run(['curl','--fail','--silent','--show-error','--location','--proto','=https','--proto-redir','=https','--max-time','45','--max-filesize','2000000','--retry','2','--user-agent','Surge/6.10.0',url],capture_output=True,check=True)
    data=result.stdout
    if len(data)>2_000_000:raise ValueError('AI source too large')
    text=data.decode('utf-8-sig')
    if check_text(text):raise ValueError('Privacy check failed for source '+source['file'])
    parsed=list(build_ai.parse(text,source['extended_matching']))
    if not parsed:raise ValueError('Empty source '+source['file'])
    updated=dict(source,sha256=hashlib.sha256(data).hexdigest(),lines=len(parsed))
    return updated,data

def main():
    manifest=json.loads((ROOT/'sources/ai/manifest.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(5) as pool:
        downloaded=list(pool.map(fetch,manifest['sources']))
    # A fetch, parse, privacy or build failure leaves current publication files untouched.
    with tempfile.TemporaryDirectory() as directory:
        stage=Path(directory)
        for d in ('sources/ai','config','rules','snippets','docs'):(stage/d).mkdir(parents=True,exist_ok=True)
        for file in ('sources/ai/manual.list','config/ai-update.json','rules/AI.list','rules/Meta.list','rules/Claude.list','config/claude.json'):
            shutil.copyfile(ROOT/file,stage/file)
        for source,data in downloaded:(stage/'sources/ai'/source['file']).write_bytes(data)
        manifest['sources']=[s for s,d in downloaded]
        (stage/'sources/ai/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        build_ai.main(stage)
        files=['rules/AI.list','snippets/AI.txt','docs/ai-build.json','sources/ai/manifest.json']+['sources/ai/'+s['file'] for s,d in downloaded]
        for file in files:
            if check_text((stage/file).read_text()):raise ValueError('Privacy check failed before publishing '+file)
        for file in files:shutil.copyfile(stage/file,ROOT/file)
if __name__=='__main__':main()
