# hash-slinging-slasher

<p align="center">
  <img src="https://static.wikia.nocookie.net/spongebob/images/b/bd/Hashslingingslasher.png"
       alt="The Hash-Slinging Slasher" width="360">
</p>

<p align="center"><em>Slinging hashes at Call of Duty until the names fall out.</em></p>

Call of Duty stores most of its asset names as hashes rather than text. The name is gone; only
the number survives. This recovers them — and proves each one against the real game, so what
comes out is a fact rather than a guess.

Supports **Black Ops 4, Cold War, MWII, MWIII, BO6, BO7 and MW7**. The modern-games release adds five games and their canonical snapshots. Available captures take turns, and findings stay separate per game. MP/SP modes are searched together after merging their captures by asset type.

See [modern capture setup and local verification](docs/MODERN_CAPTURES.md). The repository ships one snapshot per game. MWII, MWIII and BO6 each combine their captured MP/SP modes, so a game is searched once.

Normal searches recover animations, images, materials, sound assets and sound aliases in all
seven games. Models are searched only in BO4 and Cold War: the newer games carry embedded model
names. Modern model percentages and counts are omitted from progress reports, while existing
snapshots and model-name files remain available. See the model policy and exception setting in
[modern capture setup](docs/MODERN_CAPTURES.md).

## You do not need the game

This is the part worth understanding, because it is why anyone can help.

Confirming a name asks one question: *is the hash of this string the id of an asset the game
holds?* The answer is a set of numbers, and those numbers have already been captured — 1.7
million of them for Cold War and 1.2 million for Black Ops 4, alongside five modern captures.

Those numbers are committed here, in `snapshots/`, with asset-type maps alongside them. BO4 and
Cold War retain their existing captures. Newer builds replace the same game file when refreshed;
MW7 will use the same `modwar7.ids` slot when the full retail capture is available.

So you need **no game, no Cordycep, no Saluki, and not even Windows**. You need this repo and a
CPU.

## Your CPU does the work, not your AI

The searching is compiled Rust running on every core, hashing tens of billions of candidates a
pass. That is CPU time and electricity — it costs **no AI usage at all**. While an hour-long
pass runs, your assistant is just waiting on a process.

Usage goes on deciding what to try and reading a short summary afterwards: a few thousand tokens
for an hour of grinding. A whole night is cheap.

## What you need

**One command.** On Windows:

```
bin\windows\start.exe
```

It installs git and the GitHub CLI if they are missing, brings the repository up to date, fetches
the community hash tables, and reads what every other contributor has in flight so tonight does
not duplicate one. It stops and tells you exactly what to type if anything is in the way.

The only step it cannot do for you is `gh auth login`, because that opens a browser and asks you
to approve it — and it prints the exact command for your machine, full path included.
[`docs/SETUP.md`](docs/SETUP.md) walks through it for somebody who has never used a terminal.

On Linux run `bin/linux/start`, and on macOS `bin/macos/start` — a universal binary that runs on
both Apple Silicon and Intel. Both are committed and rebuilt by CI on every change to the source,
after that platform's own tests pass, so nothing needs installing.

**Those builds happen here and not in your fork**, and that is deliberate. The workflows are
guarded to this repository, because a fork that ran them committed its own copies of `bin/linux`
and `bin/macos` — and since `submit` syncs your fork's `main` before it branches, that rebuild
rode along in the next submission. A binary cannot be merged, so each one conflicted against
whatever was built here in the meantime. Submissions carry findings and generators; nothing under
`bin/` should ever appear in one, and CI now says so if it does.

To build it yourself instead, install Rust and run `cargo run --release --bin start`. There are no
dependencies, so it takes about a minute.

## Getting started

Point your assistant at this folder and say so:

> Have a look at this repo and start grinding.

It reads [`AGENTS.md`](AGENTS.md), which tells it everything: the one command to run first, what
is already established, what methods have already been exhausted by somebody else, and that it
should grind for hours rather than stop and ask you things. That is the whole setup.

If you would rather drive it yourself:

```
bin\windows\start.exe             # always first; every search refuses to run until it passes
bin\windows\confirm_cw.exe        # the general search: models, materials, images, anims
bin\windows\confirm_cw.exe --sounds --no-fold    # sound files and aliases (drop --no-fold on Cold War)
bin\windows\submit.exe            # send what was found
```

Sound is a **separate pass**, and it is the largest untouched ground in either game: 70,878 of
Black Ops 4's 79,263 `sound_asset` ids are unnamed, and 43,603 of Cold War's 50,890 `sound_alias`
ids. It is separate because sound names look nothing like the rest — deep paths, dotted tails, and
in Black Ops 4 backslashes — so a sound ending tried against a model id can only ever be a
coincidence. Split, each half gets its own measured lists and hunts only the ids its vocabulary can
reach. `--no-fold` is Black Ops 4 only: its sound names keep their backslashes and their ids are
the hash of exactly that, so without the flag a pass matches nothing while looking perfectly
healthy. `start` tells you which to run, so you do not have to remember any of this.

Or invent a method, which is the useful thing to do here — a generator that prints candidate
names, and one command that confirms them against the game:

```
python scripts/continuations.py | bin\windows\confirm_list.exe - --label "per-prefix continuations"
```

## How it actually works

1. **Build candidates** out of names already known to be real — the published hash tables, the
   names this project has already confirmed, strings scraped out of a build. Never out of thin
   air; see the seeding principle in `AGENTS.md`.
2. **Hash them** with the game's own hash (FNV-1a, 64 bit, normalised, compared at 63 bits).
3. **Look for the result** among the captured asset ids. A match means the game itself refers to
   that name.
4. **Exclude anything already published**, so what remains is genuinely new.
5. **Submit it**, and it goes upstream into the community hash tables.

The interesting part is step 1, and it is open-ended. Every method eventually exhausts, so
inventing a new way to build candidates is the highest-value thing anyone can do here — which is
exactly what an assistant is good at, and why this repo is written to be read by one.

## The two halves

Grinding uses the committed snapshots. **Capturing** reads an already prepared Cordycep
session on Windows. The repository already ships all seven captures, including their injected
sound pools. Modern captures are produced with hash-capture and combined by asset type; see
[capture setup](docs/MODERN_CAPTURES.md). The legacy snapshot tool remains behind an optional
feature for BO4 and Cold War:

```
cargo build --release --features cordycep
cargo run --release --features cordycep --bin snapshot
```

A default build has **zero external dependencies** and compiles anywhere. Nobody is asked to
build a process-memory reader they cannot use.

## Contributing

Findings arrive as pull requests, opened for you — you do not need to know git. They are
checked automatically and reviewed by hand before going upstream.

The most useful non-grinding contribution: **a home for the types that have no table**. Every
captured pool in all seven games is identified — `snapshots/*.pools.txt` is the complete map of every index,
its asset type, and how many assets it holds. What some types still lack is a *destination*:
cod-name-db carries tables for models, anims, images, materials and sounds, but a confirmed
`technique_set` name, for example, has no csv upstream to land in yet. Proposing and seeding
those tables is how whole pools' worth of findings become publishable.

## The hash tables

`tables/` says what the community has already resolved, which is the whole difference between a
discovery and a name somebody published last week. They come from
[cod-name-db](https://github.com/echo000/cod-name-db), which is also where confirmed names end
up — so the same repository is both what you check against and where your findings go.

They go stale in about a day. `start` fetches and refreshes them, so there is normally nothing to
do; `cargo run --release --bin fetch-tables` forces it in between.

Which file belongs to which game, and which hash and mask each uses, is in
[`docs/HASHES.md`](docs/HASHES.md). Getting the mask wrong is the commonest reason a correct name
fails to resolve, and it fails silently.

## Standing on other people's work

- [Cordycep](https://github.com/Scobalula/Cordycep) — loads fast files without running the game,
  which is what makes capturing a snapshot possible at all.
- [cod-name-db](https://github.com/echo000/cod-name-db) — the community hash tables, both the
  source of what is already known and the destination for what gets found here.

Licensed GPL-3.0-or-later.
