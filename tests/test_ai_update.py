import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
import build_ai as b
import update_ai as u
from check_privacy import check_text
class AIUpdateTests(unittest.TestCase):
    def setUp(self):
        self.cfg={'meta_roots':['meta.ai','metaaivm.com'],'blocked_new_suffixes':['cloudflare.com'],'max_additions':25}
        self.meta=[('DOMAIN-SUFFIX','facebook.com'),('IP-ASN','32934','no-resolve')]
    def test_meta_removed_and_cannot_reenter(self):
        rows=[('DOMAIN-SUFFIX','meta.ai'),('DOMAIN','hatch-api.meta.ai'),('DOMAIN-SUFFIX','facebook.com'),('IP-ASN','32934','no-resolve'),('DOMAIN-KEYWORD','facebook'),('URL-REGEX',r'https://www\.meta\.ai/.*'),('DOMAIN-SUFFIX','openai.com')]
        kept,removed,*_=b.select_ai(rows,rows,self.meta,self.cfg)
        self.assertEqual(kept,[('DOMAIN-SUFFIX','openai.com')]);self.assertEqual(len(removed),6)
        self.assertEqual(b.select_ai(kept,rows,self.meta,self.cfg)[0],kept)
    def test_new_domains_accepted_broad_candidates_pending(self):
        rows=[('DOMAIN-SUFFIX','new.example'),('DOMAIN-KEYWORD','new'),('IP-ASN','12345'),('DOMAIN-SUFFIX','cloudflare.com')]
        kept,_,pending,*_=b.select_ai([],rows,self.meta,self.cfg)
        self.assertEqual(kept,[('DOMAIN-SUFFIX','new.example')]);self.assertEqual(len(pending),3)
    def test_idempotent_and_retains_non_meta(self):
        old=[('DOMAIN-SUFFIX','old.example')];new=[('DOMAIN','new.example')]
        first=b.select_ai(old,new,self.meta,self.cfg)[0]
        self.assertEqual(first,b.select_ai(first,new,self.meta,self.cfg)[0]);self.assertIn(old[0],first)
    def test_limit_and_invalid_domains(self):
        self.cfg['max_additions']=0
        with self.assertRaises(ValueError):b.select_ai([],[('DOMAIN','new.example')],self.meta,self.cfg)
        with self.assertRaises(ValueError):list(b.parse('DOMAIN,$(bad).com'))
    def test_fetch_failure_leaves_publication_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'sources/ai').mkdir(parents=True);(root/'rules').mkdir()
            (root/'sources/ai/manifest.json').write_text(json.dumps({'sources':[{'url':'unused'}]}))
            target=root/'rules/AI.list';target.write_text('unchanged')
            with patch.object(u,'ROOT',root),patch.object(u,'fetch',side_effect=ValueError('download failed')):
                with self.assertRaises(ValueError):u.main()
            self.assertEqual(target.read_text(),'unchanged')
    def test_privacy_values_not_logged(self):
        email='someone'+'@'+'gmail.com'
        self.assertIn('personal email',check_text(email))
        self.assertEqual(check_text('github-actions[bot]@users.noreply.github.com'),[])
if __name__=='__main__':unittest.main()
