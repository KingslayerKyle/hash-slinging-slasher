"""Numbered sound families must vary takes rather than codec/rate digits."""
import unittest

import families


class FamilyTakeTests(unittest.TestCase):
    def test_modern_take_before_encoding_tail(self):
        for tail in ('.lnn.75.48000.all', '.ln2.100.44100.en_us'):
            with self.subTest(tail=tail):
                names = ['fixture/weapon/fire_01' + tail, 'fixture/weapon/fire_03' + tail]
                found = families.families(names)
                self.assertEqual(dict(found), {('fixture/weapon/fire_', 2, tail): {1, 3}})
                self.assertEqual(list(families.gaps(found, 0)), ['fixture/weapon/fire_02' + tail])

    def test_legacy_take_before_encoding_tail(self):
        for tail in ('.rn75.pc.en.snd', '.ln100.pc.snd'):
            with self.subTest(tail=tail):
                names = [r'fixture\weapon\fire_001' + tail, r'fixture\weapon\fire_003' + tail]
                found = families.families(names)
                self.assertEqual(dict(found), {(r'fixture\weapon\fire_', 3, tail): {1, 3}})
                self.assertEqual(list(families.gaps(found, 0)), [r'fixture\weapon\fire_002' + tail])

    def test_original_tail_case_is_preserved(self):
        tail = '.LNN.75.48000.ALL'
        found = families.families(['fixture_fire_01' + tail, 'fixture_fire_03' + tail])
        self.assertEqual(list(families.gaps(found, 0)), ['fixture_fire_02' + tail])

    def test_mixed_padding_and_tails_do_not_join_families(self):
        tails = ['.lnn.75.48000.all', '.lnn.75.44100.all']
        names = ['fixture_fire_01' + tails[0], 'fixture_fire_003' + tails[0],
                 'fixture_fire_03' + tails[1]]
        self.assertEqual(len(families.families(names)), 3)
        self.assertEqual(list(families.gaps(families.families(names), 0)), [])

    def test_margin_remains_nonnegative_and_keeps_padding(self):
        tail = '.lnn.75.48000.all'
        found = families.families(['fixture_fire_00' + tail, 'fixture_fire_02' + tail])
        self.assertEqual(list(families.gaps(found, 1)), [
            'fixture_fire_01' + tail, 'fixture_fire_03' + tail])

    def test_single_member_and_wide_span_do_not_expand(self):
        tail = '.lnn.75.48000.all'
        self.assertEqual(list(families.gaps(families.families(['fixture_fire_01' + tail]), 4)), [])
        found = families.families(['fixture_fire_001' + tail, 'fixture_fire_999' + tail])
        self.assertEqual(list(families.gaps(found, 4)), [])

    def test_other_names_keep_final_number_rule(self):
        for tail in ('', '_c', '.unknown75.pc.snd', '.lnn.75.48000', '.lnn.75.pc.all'):
            with self.subTest(tail=tail):
                names = ['fixture_item_01' + tail, 'fixture_item_03' + tail]
                expected = {}
                for name in names:
                    before, digits, after = families.NUMBERED.match(name).groups()
                    expected.setdefault((before, len(digits), after), set()).add(int(digits))
                self.assertEqual(dict(families.families(names)), expected)

    def test_take_must_follow_underscore_and_stay_bounded(self):
        for name in ('fixture_fire01.lnn.75.48000.all', 'fixture_fire_0001.lnn.75.48000.all'):
            with self.subTest(name=name):
                self.assertIsNone(families.SOUND_TAKE.match(name))
                before, digits, after = families.NUMBERED.match(name).groups()
                self.assertEqual(dict(families.families([name])), {
                    (before, len(digits), after): {int(digits)}})


if __name__ == '__main__':
    unittest.main()
