#!/usr/bin/env python3
"""Build AI snapshot from public source snapshots plus sanitized manual rules."""
import hashlib
import json
import ipaddress
import re
from claude_rules import belongs_to_claude
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
        kind, value = parts[:2]
        if kind in ('DOMAIN','DOMAIN-SUFFIX'):
            if not re.fullmatch(r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z][a-zA-Z0-9-]*', value):
                raise ValueError('Invalid domain')
            parts[1] = value.lower()
        elif kind in ('IP-CIDR','IP-CIDR6'):
            network = ipaddress.ip_network(value, strict=True)
            if not network.is_global:
                raise ValueError('Non-public network')
        elif kind == 'IP-ASN' and (not value.isdigit() or not 1 <= int(value) <= 4294967295):
            raise ValueError('Invalid ASN')
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


def is_meta(rule, meta_rules, roots):
    kind, value = rule[:2]
    domains = set(roots) | {r[1] for r in meta_rules if r[0] in ('DOMAIN','DOMAIN-SUFFIX')}
    if kind in ('DOMAIN','DOMAIN-SUFFIX'):
        # A new parent suffix which would encompass a Meta root is also excluded.
        return any(value == d or value.endswith('.'+d) or (kind == 'DOMAIN-SUFFIX' and d.endswith('.'+value)) for d in domains)
    if kind == 'DOMAIN-KEYWORD':
        return any(value.lower() in d for d in domains)
    if kind == 'IP-ASN':
        return any(r[:2] == rule[:2] for r in meta_rules)
    if kind == 'URL-REGEX':
        plain = value.lower().replace('\\.', '.')
        return any(d in plain for d in domains) or any(w in plain for w in ('meta', 'facebook', 'instagram', 'whatsapp', 'oculus', 'muse'))
    return False


def select_ai(existing, incoming, meta_rules, config, claude_config=None, claude_rules=()):
    kept, removed, pending = [], [], []
    existing = set(existing)
    for r in dict.fromkeys(list(sorted(existing)) + incoming):
        if claude_config and belongs_to_claude(r, claude_config, claude_rules):
            continue
        if is_meta(r, meta_rules, config['meta_roots']):
            removed.append(','.join(r));continue
        if r not in existing:
            if r[0] not in ('DOMAIN','DOMAIN-SUFFIX'):
                pending.append({'rule': ','.join(r), 'reason':'New keyword/IP/ASN/URL rule requires review'});continue
            if r[1] in config['blocked_new_suffixes']:
                pending.append({'rule': ','.join(r), 'reason':'Shared platform root requires review'});continue
        kept.append(r)
    kept, covered, duplicates = reduce_rules(kept)
    added = set(kept) - existing
    if len(added) > config['max_additions']:
        raise ValueError('Too many new AI rules; review before publication')
    kept = sorted(kept, key=lambda r: (r[0], r[1:]))
    return kept, sorted(set(removed)), pending, covered, duplicates, added


def main(root=ROOT):
    folder = root/'sources/ai'
    manifest=json.loads((folder/'manifest.json').read_text())
    config=json.loads((root/'config/ai-update.json').read_text())
    claude_config=json.loads((root/'config/claude.json').read_text())
    claude_rules=list(parse((root/'rules/Claude.list').read_text()))
    existing=list(parse((root/'rules/AI.list').read_text()))
    meta_rules=list(parse((root/'rules/Meta.list').read_text()))
    rows=list(parse((folder/'manual.list').read_text()))
    provenance={r:{'manual'} for r in rows}
    for source in manifest['sources']:
        data=(folder/source['file']).read_bytes()
        if hashlib.sha256(data).hexdigest()!=source['sha256']:
            raise ValueError('Source snapshot hash mismatch: '+source['file'])
        parsed=list(parse(data.decode('utf-8-sig'), source['extended_matching']))
        if not parsed:raise ValueError('Empty AI source')
        for r in parsed:
            rows.append(r);provenance.setdefault(r,set()).add(source['url'])
    kept, excluded, pending, covered, duplicates, added = select_ai(existing, rows, meta_rules, config, claude_config, claude_rules)
    excluded_claude=sorted({','.join(r) for r in existing+rows if belongs_to_claude(r,claude_config,claude_rules)})
    header='# AI routing | auto-maintained; see docs/AI.md\n# Meta and Claude dedicated rules excluded. Sources: sources/ai/\n# Apple Intelligence matching options are preserved per rule.\n'
    (root/'rules/AI.list').write_text(header+'\n'.join(','.join(r) for r in kept)+'\n')
    (root/'snippets/AI.txt').write_text('# Paste inside [Rule]. AI must be an existing policy/group.\n# Meta and Claude excluded; optional process rules are separate: AI-processes.txt\n'+'\n'.join(','.join(list(r[:2])+['AI']+list(r[2:])) for r in kept)+'\n')
    report={'rule_count':len(kept), 'excluded_meta':excluded, 'excluded_claude':excluded_claude, 'pending':pending,
        'rules':[{'rule':','.join(r),'sources':sorted(provenance.get(r, {'retained from previous publication'}))} for r in kept]}
    (root/'docs/ai-build.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(f'{len(kept)} AI rules; {len(added)} additions; {len(excluded)} Meta exclusions; {len(excluded_claude)} Claude exclusions; {len(pending)} pending')

if __name__=='__main__':main()
