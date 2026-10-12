"""Offline regressions for the animation block generator; no corpus/search needed.

Run: python -m unittest discover -s scripts -p 'test_witnessed_animation_blocks.py'

Supply the packaged scripts/contributed file through the same environment variable
to run this suite after submission. This is a local verification artifact.
"""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SOURCE = Path(os.environ.get(
    "WITNESSED_BLOCK_GENERATOR",
    str(Path(__file__).resolve().parent / "contributed" / "witnessed_animation_block_lengths.py"),
)).resolve()


def load_generator(path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = load_generator(SOURCE, "witnessed_animation_blocks_under_test")
KEY = (("anchor", "edge"), ("short",))


def sibling_seeds(prefixes):
    return {f"{prefix}_anchor_{block}_edge_tail"
            for prefix in prefixes for block in ("short", "long_form")}


class WitnessedAnimationBlocksTests(unittest.TestCase):
    def test_three_independent_pairs_learn_both_directions(self):
        rules = generator.learn_rules(sibling_seeds(("first", "second", "third")))
        self.assertEqual(rules[KEY], {("long", "form")})
        self.assertEqual(rules[(("anchor", "edge"), ("long", "form"))], {("short",)})

    def test_fewer_pairs_and_repeated_observations_do_not_qualify(self):
        seeds = sibling_seeds(("first", "second"))
        self.assertNotIn(KEY, generator.learn_rules(seeds))
        self.assertNotIn(KEY, generator.learn_rules(list(seeds) * 10))

    def test_three_pairs_sharing_four_names_do_not_count_as_six_names(self):
        seeds = set()
        for changed in range(4):
            blocks = ["anchor_long_form_edge" if position < changed else "anchor_short_edge"
                      for position in range(3)]
            seeds.add("root_" + "_".join(blocks) + "_tail")
        self.assertNotIn(KEY, generator.learn_rules(seeds))

    def test_only_complete_interior_blocks_with_both_anchors_transfer(self):
        rules = {KEY: {("long", "form")}}
        application = {
            "new_anchor_short_edge_tail",     # the only qualifying frame
            "new_other_short_edge_tail",      # different left anchor
            "new_anchor_short_other_tail",    # different right anchor
            "short_edge_anchor_tail",         # at the beginning
            "root_edge_anchor_short",         # at the end
            "new_anchor_shortish_edge_tail",  # substring, not an entire token
        }
        candidates, controls = generator.generate(rules, application, set(), 1)
        self.assertEqual(candidates, {"new_anchor_long_form_edge_tail"})
        self.assertEqual(controls, set())

    def test_simple_insertion_and_equal_width_replacement_are_not_rules(self):
        for left, right in (("short", "short_extra"), ("short", "extra_short"),
                            ("old_block", "new_piece")):
            with self.subTest(left=left, right=right):
                seeds = {f"{prefix}_anchor_{block}_edge_tail"
                         for prefix in ("first", "second", "third") for block in (left, right)}
                self.assertFalse(generator.learn_rules(seeds))

    def test_known_controls_do_not_consume_candidate_limit(self):
        rules = {KEY: {("long", "form")}}
        application = {"new_anchor_short_edge_tail", "known_anchor_short_edge_tail"}
        known = {"known_anchor_long_form_edge_tail"}
        candidates, controls = generator.generate(rules, application, known, 1)
        self.assertEqual(candidates, {"new_anchor_long_form_edge_tail"})
        self.assertEqual(controls, known)
        with self.assertRaisesRegex(ValueError, "Candidate limit exceeded"):
            generator.generate(rules, application, set(), 1)

    def test_configured_capture_path_is_used_without_reading_a_corpus(self):
        capture = SimpleNamespace(game="BLACKOP6", by_pool=lambda: {"xanim": []})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            configured = root / "configured-captures"
            output = root / "candidates.txt"
            argv = [str(SOURCE), "--game", "BLACKOP6", "--out", str(output)]
            def configured_path(key, default):
                return str(configured if key == "snapshots" else root / default)
            with patch.object(generator.snapshot.settings, "path", side_effect=configured_path), \
                    patch.object(generator.snapshot, "table_names", return_value=[]), \
                    patch.object(generator.snapshot, "read", return_value=capture) as read, \
                    patch.object(generator, "held_history", return_value=set()), \
                    patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
                generator.main()
            read.assert_called_once_with(configured / "blackop6.ids")
            self.assertEqual(output.read_text(encoding="utf-8"), "")

    def test_configured_findings_are_verified_against_selected_capture(self):
        game = "BLACKOP6"
        good = "new_anchor_short_edge_tail"
        bad = "wrong_anchor_short_edge_tail"
        key = generator.snapshot.fnv1a(good, game, "xanim") & generator.snapshot.ID_MASK
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "custom-findings" / game.lower() / "run_fixture"
            run.mkdir(parents=True)
            (run / "xanim.txt").write_text(f"{key:x},{good}\n{key:x},{bad}\ninvalid,{good}\n",
                                           encoding="utf-8")
            with patch.object(generator, "ROOT", root), \
                    patch.object(generator.snapshot.settings, "path", return_value=str(root / "custom-findings")):
                self.assertEqual(generator.held_history(game, {key}), {good})
                self.assertEqual(generator.held_history(game, set()), set())

    def test_generator_finds_root_after_moving_to_contributed_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / "scripts"
            contributed = scripts / "contributed"
            contributed.mkdir(parents=True)
            (scripts / "snapshot.py").write_text("# test root marker\n", encoding="utf-8")
            moved = contributed / "generator_with_submit_timestamp.py"
            shutil.copyfile(SOURCE, moved)
            with patch.object(sys, "path", list(sys.path)), \
                    patch.dict(sys.modules, {"snapshot": SimpleNamespace()}):
                relocated = load_generator(moved, "relocated_animation_generator")
            self.assertEqual(relocated.ROOT, root)


if __name__ == "__main__":
    unittest.main()
