"""Regression checks for game-specific collection, coverage and Discord output."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import collect_names as collect
import announce_names as announce
import measure_coverage as coverage
import snapshot


class NameReporting(unittest.TestCase):
    def test_every_game_and_type_keeps_search_hash_and_width(self):
        for game in collect.SUPPORTED:
            for kind in collect.WANTED:
                row = collect.output_row(game, kind, r'Test\asset.name')
                key, _, name = row.partition(',')
                full = snapshot.fnv1a_nofold(name) if game == 'BLKOPS04' and kind == 'sound_asset' else snapshot.fnv1a(name, game, kind)
                expected = full if game in snapshot.MODERN and kind == 'sound_alias' else full & snapshot.ID_MASK
                self.assertEqual(int(key, 16), expected)
                self.assertEqual(collect.verified_row(game, kind, row), row)
        self.assertEqual(collect.verified_row('MODWAR22', 'sound_asset',
            '10004dd150a8b9e6,iw9/dst/iw9_dst_street_barricade_03.ln.75.48000.all'),
            '10004dd150a8b9e6,iw9.dst.iw9_dst_street_barricade_03.ln.75.48000.all')
        self.assertIsNone(collect.verified_row('BLACKOP6', 'image', '123,invalid/name'))

    def test_untagged_rows_use_game_basis_and_the_correct_pool(self):
        name = 'test_asset'
        old = collect.output_row('BLKOPS04', 'image', name)
        new = collect.output_row('BLACKOP6', 'image', name)
        old_key = int(old.partition(',')[0], 16)
        new_key = int(new.partition(',')[0], 16)
        held = {'blkops04': {'image': {old_key}}, 'blackop6': {'image': {new_key}},
                'blkopscw': {'material': {old_key}}}
        self.assertEqual(collect.games_holding(old, held, 'image'),
                         [('blkops04', old), ('blackop6', new)])

    def test_modern_alias_restores_full_width_from_masked_capture(self):
        name = 'fly_npc_ar_able18_ubgl_reload_07'
        row = collect.output_row('BLACKOP6', 'sound_alias', name)
        key = int(row.partition(',')[0], 16)
        self.assertGreater(key, snapshot.ID_MASK)
        legacy = collect.output_row('BLKOPS04', 'sound_alias', name)
        self.assertEqual(collect.games_holding(legacy, {'blackop6': {'sound_alias': {key & snapshot.ID_MASK}}}, 'sound_alias'), [('blackop6', row)])
        self.assertIsNone(collect.verified_row('BLACKOP6', 'sound_alias', legacy))

    def test_coverage_uses_each_game_tables_and_masks_our_alias_ids(self):
        full = snapshot.fnv1a('fly_npc_ar_able18_ubgl_reload_07', 'BLACKOP6', 'sound_alias')
        shots = {'old': snapshot.Snapshot('BLKOPS04', [(11, 0)], ['image']),
                 'new': snapshot.Snapshot('BLACKOP6', [(11, 0), (full & snapshot.ID_MASK, 1)], ['image', 'sound_alias'])}
        calls = []
        def known(game=None):
            calls.append(game)
            return {11} if game != 'BLACKOP6' else {999}
        with patch.object(snapshot, 'snapshots', return_value=list(shots)), patch.object(snapshot, 'read', side_effect=shots.get), \
             patch.object(snapshot, 'known_hashes', side_effect=known), patch.object(coverage, 'our_ids', return_value={'blackop6': {'sound_alias': {full}}}):
            report = coverage.measure()['games']
        self.assertEqual(report['blkops04']['image']['named'], 1)
        self.assertEqual(report['blackop6']['image']['named'], 0)
        self.assertEqual(report['blackop6']['sound_alias']['named'], 1)
        self.assertIn('BLACKOP6', calls)

    def test_missing_game_tables_refuse_a_zero_baseline(self):
        shot = snapshot.Snapshot('BLACKOP6', [(11, 0)], ['image'])
        with patch.object(snapshot, 'snapshots', return_value=['new']), patch.object(snapshot, 'read', return_value=shot), \
             patch.object(snapshot, 'known_hashes', return_value=set()), patch.object(coverage, 'our_ids', return_value={}):
            with self.assertRaises(SystemExit):
                coverage.measure()

    def test_real_collection_preserves_bad_rows_and_excludes_local_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / 'submissions/Tester_BLACKOP6_20261008-010101'
            folder.mkdir(parents=True)
            good = collect.output_row('BLACKOP6', 'image', 'test_image')
            (folder/'image_20261008-010101.txt').write_text(good+'\n123,invalid/name\n', encoding='utf-8')
            hidden = root/'findings/blackop6'
            hidden.mkdir(parents=True)
            (hidden/'image.txt').write_text(collect.output_row('BLACKOP6', 'image', 'private_find'), encoding='utf-8')
            audit = []
            with patch.object(collect, 'ROOT', directory), patch.object(collect, 'snapshots_by_game', return_value={}):
                gathered = collect.collect(audit)
                _, written = collect.write(gathered, False)
                collect.write_summary(written, False)
            self.assertEqual(gathered[('blackop6', 'image')], {good})
            self.assertEqual(len(audit), 1)
            self.assertEqual(len(gathered), 7 * 6)
            self.assertTrue((root/'all_names/modwar7/sound_alias.txt').exists())
            self.assertEqual((root/'all_names/modwar7/sound_alias.txt').read_bytes(), b'')

    def test_discord_all_seven_games_with_zero_findings_and_payload_limits(self):
        summary = {'games': {game.lower(): {'names': 0, 'types': {kind: {'names': 0, 'found_pct': 95.5} for kind in collect.WANTED}} for game in collect.SUPPORTED},
                   'totals': {'names': 0}, 'order': collect.DISPLAY_ORDER}
        card = announce.embed(summary)
        self.assertEqual(len(card['fields']), 7)
        self.assertTrue(any(field['name'].startswith('Black Ops 6') for field in card['fields']))
        self.assertTrue(any(field['name'].startswith('Modern Warfare III') for field in card['fields']))
        for field in card['fields']:
            self.assertLessEqual(len(field['name']), 256)
            self.assertLessEqual(len(field['value']), 1024)
        size = len(card['title']) + len(card['footer']['text']) + sum(len(f['name'])+len(f['value']) for f in card['fields'])
        self.assertLessEqual(size, 6000)


if __name__ == '__main__':
    unittest.main()
