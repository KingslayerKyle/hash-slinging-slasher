# hash-slinging-slasher

<p align="center">
  <img src="https://static.wikia.nocookie.net/spongebob/images/b/bd/Hashslingingslasher.png"
       alt="The Hash-Slinging Slasher" width="360">
</p>

<p align="center"><em>Slinging hashes at Call of Duty until the names fall out.</em></p>

Call of Duty stores most of its asset names as hashes rather than text. The name is gone; only
the number survives. This recovers them — and proves each one against the real game, so what
comes out is a fact rather than a guess.

Currently **Black Ops Cold War** and **Black Ops 4**.

## You do not need the game

This is the part worth understanding, because it is why anyone can help.

Confirming a name asks one question: *is the hash of this string the id of an asset the game
holds?* The answer is a set of numbers, and those numbers have already been captured — 1.6
million of them for Cold War, 1.0 million for Black Ops 4, in a file of a few megabytes.

Those numbers are committed here, in `snapshots/`. Both games are finished and will never be
patched again, so the capture was a one-off: these files are final, not a cache that goes stale.

So you need **no game, no Cordycep, no Saluki, and not even Windows**. You need this repo and a
CPU.

## Your CPU does the work, not your AI

The searching is compiled Rust running on every core, hashing tens of billions of candidates a
pass. That is CPU time and electricity — it costs **no AI usage at all**. While an hour-long
pass runs, your assistant is just waiting on a process.

Usage goes on deciding what to try and reading a short summary afterwards: a few thousand tokens
for an hour of grinding. A whole night is cheap.

## What you need

- **git**, and the **GitHub CLI** (`gh`) signed in with `gh auth login`. Findings are submitted
  through it, and the hash tables are fetched with git.
- **On Windows, nothing else.** The compiled tools are committed in `bin/windows/` -- run
  `bin/windows/preflight.exe` and skip the rest of this.
- **On Linux or macOS**, Rust. There are no dependencies, so `cargo build --release` takes about
  a minute once.

Your assistant should help you set these up rather than assume them. `preflight` refuses to pass
until they are working, because a night of grinding with nowhere to send it is a night wasted.

## The one-click grinder

For anyone who wants to donate CPU time and nothing else, there is a standalone app: run
`bin/windows/grinder.exe` (or `cargo run --release --bin grinder`). It fetches the community
tables itself — with git if the machine has one, by plain download if not — then grinds the
searches in a self-feeding rotation, printing every find as it lands. No GitHub account, no
terminal knowledge, nothing to configure.

Everything found is continuously exported to `exports/` as `hash,name` csv files named for the
[cod-name-db](https://github.com/echo000/cod-name-db) table each belongs to, so closing the app
at any moment — Enter, Ctrl+C, or just closing the window — leaves files ready to contribute.
At most the last minute of work is lost.

To ship it to somebody, give them a folder holding `grinder.exe`, the other `bin/windows`
executables, `snapshots/` and `data/`. That is the whole app.

## Getting started

Point your assistant at this folder and say so:

> Have a look at this repo and start grinding.

It reads [`AGENTS.md`](AGENTS.md), which tells it everything: what is already established, what
methods work, and that it should grind for hours rather than stop and ask you things. That is
the whole setup.

If you would rather drive it yourself:

```
cargo run --release --bin preflight        # always first
cargo run --release --bin confirm_cw       # the general search
cargo run --release --bin submit           # send what was found
```

`preflight` checks the one thing people forget: **that you are signed in to GitHub**, because a
night of grinding with nowhere to send it is a night wasted. If it complains, run `gh auth
login` and try again.

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

Grinding needs nothing. **Capturing** needed the game, Cordycep with everything loaded, and
Windows — and has already been done, for every pool in both games. It is kept for whenever a
third title is worth adding, behind a feature that is off by default:

```
cargo build --release --features cordycep
cargo run --release --features cordycep --bin snapshot
```

A default build has **zero external dependencies** and compiles anywhere. Nobody is asked to
build a process-memory reader they cannot use.

## Contributing

Findings arrive as pull requests, opened for you — you do not need to know git. They are
checked automatically and reviewed by hand before going upstream.

The most useful non-grinding contribution: **the unidentified pools**. A game holds assets in
numbered pools, and only some of those numbers have known asset types. Cold War has 67 pools
holding confirmed names that are labelled `pool_184` and the like, because nobody has worked out
what they are — and a name in an unidentified pool cannot be submitted upstream until its type is
known. `pool_184` alone holds over 52,000 confirmed names. See `snapshots/*.pools.txt`.

## The hash tables

`tables/` says what the community has already resolved, which is the whole difference between a
discovery and a name somebody published last week. They come from
[cod-name-db](https://github.com/echo000/cod-name-db), which is also where confirmed names end
up — so the same repository is both what you check against and where your findings go.

They go stale in about a day. Fetch them before a session:

```
cargo run --release --bin fetch-tables
```

## Standing on other people's work

- [Cordycep](https://github.com/Scobalula/Cordycep) — loads fast files without running the game,
  which is what makes capturing a snapshot possible at all.
- [cod-name-db](https://github.com/echo000/cod-name-db) — the community hash tables, both the
  source of what is already known and the destination for what gets found here.

Licensed GPL-3.0-or-later.
