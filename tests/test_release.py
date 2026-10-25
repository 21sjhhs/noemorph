"""Release acceptance: actual ledger runs, preserved limits, safe packaging and config."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from io import BytesIO
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_run import audit
from knowledge_map import main as export_map, state_to_graph
from package_skill import package
from release_scan import scan
from run_card import validate_config, CardHandler
from validate_skill import validate


def direction(round_no, role, index):
    return {"id": f"R{round_no}-A{role}-{index}", "question": f"R{round_no} role {role} distinct query {index}?",
            "anchor_ids": ["S"], "logical_move": f"abstract operator {role}",
            "discovery_target": "Unknown", "search_route": "Pending retrieval", "bridge_test": "Check conditions",
            "novelty_reason": "Structural fixture only", "unknowns": ["Not actual research"]}


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.state_path = self.folder / "state.json"
        self.counter = 0

    def call(self, *args, success=True):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/run_state.py'), *map(str,args)], capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stderr)
        return result

    def save(self, data):
        self.counter += 1
        path = self.folder / f"record{self.counter}.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def init(self, rounds=1):
        self.call('init','--state',self.state_path,'--question','Q?','--rounds',rounds,'--agents',4,'--top-n',1)
        self.call('decomp','--state',self.state_path,'--input',self.save({
            'concepts':[{'id':'S','label':'S','kind':'entity'}], 'relations':[], 'open_questions':[]}))

    def breadth(self, rn):
        for role in range(2,6):
            self.call('breadth','--state',self.state_path,'--input',self.save({
                'round':rn,'agent_id':f'agent{role}', 'directions':[direction(rn,role,i) for i in range(1,6)]}))

    def finish_round(self, rn, supported_without_source=False):
        self.breadth(rn)
        ident = f'R{rn}-A2-1'
        self.call('select','--state',self.state_path,'--ids',ident)
        item={'round':rn,'agent_id':'structural-test-fixture','direction_id':ident,
              'hops':[{'question':f'Attempt {i}?','finding':'No searched evidence; fixture only', 'relation':'unresolved boundary check',
                       'evidence_refs':[], 'status':'verified_direct' if supported_without_source else 'unresolved'} for i in range(3)],
              'new_concepts':[], 'bridges':[], 'boundary_change':'Pending evidence', 'limits':['Fixture only'], 'unresolved':['No research performed']}
        self.call('depth','--state',self.state_path,'--input',self.save(item))
        self.call('close','--state',self.state_path)

    def test_full_two_rounds_twenty_directions_and_exact_stop(self):
        self.init(rounds=2)
        self.finish_round(1)
        self.assertEqual(json.loads(self.state_path.read_text())['phase'],'breadth')
        self.finish_round(2)
        state=json.loads(self.state_path.read_text())
        checked=audit(state, require_complete=True)
        self.assertTrue(checked['ok'],checked)
        self.assertEqual(checked['counts'],{'rounds':2,'directions':40,'selected':2,'attempts':6})
        self.call('close','--state',self.state_path, success=False)
        graph=state_to_graph(state)
        directions=[n for n in graph['nodes'] if n['type']=='direction']
        self.assertEqual(len(directions),40)
        self.assertEqual(sum(n['selected'] for n in directions),2)
        self.assertEqual(sum(n['status']=='frontier' for n in directions),38)

    def test_original_engine_accepts_claim_without_sources_but_readonly_audit_flags_it(self):
        self.init();self.finish_round(1,supported_without_source=True)
        state=json.loads(self.state_path.read_text())
        before=self.state_path.read_bytes()
        result=audit(state)
        self.assertFalse(result['ok'])
        self.assertIn('supported_claim_without_recorded_source',{e['code'] for e in result['errors']})
        self.assertEqual(self.state_path.read_bytes(),before)

    def test_higher_configured_depth_checked_without_modifying_engine(self):
        self.init();self.finish_round(1)
        state=json.loads(self.state_path.read_text())
        config=validate_config({'question':'Q?','macro_rounds':1,'top_n':1,'depth_hops':5,'scope':'Do not add excluded topics'})
        result=audit(state,config)
        self.assertIn('configured_depth_not_reached',{e['code'] for e in result['errors']})
        self.assertFalse(result['ok'])

    def test_early_selection_and_duplicate_questions_are_rejected(self):
        self.init()
        self.call('select','--state',self.state_path,'--ids','R1-A2-1',success=False)
        rows=[direction(1,2,i) for i in range(1,6)]
        rows[-1]['question']=rows[0]['question'].upper().replace('?','!!!')
        self.call('breadth','--state',self.state_path,'--input',self.save({'round':1,'agent_id':'agent2','directions':rows}),success=False)
        self.assertEqual(json.loads(self.state_path.read_text())['history'][0]['breadth'],{})

    def test_forged_completion_and_wrong_breadth_protocol_fail_audit(self):
        self.init();self.finish_round(1)
        state=json.loads(self.state_path.read_text())
        state['config']['agents']=5
        state['history'][0]['closed']=False
        result=audit(state)
        codes={e['code'] for e in result['errors']}
        self.assertIn('maintained_protocol_requires_four_breadth_submitters',codes)
        self.assertIn('premature_completion',codes)

    def test_cross_round_literal_repeats_are_flagged_for_semantic_review(self):
        self.init(2);self.finish_round(1);self.finish_round(2)
        state=json.loads(self.state_path.read_text())
        first=state['history'][0]['breadth']['agent2']['directions'][0]
        state['history'][1]['breadth']['agent2']['directions'][0]['question']=first['question']
        result=audit(state)
        self.assertIn('cross_round_question_repeated_review_conditions_and_novelty',{w['code'] for w in result['warnings']})

    def test_legacy_configuration_normalizes_and_retains_scope(self):
        config=validate_config({'schema_version':'socrates-run-config/1.0','question':'Q?','scope':'Limit C','ui_language':'en','presentation_languages':['zh-CN']})
        self.assertEqual(config['schema_version'],'noemorph-run-config/1.0')
        self.assertEqual(config['scope'],'Limit C')
        self.assertEqual(config['research_language_policy'],'unconstrained')

    def test_branded_card_submission_returns_config_and_rejects_wrong_origin(self):
        handler=CardHandler.__new__(CardHandler)
        data=validate_config({'question':'Q?','scope':'Exclude topic Z','ui_language':'en','presentation_languages':['zh-CN']})
        body=json.dumps(data).encode()
        handler.path='/api/config'
        handler.headers={'Host':'127.0.0.1:8765','Origin':'http://127.0.0.1:8765','X-Noemorph-Token':'local-test-token','Content-Length':str(len(body))}
        handler.rfile=BytesIO(body);handler.respond=Mock()
        handler.server=SimpleNamespace(expected_origin='http://127.0.0.1:8765',card_token='local-test-token',config_path=self.folder/'run-config.json',shutdown=Mock())
        handler.do_POST()
        self.assertEqual(json.loads(handler.server.config_path.read_text()),data)
        handler.server.shutdown.assert_called_once()
        handler.headers['Origin']='https://elsewhere.example'
        handler.respond.reset_mock();handler.server.shutdown.reset_mock()
        handler.do_POST()
        self.assertEqual(handler.respond.call_args[0][0],403)
        handler.server.shutdown.assert_not_called()

    def test_single_language_export_keeps_independent_ui_preference(self):
        source=json.loads((ROOT/'examples/demo.graph.json').read_text())
        original=self.save(source)
        config=self.save(validate_config({'question':'Q?','ui_language':'en','presentation_languages':['zh-CN']}))
        output=self.folder/'single.html'
        self.assertEqual(export_map(['--input',str(original),'--config',str(config),'--output',str(output)]),0)
        exported=json.loads(output.with_suffix('.graph.json').read_text())
        self.assertEqual(exported['view']['ui_language'],'en')
        self.assertEqual(exported['meta']['language'],'zh-CN')

    def test_packaged_skill_installs_and_validates_without_external_dependencies(self):
        output=self.folder/'noemorph.zip'
        result=package(ROOT,output)
        self.assertGreater(result['files'],30)
        with zipfile.ZipFile(output) as archive:
            names=archive.namelist()
            self.assertTrue(all(n.startswith('noemorph/') and '..' not in Path(n).parts for n in names))
            self.assertTrue(all('/.git/' not in n and '/local-runs/' not in n and '/runs/' not in n for n in names))
            archive.extractall(self.folder/'install')
        installed=self.folder/'install/noemorph'
        self.assertTrue(validate(installed)['ok'])
        check=subprocess.run([sys.executable,str(installed/'scripts/check_upstream.py')],capture_output=True,text=True)
        self.assertEqual(check.returncode,0,check.stderr)
        result=subprocess.run([sys.executable,str(installed/'scripts/run_card.py'),'prompt','--question','Q?'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['question'],'Q?')
        # Reversible uninstall consists of removing this one installation directory.
        backup=installed.with_name('noemorph-uninstalled')
        installed.rename(backup)
        self.assertFalse(installed.exists());self.assertTrue((backup/'SKILL.md').is_file())

    def test_equivalent_validator_rejects_directory_mismatch_and_broken_reference(self):
        target=self.folder/'wrong-name';target.mkdir()
        (target/'SKILL.md').write_text('---\nname: noemorph\ndescription: Explore concepts.\n---\nSee [guide](references/missing.md).\n')
        result=validate(target)
        self.assertFalse(result['ok'])
        self.assertTrue(any('directory' in e for e in result['errors']))
        self.assertTrue(any('unresolved' in e for e in result['errors']))

    def test_release_scan_redacts_token_and_personal_path(self):
        path=self.folder/'leak.txt'
        key='gh'+'p_'+'A'*40
        personal='/'+'Users'+'/private-person/project'
        path.write_text(key+'\n'+personal)
        result=scan(self.folder)
        self.assertFalse(result['ok'])
        encoded=json.dumps(result)
        self.assertNotIn(key,encoded);self.assertNotIn(personal,encoded)
        self.assertEqual({r['kind'] for r in result['findings']},{'github_token','personal_absolute_path'})


if __name__=='__main__':unittest.main()
