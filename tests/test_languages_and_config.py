import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from graph_languages import (canonical, fingerprint, make_bundle, stamp_translation,
                             validate_bundle, validate_translation, language_issues)
from knowledge_map import main as export_map, render_html
from run_card import DEFAULTS, portable_prompt, render_card, save_config, validate_config


def source_graph():
    return {'schema_version':'1.0', 'meta':{'title':'问题', 'question':'问题是什么？', 'language':'zh-CN'},
        'nodes':[{'id':'q','label':'问题是什么？','type':'question','importance':5,
                  'summary':'保留限定。','details':{'id':'S','typed_queries':['Has(S,P)?'],'status':'尚未解决'},
                  'links':[{'label':'资料','url':'https://example.org/paper','kind':'source'}]}], 'edges':[]}


def translated_graph():
    translated = copy.deepcopy(source_graph())
    translated['meta'].update(language='en', language_label='English', title='Question', question='What is the question?')
    translated['nodes'][0].update(label='What is the question?', summary='Keep the qualification.')
    translated['nodes'][0]['details']['status'] = 'Unresolved'
    translated['nodes'][0]['links'][0]['label'] = 'Reference'
    return translated


class LanguagesTests(unittest.TestCase):
    def test_translation_preserves_machine_fields_and_binds_source(self):
        original = source_graph(); before = copy.deepcopy(original)
        translated = stamp_translation(original, translated_graph(), 'actual-test-translator')
        validate_translation(original, translated)
        self.assertEqual(original, before)
        self.assertEqual(translated['meta']['translation']['source_fingerprint'], fingerprint(original))
        self.assertEqual(translated['nodes'][0]['details']['typed_queries'], ['Has(S,P)?'])

    def test_rejects_changed_id_url_and_evidence(self):
        for mutate in (lambda g: g['nodes'][0].update(id='other'),
                       lambda g: g['nodes'][0]['links'][0].update(url='https://other.org'),
                       lambda g: g['nodes'][0].update(evidence='verified_direct'),
                       lambda g: g['nodes'][0]['details']['typed_queries'].append('Extra(S)?')):
            target = translated_graph(); mutate(target)
            with self.assertRaises(ValueError): stamp_translation(source_graph(), target)

    def test_stale_source_is_rejected_even_when_structure_matches(self):
        original = source_graph(); translated = stamp_translation(original, translated_graph(), 'test')
        original['nodes'][0]['summary'] = '新增了重要限定。'
        with self.assertRaisesRegex(ValueError,'fingerprint'): validate_translation(original, translated)

    def test_bundle_declaration_duplicates_and_unavailable_default(self):
        original = source_graph(); translated = stamp_translation(original, translated_graph(), 'test')
        bundle = make_bundle(original, [translated], 'en'); validate_bundle(bundle)
        self.assertEqual([g['meta']['language'] for g in bundle['graphs']], ['zh-CN','en'])
        with self.assertRaises(ValueError): make_bundle(original, [translated, translated])
        with self.assertRaises(ValueError): make_bundle(original, [translated], 'ja')

    def test_view_changes_do_not_invalidate_translations_but_text_changes_do(self):
        original = source_graph(); first = fingerprint(original)
        original['view'] = {'positions':{'q':{'x':12.5,'y':4}},'ui_language':'en'}
        original['meta']['language_label'] = '简体中文'
        self.assertEqual(fingerprint(original), first)
        original['meta']['question'] += '修订'
        self.assertNotEqual(fingerprint(original), first)

    def test_incomplete_translation_is_rejected_even_with_valid_structure(self):
        translated = translated_graph()
        translated['nodes'][0]['summary'] = '这段中文还没有翻译。'
        with self.assertRaisesRegex(ValueError, '展示文字'):
            stamp_translation(source_graph(), translated, 'test')
        mixed = source_graph()
        mixed['nodes'][0]['details']['note'] = 'This entire sentence was left untranslated in the Chinese language graph.'
        self.assertEqual(language_issues(mixed), ['nodes.0.details.note'])

    def test_final_export_requires_english_even_without_a_config_file(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory); source = folder / 'source.json'; output = folder / 'map.html'
            source.write_text(json.dumps(source_graph()))
            self.assertEqual(export_map(['--input', str(source), '--output', str(output)]), 2)
            self.assertFalse(output.exists())
            self.assertEqual(export_map(['--input', str(source), '--output', str(output), '--allow-incomplete-languages']), 0)

    def test_embedded_configuration_is_checked_when_no_config_flag_is_supplied(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory); source = folder / 'source.json'; output = folder / 'map.html'
            graph = translated_graph(); graph['run_config'] = validate_config({'question':'Q', 'presentation_languages':['ja']})
            source.write_text(json.dumps(graph))
            self.assertEqual(export_map(['--input', str(source), '--output', str(output)]), 2)
            self.assertFalse(output.exists())

    def test_edge_prose_translates_but_evidence_enums_and_reference_urls_are_locked(self):
        original = source_graph(); translated = translated_graph()
        original['edges'] = [{'id':'e','source':'q','target':'q','label':'关联','kind':'related',
            'details':{'from':'原始材料','evidence':'只支持这一批次。','status':'supported_with_limits',
                       'direct_url':'https://example.org/a/very/long/url/that/is/a/reference'}}]
        translated['edges'] = copy.deepcopy(original['edges'])
        translated['edges'][0]['label'] = 'Related'
        translated['edges'][0]['details'].update({'from':'Source material','evidence':'Supports this batch only.'})
        stamp_translation(original, translated, 'test')
        for key in ['direct_url','status']:
            changed = copy.deepcopy(translated); changed['edges'][0]['details'][key] = 'changed'
            with self.assertRaises(ValueError): stamp_translation(original, changed, 'test')
        original['edges'][0]['details']['evidence'] = 'supported_with_limits'
        translated['edges'][0]['details']['evidence'] = 'inferred'
        with self.assertRaises(ValueError): stamp_translation(original, translated, 'test')
        chinese = source_graph()
        chinese['nodes'][0]['details']['refs'] = ['https://example.org/a/very/long/url/that/is/a/reference']
        self.assertEqual(language_issues(chinese), [])

    def test_numeric_encoding_handles_scientific_notation(self):
        self.assertEqual(canonical(1), canonical(1.0))
        self.assertEqual(canonical(1e-6), 'n3eb0c6f7a0b5ed8d')
        with self.assertRaises(ValueError): canonical(9007199254740993)

    def test_offline_html_keeps_all_language_versions(self):
        original = source_graph(); translated = stamp_translation(original, translated_graph(), 'test')
        document = render_html(make_bundle(original, [translated]))
        self.assertIn('What is the question?', document)
        self.assertIn('问题是什么？', document)
        self.assertNotIn('src="languages.js"', document)
        self.assertNotIn('src="i18n.js"', document)

    def test_cli_exports_bundle_and_keeps_original_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory); original=source_graph(); translated=stamp_translation(original, translated_graph(),'test')
            src=folder/'graph.json'; target=folder/'graph.en.json'
            original['view'] = {'positions':{'q':{'x':12,'y':24}},'content_language':'auto'}
            src.write_text(json.dumps(original)); target.write_text(json.dumps(translated)); before=src.read_bytes()
            code=export_map(['--input',str(src),'--translation',str(target),'--output',str(folder/'map.html'),'--default-language','en'])
            self.assertEqual(code,0); self.assertEqual(src.read_bytes(),before)
            bundle=json.loads((folder/'map.graph.json').read_text()); self.assertEqual(bundle['default_language'],'en')
            self.assertEqual(bundle['view'], original['view'])


class ConfigTests(unittest.TestCase):
    def test_interface_and_presentation_languages_are_independent(self):
        config=validate_config({'question':'Q','macro_rounds':4,'ui_language':'en','presentation_languages':['zh-CN'],'max_parallel_agents':2})
        self.assertEqual(config['presentation_languages'],['zh-CN','en'])
        self.assertEqual(config['research_language_policy'],'unconstrained')
        self.assertEqual(config['logical_roles'],5)

    def test_invalid_choices_and_silent_workflow_changes_are_rejected(self):
        for patch in ({'macro_rounds':True},{'macro_rounds':0},{'max_parallel_agents':6},{'depth_hops':2},
                      {'presentation_languages':[]},{'presentation_languages':['und']},{'logical_roles':2},
                      {'research_language_policy':'English only'},{'agent_command':'run something'}):
            with self.assertRaises(ValueError):validate_config({'question':'Q',**patch})

    def test_card_is_portable_offline_and_injection_safe(self):
        document=render_card({'question':'</script><script>alert(1)</script>'})
        self.assertNotIn('src="settings.js"',document)
        self.assertNotIn('src="i18n.js"',document)
        self.assertNotIn('</script><script>alert(1)</script>',document)
        self.assertIn('\\u003c/script>',document)
        self.assertNotIn('https://',document)

    def test_saved_config_is_complete_and_native_card_has_language_choice(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'run-config.json'
            saved=save_config(path,{'question':'Q','presentation_languages':['en','en','ja']})
            self.assertEqual(saved['presentation_languages'],['en','ja'])
            self.assertEqual(json.loads(path.read_text()),saved)
        prompt=portable_prompt('Q')
        self.assertIn('presentation_languages',{f['id'] for f in prompt['fields']})
        self.assertEqual(prompt['fixed']['research_language_policy'],'unconstrained')


if __name__=='__main__':unittest.main()
