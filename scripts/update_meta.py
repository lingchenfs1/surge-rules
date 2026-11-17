#!/usr/bin/env python3
"""Add-only Meta upstream sync. Standard library only; upstream data is never executed."""
import concurrent.futures
import hashlib
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_RE = re.compile(r'(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z](?:[a-z0-9-]{0,61}[a-z0-9])?$')


def parse(text):
    rules = set()
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line or line.startswith('include:'):
            continue  # explicitly configured include files are fetched separately
        if ',' in line:
            fields = line.split(',')
            kind, value = fields[:2]
        elif line.startswith('full:'):
            kind, value = 'DOMAIN', line[5:].split()[0]
        elif ':' not in line:
            kind, value = 'DOMAIN-SUFFIX', line.split()[0]
        else:
            continue
        value = value.lower()
        if kind in ('DOMAIN', 'DOMAIN-SUFFIX') and DOMAIN_RE.fullmatch(value):
            rules.add((kind, value))
    return rules


def covered(rule, rules):
    kind, value = rule
    return rule in rules or any(t == 'DOMAIN-SUFFIX' and (value == d or value.endswith('.' + d)) for t, d in rules)


def dedupe(rules):
    result = set(rules)
    for rule in rules:
        if covered(rule, rules - {rule}):
            result.discard(rule)
    return result


def select(existing, snapshots, config):
    evidence = {}
    for source, text in snapshots:
        parsed = parse(text)
        if not parsed:
            raise ValueError('Empty or invalid source: ' + source['name'])
        for rule in parsed:
            evidence.setdefault(rule, set()).add(source['family'])
    selected, pending = set(existing), []
    excluded = set(config['excluded_domains'])
    for rule, families in sorted(evidence.items()):
        if covered(rule, existing):
            continue
        kind, value = rule
        if value in excluded or any(value == d or value.endswith('.' + d) for d in config['blocked_suffixes']):
            continue
        # Existing explicit hostname must not be silently widened to its entire suffix.
        if kind == 'DOMAIN-SUFFIX' and any(t == 'DOMAIN' and (d == value or d.endswith('.' + value)) for t, d in existing):
            reason = 'Would broaden an existing exact hostname'
        elif len(families) < config['minimum_families']:
            reason = 'Needs a second source family'
        else:
            selected.add(rule)
            continue
        pending.append({'rule': ','.join(rule), 'families': sorted(families), 'reason': reason})
    selected = dedupe(selected)
    added = {r for r in selected if not covered(r, existing)}
    if len(added) > config['max_additions']:
        raise ValueError('Too many additions; review upstream changes before publishing')
    return selected, pending, added


def fetch(source):
    request = Request(source['url'], headers={'User-Agent': 'surge-rules-updater'})
    with urlopen(request, timeout=30) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError('Source exceeds size limit')
    return source, data.decode('utf-8-sig')


def render(selected, asns):
    rows = [','.join(r) for r in sorted(selected, key=lambda r: (r[0] != 'DOMAIN-SUFFIX', r[1]))]
    rows += ['IP-ASN,' + a + ',no-resolve' for a in sorted(asns, key=int)]
    rule_file = '# Meta family | auto-maintained; see docs/Automation.md\n' + '\n'.join(rows) + '\n'
    snippets = []
    for row in rows:
        fields = row.split(',')
        snippets.append(','.join(fields[:2] + ['META'] + (fields[2:] if fields[0] == 'IP-ASN' else ['extended-matching'])))
    snippet_file = '# Paste into [Rule]; replace META with an existing policy.\n# Applies to all devices; place before device-wide rules and FINAL.\n' + '\n'.join(snippets) + '\n'
    return rule_file, snippet_file


def main():
    config = json.loads((ROOT / 'config/meta-upstreams.json').read_text())
    current = (ROOT / 'rules/Meta.list').read_text()
    existing = parse(current)
    asns = {line.split(',')[1] for line in current.splitlines() if line.startswith('IP-ASN,')}
    if not existing or asns != {'11917', '32934', '63293'}:
        raise ValueError('Unexpected local rules or ASN baseline')
    # Fetch all sources successfully before writing anything. No partial-source publication.
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        snapshots = list(pool.map(fetch, config['sources']))
    selected, pending, added = select(existing, snapshots, config)
    rule_file, snippet_file = render(selected, asns)
    report = {
        'rule_count': len(selected) + len(asns),
        'pending': pending,
        'sources': [{'name': s['name'], 'family': s['family'], 'url': s['url'],
                     'sha256': hashlib.sha256(t.encode()).hexdigest(), 'domain_rules': len(parse(t))}
                    for s, t in snapshots],
    }
    # No wall-clock timestamp: unchanged upstreams produce no empty daily commits.
    (ROOT / 'rules/Meta.list').write_text(rule_file)
    (ROOT / 'snippets/Meta.txt').write_text(snippet_file)
    (ROOT / 'docs/meta-sync.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f'{len(selected) + len(asns)} rules; {len(added)} additions; {len(pending)} pending')
    for rule in sorted(added):
        print('Added: ' + ','.join(rule))


if __name__ == '__main__':
    main()
