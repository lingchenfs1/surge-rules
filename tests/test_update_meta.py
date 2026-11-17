import importlib.util
import unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location('update_meta', Path(__file__).parents[1] / 'scripts/update_meta.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class RulesTests(unittest.TestCase):
    def setUp(self):
        self.config = dict(excluded_domains=['old.example'], blocked_suffixes=['shared.example'], minimum_families=2, max_additions=25)
    def snap(self, family, text):
        return ({'name': family, 'family': family}, text)
    def test_parser_rejects_injection_and_broad_rules(self):
        text = 'DOMAIN-SUFFIX,meta.com\nfull:api.meta.ai\nIP-CIDR,1.2.3.4/32\nDOMAIN-KEYWORD,meta\nDOMAIN-SUFFIX,$(evil).com\ninclude:meta'
        self.assertEqual(m.parse(text), {('DOMAIN-SUFFIX','meta.com'),('DOMAIN','api.meta.ai')})
    def test_family_consensus_and_exclusions(self):
        text='new.example\nold.example\nshared.example\napi.shared.example'
        snaps=[self.snap('geosite',text),self.snap('geosite',text)]
        selected,pending,_=m.select(set(),snaps,self.config)
        self.assertFalse(selected);self.assertEqual(len(pending),1)
        selected,_,_=m.select(set(),snaps+[self.snap('blackmatrix7',text)],self.config)
        self.assertEqual(selected,{('DOMAIN-SUFFIX','new.example')})
    def test_parent_deduplication_and_no_removals(self):
        base={('DOMAIN-SUFFIX','keep.example'),('DOMAIN','api.new.example')}
        s,p,a=m.select(base,[self.snap('a','new.example'),self.snap('b','new.example')],self.config)
        self.assertEqual(s,base);self.assertEqual(len(p),1)
        self.assertEqual(m.dedupe({('DOMAIN-SUFFIX','meta.com'),('DOMAIN','api.meta.com'),('DOMAIN-SUFFIX','cdn.meta.com')}),{('DOMAIN-SUFFIX','meta.com')})
    def test_empty_source_and_mass_additions_fail(self):
        with self.assertRaises(ValueError):m.select(set(),[self.snap('a','<html>error</html>')],self.config)
        self.config['max_additions']=0
        with self.assertRaises(ValueError):m.select(set(),[self.snap('a','new.example'),self.snap('b','new.example')],self.config)
    def test_render_is_deterministic(self):
        r,s=m.render({('DOMAIN-SUFFIX','meta.com')},{'32934'})
        self.assertIn('IP-ASN,32934,META,no-resolve',s)
        self.assertIn('DOMAIN-SUFFIX,meta.com,META,extended-matching',s)
        self.assertEqual((r,s),m.render({('DOMAIN-SUFFIX','meta.com')},{'32934'}))
if __name__=='__main__':unittest.main()
