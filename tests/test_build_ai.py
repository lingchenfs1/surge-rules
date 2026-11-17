import importlib.util
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('build_ai',Path(__file__).parents[1]/'scripts/build_ai.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class AIBuildTests(unittest.TestCase):
    def test_domain_coverage_preserves_flags_and_other_types(self):
        rows=list(m.parse('DOMAIN,api.example.com\nDOMAIN-SUFFIX,example.com\nDOMAIN,api.example.com,extended-matching\nDOMAIN-KEYWORD,sora\nIP-ASN,20473,no-resolve\nDOMAIN-SUFFIX,example.com'))
        kept,removed,duplicates=m.reduce_rules(rows)
        self.assertEqual(len(removed),1);self.assertEqual(duplicates,1)
        self.assertIn(('DOMAIN','api.example.com','extended-matching'),kept)
        self.assertIn(('IP-ASN','20473','no-resolve'),kept)
        self.assertIn(('DOMAIN-KEYWORD','sora'),kept)
    def test_apple_extended_matching_stays_local(self):
        self.assertEqual(list(m.parse('DOMAIN,apple-relay.apple.com',True)),[('DOMAIN','apple-relay.apple.com','extended-matching')])
        self.assertEqual(list(m.parse('DOMAIN,example.com')),[('DOMAIN','example.com')])
    def test_unknown_input_fails(self):
        with self.assertRaises(ValueError):list(m.parse('DOMAIN,example.com,AI'))
        with self.assertRaises(ValueError):list(m.parse('PROCESS-NAME,private-path'))
if __name__=='__main__':unittest.main()
