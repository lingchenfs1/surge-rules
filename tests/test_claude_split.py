import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
import build_ai as b
import update_claude as c
from claude_rules import belongs_to_claude
ROOT=Path(__file__).parents[1]
class ClaudeSplitTests(unittest.TestCase):
    def setUp(self):
        self.claude=json.loads((ROOT/'config/claude.json').read_text())
        self.ai=json.loads((ROOT/'config/ai-update.json').read_text())
    def test_claude_cannot_reenter_ai_but_shared_stays(self):
        rows=list(b.parse('DOMAIN-SUFFIX,anthropic.com\nDOMAIN,api.anthropic.com\nDOMAIN-KEYWORD,claude\nDOMAIN,anthropic.auth0.com\nDOMAIN-SUFFIX,auth0.com\nDOMAIN-SUFFIX,intercom.io\nDOMAIN-SUFFIX,chatgpt.com\nIP-ASN,399358,no-resolve\nIP-CIDR,160.79.104.0/21,no-resolve'))
        kept=b.select_ai(rows,rows,[],self.ai,self.claude)[0]
        self.assertEqual({r[1] for r in kept},{'auth0.com','intercom.io','chatgpt.com'})
        self.assertEqual(kept,b.select_ai(kept,rows,[],self.ai,self.claude)[0])
    def test_review_candidate_excluded_from_ai(self):
        self.assertTrue(belongs_to_claude(('DOMAIN','api.antspace.dev'),self.claude))
        self.assertFalse(belongs_to_claude(('DOMAIN','other.auth0.com'),self.claude))
    def test_unknown_root_and_shared_not_adopted_as_core(self):
        source={'family':'new-source'}
        rows=list(b.parse('DOMAIN-SUFFIX,new-example.com\nDOMAIN-SUFFIX,intercom.io\nDOMAIN-SUFFIX,anthropic.com\nDOMAIN-KEYWORD,datadog'))
        core,shared,pending=c.select(self.claude,[(source,b'',rows)])
        self.assertNotIn(('DOMAIN-SUFFIX','intercom.io'),core)
        self.assertIn(('DOMAIN-SUFFIX','intercom.io'),shared)
        self.assertTrue(any(x['rule']=='DOMAIN-SUFFIX,new-example.com' for x in pending))
    def test_core_uses_current_inbound_networks(self):
        core,_,_=c.select(self.claude,[])
        self.assertIn(('IP-CIDR','160.79.104.0/23','no-resolve'),core)
        self.assertIn(('IP-CIDR','153.61.224.0/22','no-resolve'),core)
        self.assertIn(('IP-CIDR6','2607:6bc0::/48','no-resolve'),core)
        self.assertNotIn(('IP-CIDR6','2607:6bc0::/32','no-resolve'),core)
    def test_geosite_parser(self):
        self.assertEqual(c.parse_source('claude.ai\nfull:example.com @telemetry # note','v2fly'),[('DOMAIN-SUFFIX','claude.ai'),('DOMAIN','example.com')])
if __name__=='__main__':unittest.main()
