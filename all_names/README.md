# Every name this project has recovered

<table><tr>
<td valign="top">

<table>
<tr><th align="left"><code>blkops04/</code></th>
<th align="right" colspan="2">96,420 names in 6 file(s)</th>
</tr>
<tr><th align="left">asset type</th><th align="right">found here</th><th align="right">named, of all in the game</th>
</tr>
<tr><td><code>xmodel</code></td><td align="right">9,826</td><td align="right">49,949 / 61,139 &nbsp;(81.7%)</td></tr>
<tr><td><code>material</code></td><td align="right">33,384</td><td align="right">105,498 / 122,750 &nbsp;(85.9%)</td></tr>
<tr><td><code>image</code></td><td align="right">33,036</td><td align="right">140,063 / 167,360 &nbsp;(83.7%)</td></tr>
<tr><td><code>xanim</code></td><td align="right">4,582</td><td align="right">16,551 / 21,968 &nbsp;(75.3%)</td></tr>
<tr><td><code>sound_asset</code></td><td align="right">235</td><td align="right">8,619 / 79,263 &nbsp;(10.9%)</td></tr>
<tr><td><code>sound_alias</code></td><td align="right">15,357</td><td align="right">41,828 / 50,043 &nbsp;(83.6%)</td></tr>
</table>

</td>
<td valign="top">

<table>
<tr><th align="left"><code>blkopscw/</code></th>
<th align="right" colspan="2">69,123 names in 6 file(s)</th>
</tr>
<tr><th align="left">asset type</th><th align="right">found here</th><th align="right">named, of all in the game</th>
</tr>
<tr><td><code>xmodel</code></td><td align="right">3,608</td><td align="right">68,073 / 85,612 &nbsp;(79.5%)</td></tr>
<tr><td><code>material</code></td><td align="right">20,325</td><td align="right">140,696 / 158,158 &nbsp;(89.0%)</td></tr>
<tr><td><code>image</code></td><td align="right">9,725</td><td align="right">208,733 / 245,235 &nbsp;(85.1%)</td></tr>
<tr><td><code>xanim</code></td><td align="right">4,680</td><td align="right">21,011 / 28,468 &nbsp;(73.8%)</td></tr>
<tr><td><code>sound_asset</code></td><td align="right">1,662</td><td align="right">79,600 / 97,217 &nbsp;(81.9%)</td></tr>
<tr><td><code>sound_alias</code></td><td align="right">29,123</td><td align="right">37,542 / 50,890 &nbsp;(73.8%)</td></tr>
</table>

</td>
</tr></table>

**found here** is what this project has recovered and published in these files.
**named, of all in the game** is the whole pool: those names plus every one already in
the community tables, against every id the game holds.

They are not the same measure, and the second is much the larger.

Where `image` under `blkops04/` reads 33,036 and 140,063 / 167,360:
this project found 33,036 of the 140,063 names anybody has for that pool, and
27,297 of its ids are still nameless. The percentage is the fraction named,
not the fraction found here.

The emptiest pool is `sound_asset` under `blkops04/`: 8,619 of 79,263 named,
so 70,644 ids carry no name at all. That is the largest unworked ground
here, and it is invisible from a count on its own.

The community half of that is measured against `cod-name-db` on 2026-08-24 and stored in
`coverage.json`, because the tables are 345 MB and are not in this repository. Names
recovered here since are added on top, which is exact rather than approximate: `submit`
drops anything the tables already publish, so a later find cannot already be counted.
What a stale baseline misses is names *somebody else* published upstream, so it
under-reports rather than over-reports. `scripts/measure_coverage.py` refreshes it.

**Generated. Do not edit anything here by hand** -- `scripts/collect_names.py` rewrites it
whenever a submission lands, and an edit would be overwritten without warning. Corrections
belong in a submission, which is the record these are built from.

One file per game and asset type, `hash,name`, sorted by name. Together they are every name
in every merged submission in `submissions/`, with duplicates removed.

## Why you might want these rather than `submissions/`

`submissions/` answers *who found what, when, and by which method* -- it is the provenance
record and the input to `scripts/methods_report.py`. It is several hundred folders, and
anybody who just wants the names has had to walk and merge them. That loop is written once,
here, and the answer committed.

These are **not** a substitute for the community tables in `cod-name-db`. Those are the
published truth and are what every search excludes against. These are this project's own
contribution to them, which is a different and smaller thing.

## Why it is split by game

The two games number their asset types differently -- `xmodel` is pool 6 in Cold War and 4 in
Black Ops 4 -- so a file mixing them mislabels every row. You can see it in the type names
themselves: both `clipmap` and `clip_map` appear, and both `localizeentry` and
`localize_entry`, because those are the two games' own names for one pool.

A name appearing under both games is not duplication. Cold War carries a great deal of Black
Ops 4's content, and a name confirmed against both games' ids is a fact about both.

Twenty-three submissions predate the game going into the folder name. They are placed by
hashing each name and asking each game's `.ids` snapshot whether it holds an asset under it
-- the same question that made the name a find. A name both snapshots hold is filed under
both, because it is genuinely a fact about both.

Only the five asset types worth searching are here. Submissions carry names for 105 types;
the rest stay in `submissions/`, which is the record.
