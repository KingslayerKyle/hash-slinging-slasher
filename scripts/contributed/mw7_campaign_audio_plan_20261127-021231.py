"""Build a compiled sound-file search for named MW7 campaign dialogue lines.

Run: python contrib/mw7_campaign_audio_plan.py --manifest <path>/sp26/techsets_manifest.csv
Size: bin/windows/confirm_plan.exe plans/mw7-campaign-audio.txt --game MODWAR7 --size
Search: bin/windows/confirm_plan.exe plans/mw7-campaign-audio.txt --game MODWAR7

Reads explicit retail campaign zone names and exact target-held dialogue aliases.
Measures dialogue sound paths and encoding tails from MW7, BO6, and MWIII.
Writes one plan and its beginning, stem and ending lists in plans/. Reusable
when the MW7 campaign manifest or confirmed campaign lines change.
Initial measurement: 32 beginnings, 1,852 line stems and 6 encoding tails.
The engine tested 414,848 candidates in 9 seconds and confirmed 3,352 sound files.
"""

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))

from generator_inputs import TAIL, named_names

ZONE_FILE = re.compile(r"techsets_(sp_rex_[a-z0-9_]+)\.ff")
CAMPAIGN_LINE = re.compile(r"dx_sp_(?:[a-z0-9]+_){3,}[a-z0-9]+")
PATH_STYLES = {
    "full-zone": re.compile(r"[a-z0-9]+/sp/sp_[a-z0-9]+_[a-z0-9_]+/$"),
    "map-only": re.compile(r"[a-z0-9]+/sp/(?!sp_)[a-z0-9_]+/$"),
}


def read_zones(path):
    zones = set()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.reader(handle):
            match = ZONE_FILE.fullmatch(row[0].strip().lower()) if row else None
            if match:
                zones.add(match[1])
    return {zone for zone in zones if not any(
        zone.endswith(suffix) and zone.removesuffix(suffix) in zones
        for suffix in ("_entities", "_subset_ai")
    )}


def measure_sound_paths(game):
    aliases = named_names(game, "sound_alias")
    styles, tails = Counter(), Counter()
    for name in named_names(game, "sound_asset"):
        tail = TAIL.search(name)
        if not tail or "dx_sp_" not in name:
            continue
        before, line = name[:tail.start()].split("dx_sp_", 1)
        before = before.replace(".", "/")
        if not CAMPAIGN_LINE.fullmatch("dx_sp_" + line):
            continue
        if not tail[0].endswith((".english", ".english_safe")):
            continue
        for style, pattern in PATH_STYLES.items():
            if pattern.fullmatch(before):
                styles[style] += 1
                tails[tail[0]] += 1
    return styles, tails, {name for name in aliases if CAMPAIGN_LINE.fullmatch(name)}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()

    zones = read_zones(args.manifest)
    target_styles, target_tails, stems = measure_sound_paths("MODWAR7")
    styles = target_styles.copy()
    tails = target_tails.copy()
    donor_styles = {}
    for game in ("BLACKOP6", "YAMYAMOK"):
        donor_paths, donor_tails, _ = measure_sound_paths(game)
        donor_styles[game] = dict(donor_paths)
        styles.update(donor_paths)
        tails.update(donor_tails)

    begins = {f"rex/sp/{zone}/" for zone in zones if styles["full-zone"] >= 3}
    begins.update(f"rex/sp/{zone.removeprefix('sp_rex_')}/" for zone in zones if styles["map-only"] >= 3)
    endings = {tail for tail, count in tails.items() if count >= 3 or tail in target_tails}
    if not (begins and stems and endings):
        parser.error("no witnessed plan factors")

    folder = ROOT / "plans"
    folder.mkdir(exist_ok=True)
    lines = ["label: MW7 campaign dialogue files from captured aliases and retail zone names",
             "describe: captured dx_sp line stem, official campaign zone, and independently witnessed campaign path and encoding",
             "game: MODWAR7", "bare: no"]
    for key, entries in (("begin", begins), ("stem", stems), ("end", endings)):
        file = folder / f"mw7-campaign-audio.{key}.txt"
        with file.open("w", encoding="utf-8", newline="\n") as handle:
            handle.writelines(f"{entry}\n" for entry in sorted(entries))
        lines.append(f"{key}: @{file.relative_to(ROOT).as_posix()}")
    (folder / "mw7-campaign-audio.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"zones": len(zones), "begins": len(begins), "stems": len(stems),
                      "endings": len(endings), "target_style_controls": dict(target_styles),
                      "donor_style_controls": donor_styles}))


if __name__ == "__main__":
    main()
