"""Regression checks for the submitted sound-template generator, without a search."""
import contextlib
import importlib.util
import io
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

FILE = Path(__file__).parent / 'contributed/sound_word_templates_20261005-225503.py'
SPEC = importlib.util.spec_from_file_location('sound_word_templates', FILE)
templates = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(templates)


class SoundWordTemplatesTests(unittest.TestCase):
    def run_generator(self, game, names, *flags):
        output = io.StringIO()
        with patch.object(templates, 'present_sound_names', return_value=names), \
                patch.object(templates.sys, 'argv', [str(FILE), '--game', game, *flags]), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
            templates.main()
        return output.getvalue()

    def test_single_slot_and_count(self):
        names = {'wpn/rifle/rifle_fire.snd', 'wpn/smg/smg_reload.snd'}
        output = self.run_generator('BLKOPSCW', names)
        self.assertEqual(set(output.splitlines()), {
            'wpn/smg/smg_fire.snd', 'wpn/rifle/rifle_reload.snd'})
        self.assertEqual(self.run_generator('BLKOPSCW', names, '--count'), '')

    def test_two_slots_have_valid_line_endings_and_no_control_bytes(self):
        names = {'wpn/rifle/plr/rifle_plr_fire.snd', 'wpn/smg/npc/smg_npc_reload.snd'}
        output = self.run_generator('BLKOPSCW', names, '--two', '2')
        self.assertIn('wpn/smg/plr/smg_plr_fire.snd\n', output)
        self.assertTrue(output.endswith('\n'))
        self.assertFalse(any(ord(c) < 32 and c != '\n' for c in output))

    def test_bo4_keeps_backslash_output(self):
        output = self.run_generator('BLKOPS04', {
            'wpn/rifle/rifle_fire.snd', 'wpn/smg/smg_reload.snd'})
        self.assertNotIn('/', output)
        self.assertIn('wpn\\smg\\smg_fire.snd\n', output)

    def test_seed_membership_uses_each_games_sound_hash(self):
        for game in ['BLKOPS04', 'BLKOPSCW', *sorted(templates.snapshot.MODERN)]:
            with self.subTest(game=game):
                name = 'wpn/rifle/rifle_fire.snd'
                spelling = name.replace('/', '\\') if game == 'BLKOPS04' else name
                value = (templates.snapshot.fnv1a_nofold(spelling) if game == 'BLKOPS04'
                         else templates.snapshot.fnv1a(spelling, game, 'sound_asset'))
                shot = SimpleNamespace(game=game, records=[(value & templates.snapshot.ID_MASK, 1)],
                                       pool_name=lambda pool: 'sound_asset')
                with patch.object(templates.snapshot, 'snapshots', return_value=['fixture']), \
                        patch.object(templates.snapshot, 'read', return_value=shot), \
                        patch.object(templates.snapshot, 'table_names', return_value=[spelling, 'absent.snd']) as tables, \
                        patch.object(templates.snapshot, 'confirmed_names', return_value=[]):
                    self.assertEqual(templates.present_sound_names(game), {name})
                    self.assertEqual('fnv1a_xsounds_v2' in tables.call_args.args,
                                     game in templates.snapshot.MODERN)


if __name__ == '__main__':
    unittest.main()
