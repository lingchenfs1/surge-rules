#!/usr/bin/env python3
"""Build AI snapshot from public source snapshots plus sanitized manual rules."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TYPES = {'DOMAIN','DOMAIN-SUFFIX','DOMAIN-KEYWORD','IP-CIDR','IP-CIDR6','IP-ASN','URL-REGEX'}


def parse(text, extended=False):
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(',')
        if len(parts) < 2 or parts[0] not in TYPES:
            raise ValueError('Unsupported rule: ' + line)
        if any(option not in ('no-resolve','extended-matching') for option in parts[2:]):
            raise ValueError('Unsupported options: ' + line)
        if extended and parts[0].startswith('DOMAIN') and 'extended-matching' not in parts:
            parts.append('extended-matching')
        yield tuple(parts[:2] + sorted(set(parts[2:])))


def reduce_rules(rows):
    unique = list(dict.fromkeys(rows))
    suffixes = [r for r in unique if r[0]=='DOMAIN-SUFFIX']
    removed = []
    kept = []
    for r in unique:
        covering = next((s for s in suffixes if s != r and r[0] in ('DOMAIN','DOMAIN-SUFFIX')
            and (r[1] == s[1] or r[1].endswith('.' + s[1])) and r[2:] == s[2:]), None)
        if covering:
            removed.append({'rule': ','.join(r), 'covered_by': ','.join(covering)})
        else:
            kept.append(r)
    return kept, removed, len(rows)-len(unique)


def main():
    folder = ROOT/'sources/ai'
    manifest=json.loads((folder/'manifest.json').read_text())
    rows=list(parse((folder/'manual.list').read_text()))
    provenance={r:{'manual'} for r in rows}
    for source in manifest['sources']:
        data=(folder/source['file']).read_bytes()
        if hashlib.sha256(data).hexdigest()!=source['sha256']:
            raise ValueError('Source snapshot hash mismatch: '+source['file'])
        for r in parse(data.decode('utf-8-sig'), source['extended_matching']):
            rows.append(r);provenance.setdefault(r,set()).add(source['url'])
    kept,removed,duplicates=reduce_rules(rows)
    header='# AI routing snapshot | 2026-11-17\n# Sources and broad-match notes: docs/AI.md\n# Public source snapshots: sources/ai/ | Includes shared services and meta.ai.\n# Do not add outer extended-matching if preserving the exported matching options.\n'
    (ROOT/'rules/AI.list').write_text(header+'\n'.join(','.join(r) for r in kept)+'\n')
    (ROOT/'snippets/AI.txt').write_text('# Paste inside [Rule]. AI must be an existing policy/group.\n# Optional process rules are separate: AI-processes.txt\n'+'\n'.join(','.join(list(r[:2])+['AI']+list(r[2:])) for r in kept)+'\n')
    report={'date':manifest['date'],'expanded_destination_rules':len(rows),'exact_duplicates_removed':duplicates,'covered_domain_rules_removed':removed,'rule_count':len(kept),
        'rules':[{'rule':','.join(r),'sources':sorted(provenance[r])} for r in kept]}
    (ROOT/'docs/ai-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(rows)} expanded -> {len(kept)} unique destination rules; {duplicates} duplicates, {len(removed)} covered domains removed')

if __name__=='__main__':main()
