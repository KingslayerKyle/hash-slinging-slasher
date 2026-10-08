"""Ensure table readers undo export-directory rewrites only when the source key verifies."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import snapshot

class DatabaseSpellings(unittest.TestCase):
    def test_modern_periods_and_original_legacy_backslashes(self):
        cases=[
            ('fnv1a_xsounds_v2',0x10004dd150a8b9e6,'iw9/dst/iw9_dst_street_barricade_03.ln.75.48000.all','iw9.dst.iw9_dst_street_barricade_03.ln.75.48000.all'),
            ('fnv1a_xsounds',0x100116a5a23b8100,'amb/environment/water/waves/crash/wave_crash_01.ln100.pc.snd',r'amb\environment\water\waves\crash\wave_crash_01.ln100.pc.snd'),
        ]
        for table,key,display,original in cases:
            full,name=snapshot.verified_database_row(table,key,display)
            self.assertEqual(name,original)
            self.assertEqual(full&snapshot.ID_MASK,key)
            self.assertEqual(list(snapshot.database_names(table,[f'{key:x},{display}\n'])),[original])

    def test_all_readers_use_source_table_policy_and_keep_bad_row_keys(self):
        original='iw9.dst.iw9_dst_street_barricade_03.ln.75.48000.all'
        display='iw9/dst/iw9_dst_street_barricade_03.ln.75.48000.all'
        bad='bad/export/friendly.name'
        with tempfile.TemporaryDirectory() as directory:
            Path(directory,'fnv1a_xsounds_v2.csv').write_text(f'10004dd150a8b9e6,{display}\n123,{bad}\n')
            with patch.object(snapshot.settings,'tables_csv',return_value=directory):
                for game in ('BLKOPS04','BLKOPSCW','MODWAR22','YAMYAMOK','BLACKOP6','BLACKOP7','MODWAR7'):
                    with patch.object(snapshot.settings,'game',return_value=game):
                        self.assertEqual(snapshot.table_names('fnv1a_xsounds_v2'),[original])
                        known=snapshot.known_hashes()
                        self.assertIn(0x10004dd150a8b9e6,known)
                        self.assertIn(0x123,known)
                        self.assertNotIn(snapshot.database_source_hash('fnv1a_xsounds_v2',bad)&snapshot.ID_MASK,known)

    def test_unchanged_names_source_masks_and_full_width_aliases(self):
        name='cin/scene/file.sn75.pc.en.snd'
        full=snapshot.database_source_hash('fnv1a_english_xsounds',name)
        self.assertEqual(snapshot.verified_database_row('fnv1a_english_xsounds',full&snapshot.ID_MASK,name),(full,name))
        for table in ('fnv1a_bones','fnv1a_strings','fnv1a_bones_v2','fnv1a_soundbanks_aliases_v2','fnv1a_ximages_v2'):
            full=snapshot.database_source_hash(table,'test_name')
            self.assertEqual(snapshot.verified_database_row(table,full&snapshot.database_policy(table)[1],'test_name'),(full,'test_name'))
            self.assertEqual(snapshot.verified_database_row(table+'.csv',full&snapshot.database_policy(table)[1],'test_name'),(full,'test_name'))
        alias='fly_npc_ar_able18_ubgl_reload_07'
        full=snapshot.database_source_hash('fnv1a_soundbanks_aliases_v2',alias)
        self.assertGreater(full,snapshot.ID_MASK)
        self.assertIsNone(snapshot.verified_database_row('fnv1a_soundbanks_aliases_v2',full&snapshot.ID_MASK,alias))

    def test_legacy_case_and_older_mask_are_not_lost(self):
        for table,key,name in [('fnv1a_ximages',0x1cbe11a68bb09e77,'ui_icon_stickers_BPS1_058'),('fnv1a_xanims',0x1fd88e8f753ff0d,'a_chicken_death'),('fnv1a_english_xsounds',0xb007f5ada1917b7,'cin/cp_amerikatown_load/amerikatown_lr.sn75.pc.en.snd')]:
            self.assertEqual(snapshot.verified_database_row(table,key,name)[1],name)

if __name__=='__main__':
    unittest.main()
