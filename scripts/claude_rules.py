"""Shared Claude ownership boundaries used by Claude and general-AI builders."""
import ipaddress

def belongs_to_claude(rule, config, dedicated=()):
    kind,value=rule[:2]
    core=[tuple(r.split(',')) for r in config['core_rules']]+list(dedicated)
    suffixes={r[1] for r in core if r[0]=='DOMAIN-SUFFIX'} | set(config.get('excluded_ai_roots', []))
    exact={r[1] for r in core if r[0]=='DOMAIN'}
    if kind in ('DOMAIN','DOMAIN-SUFFIX'):
        return value in exact or any(value==d or value.endswith('.'+d) for d in suffixes)
    if kind=='DOMAIN-KEYWORD':
        return any(value.lower() in d for d in suffixes|exact)
    if kind=='URL-REGEX':
        plain=value.lower().replace('\\.','.')
        return any(d in plain for d in suffixes|exact) or 'claude' in plain or 'anthropic' in plain
    if kind=='IP-ASN':return value=='399358'
    if kind in ('IP-CIDR','IP-CIDR6'):
        network=ipaddress.ip_network(value)
        ranges=[r[1] for r in core if r[0] in ('IP-CIDR','IP-CIDR6')]+config['retired_ai_networks']
        return any(network.version==ipaddress.ip_network(d).version and network.subnet_of(ipaddress.ip_network(d)) for d in ranges)
    return False
