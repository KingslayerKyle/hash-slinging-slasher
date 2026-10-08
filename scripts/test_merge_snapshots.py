"""Regression checks for merging native and synthetic pools by type."""
import struct
import tempfile
import unittest
from pathlib import Path
from merge_snapshots import merge, load


def fixture(path, records, census):
    tag = b"BLACKOP6"
    data = b"CODIDS"+struct.pack("<HH",1,len(tag))+tag+struct.pack("<Q",len(records))
    data += b"".join(struct.pack("<QH",*record) for record in records)
    path.write_bytes(data)
    path.with_suffix(".pools.txt").write_text(census)


class MergeTests(unittest.TestCase):
    def test_native_indexes_and_injected_indexes_are_remapped_by_type(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            mp, sp, out = [root/name for name in ("mp.ids","sp.ids","combined.ids")]
            fixture(mp, [(10,0),(20,1),(30,364)], "0 image 1\n1 material 1\n364 sound_alias 1\n")
            fixture(sp, [(10,1),(20,0),(30,315),(40,315),(50,2)], "0 material 1\n1 image 1\n2 campaign_only 1\n315 sound_alias 2\n")
            before = [p.read_bytes() for p in (mp,sp)]
            report = merge("BLACKOP6",[mp,sp],out)
            _, records, pools, _ = load(out)
            self.assertEqual(records, [(10,0),(20,1),(30,364),(40,364),(50,365)])
            self.assertEqual(pools[365][0], "campaign_only")
            self.assertEqual(report["shared_records_removed"],3)
            self.assertEqual([p.read_bytes() for p in (mp,sp)],before)
            with self.assertRaises(ValueError):
                merge("BLACKOP6",[mp,sp],out)

    def test_a_census_mismatch_and_unsorted_input_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"bad.ids"
            fixture(path, [(10,0)], "0 image 2\n")
            with self.assertRaises(ValueError):
                load(path)
            fixture(path, [(20,0),(10,0)], "0 image 2\n")
            with self.assertRaises(ValueError):
                load(path)


if __name__ == "__main__":
    unittest.main()
