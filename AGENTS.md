# Read this first

## Modern-games support

This solver supports BO4 (`BLKOPS04`), Cold War (`BLKOPSCW`), MWII (`MODWAR22`),
MWIII (`YAMYAMOK`), BO6 (`BLACKOP6`), BO7 (`BLACKOP7`) and MW7 (`MODWAR7`).
The older two-game counts and examples below are historical. Startup rotates all seven
installed captures; explicit game selection leaves the rotation cursor unchanged.

Search animations, images, materials, sound assets and sound aliases in every game.
Search models normally only in BO4 and Cold War: modern models carry embedded names.
Existing xmodel pool lists and all_pools also obey this policy. Only a verified hash-only
modern model exception warrants search_modern_models = true in [search]; searches and submit
honor that explicit opt-in. Never call historical modern model entries new recoveries.
Modern model coverage is omitted from progress reports; snapshots and name history remain.

Modern ordinary assets use offset `0x47F5817A5EF961BA`; modern aliases
use `0xCBF29CE484222325`. Lookup uses 63 bits; modern alias output keeps all 64 bits.
BO4 SAB sound names retain their literal backslashes. Use the shared game policies rather
than reusing a legacy hash for modern candidates. Pool indexes come from the capture's
adjacent census, including injected sound pools, rather than another game's native enum.

Each game has one combined snapshot. MWII, MWIII and BO6 combine captured MP/SP modes by
asset type. MW7 keeps one canonical filename when its build is replaced. Source-mode captures
and private extraction notes stay outside tracked source. No game needs to be launched to search.

Database keys exclude resolved assets even when Saluki's display paths use different separators.
Read verified original spellings through the shared database readers; never submit an export
path spelling unless it hashes back to the key. Unrestorable rows still exclude their stored key.
The collection, coverage, Discord report and submission paths all handle the seven game tags.
See [capture setup and policies](docs/MODERN_CAPTURES.md) and [table policies](docs/HASHES.md).


You are here to recover Call of Duty asset names that nobody has resolved yet, and to prove each
one against the real game so it is a fact rather than a guess.

The person who started you has gone to do something else. They are not waiting at the keyboard.
Your job is to grind for hours and have findings on disk and submitted when they come back.

---

# 1. Run this. It is the only thing you have to remember.

```
bin\windows\start.exe                          Windows
bin/linux/start                                Linux
bin/macos/start                                macOS (universal: Apple Silicon and Intel)
cargo run --release --bin start                to build it yourself
```

That one command **updates the clone, installs and checks git and the GitHub CLI, refreshes the
community hash tables, and reads every pull request other contributors have open right now.** It
exits non-zero if anything would stop a grind, and every search in this repository refuses to run
until it has passed.

It is one command because three separate instructions did not survive contact with reality. Each
of the three things it does has failed in the field, repeatedly, and each failure costs somebody's
entire night:

- **A stale clone.** Everything a search excludes against moves daily. A clone from yesterday
  rediscovers what was submitted last night, and the run looks like a success right up to the
  moment the pull request is a duplicate.
- **`gh` not signed in.** Discovered at 4am with a full results folder and nowhere to send it.
- **Not knowing what is in flight.** Your clone cannot see an open pull request. That is exactly
  where duplicates come from — and **five contributors have submitted the same 430 names**, byte
  for byte identical in every file. Nobody was careless. They simply had no way to know.

`preflight` is the same program under its older name. Either will do.

**If it blocks, fix what it says and run it again.** That is the one thing worth interrupting the
user for, and only for the one step that cannot be automated: `gh auth login` opens a browser and
needs a human. `start` prints the exact command, including the full path to `gh.exe` — a terminal
opened before the install does not know the plain `gh` command, and telling somebody to type
`gh auth login` in that terminal has wasted more contributor hours here than any bad search.

---

# 2. Grind. Do not ask.

**You are the thing that decides.** That is the whole job, and it is not a figure of speech. Three
things tell you where to point it, and all three are worth an hour before you write a line:

- **the submissions** -- what has already been found, by what method, and what it returned
- **the tables** -- what cod-name-db already resolves, which is what a find has to be *new* to
- **the scripts** -- `scripts/` and `scripts/contributed/` are the library, and they are for
  reading as much as running. They are where the ideas are, and where the shape is: what a
  generator looks like, how it seeds from names known to be real, how it sizes itself. Take one
  apart before writing your own, and check whether what you are about to build already exists.

Out of that, work out where the reach is missing and *build the thing that reaches it*. Then run
it, submit, and do it again with what you just learned. Nobody is going to hand you a method.

**So do not build or run a fixed rotation, and do not write one for somebody else to run.** A
script that runs every existing method in order looks productive and is the one shape that cannot
grow this project: every method already in the repository has been ground repeatedly, so a
rotation buys throughput on picked-over ground while the invention -- the only thing that reaches
anywhere new -- quietly stops. One such driver was written and removed on 2026-08-20 for exactly
this reason. Measured the same day: 165 pull requests landed, and the overwhelming majority came
from methods somebody invented that evening, none of which any rotation contained.

- **Do not stop to ask which method to try.** Pick one and run it. Given a choice between asking
  and grinding, grind.
- **Do not summarise and wait for approval.** There is nobody to approve it.
- **Do not stop because a pass found little.** A pass that finds nothing still feeds the next one.
- **Do not stop because you think you are done.** Cold War has 136,467 unnamed ids in the five
  types that matter and Black Ops 4 has 141,889. Nobody has come close.
- **Keep going for hours.** Run a pass, re-measure, run another.

## The grinding costs your CPU, not your AI usage

The searching is compiled Rust on every core, tens of billions of candidates a pass. That is
electricity, not tokens. While an hour-long pass runs you are waiting on a process.

Your usage goes on deciding what to try and reading a short summary. **So do not waste it on
output.** A pass prints progress every thirty seconds for an hour; pulling all of that into your
context is the one way to drain a limit here for nothing.

```
bin\windows\confirm_cw.exe > logs\general.log 2>&1      then read the last ~30 lines
```

Never read a results file to count it — count the lines. Never paste found names into your
reasoning to "check" them; the tools already verified them against the game, which is what
confirmation *is*.

## Optional CUDA for worthwhile forward products

CPU is the default, requires no CUDA software, and never probes a GPU. A source build with
`cargo build --release --features cuda --bin confirm_plan --bin confirm_cw` adds an optional
NVIDIA backend to those two tools. Use the new executables in `target/release`; the committed
portable binaries in `bin/` do not gain CUDA support from installing a Toolkit. `confirm_list`
continues to stream on the CPU.

Prefer `--backend auto` when CUDA is available. It retains cheap and inverse (`Meet`) searches
on CPU, then checks support and calibrates performance before selecting the GPU for a large
forward product. An eligible GPU can still be slower. `--backend cuda` explicitly forces the
forward backend and reports an error if it cannot run; `auto` falls back to CPU. The default
automatic threshold is 100 million candidates; `--gpu-min-candidates N` accepts a positive
override, and `--cuda-device N` chooses the zero-based device ordinal.

`confirm_plan --gpu-check` or `confirm_cw --gpu-check` is a standalone diagnostic: no search,
capture, startup refresh, or findings run. `confirm_plan --size` does not probe CUDA. Missing
support is explained; CPU work remains available. Consult [the GPU guide](docs/GPU.md) for
compatible NVIDIA hardware, Toolkit/build tools, driver setup, and the distinction between
build requirements and runtime requirements. Nothing installs drivers or a Toolkit automatically.
Do not install CUDA for AMD, Apple, or NVIDIA GPUs below compute capability 7.5.

Hardware selection does not change candidates, game/type hashing, exclusions, fingerprints,
findings, or submission. **A backend change never makes a spent method new.** Continue to run
`start`, invent grounded methods, honor fingerprint/futility guards, and submit each completed
job as before. GPU speed is useful only after deciding a pass is worthwhile.

## Thinking is the engine. Do not economise on it

**The thinking is what keeps this open-ended.** Every method here exists because somebody worked
out that it could exist; the corpus grows, which changes what the next method can reach, which is
why there is always another one. Take that away and what is left is a fixed list of scripts
somebody runs -- finite, decaying as each method exhausts, and reproducible by anybody with a
weekend. **So the thing to cut is never the thinking.**

What actually drains a limit is none of that:

- **reading output.** A pass prints progress every thirty seconds for an hour. Read the last ~30
  lines of a log, never the log.
- **refining an idea that already failed.** The fourth version of a measurement that was weak the
  first time. One idea gets one cheap measurement; write the number down and move on.
- **narrating.** Summarising what you are about to do, then doing it, then summarising it again.

And one free optimisation, which is not a limit on thinking but a way to get it for nothing: a
pass costs no usage at all and saturates every core for hours, so **if there is a pass worth
running, start it before you settle in to think.** The reasoning then happens while the machine
works.

The word doing the work there is *worthwhile*. Cores busy with a spent method are not better than
cores idle -- it is the same night lost, and worse, it looks like progress. **Never start a pass
merely to have something running.** That is exactly the mistake §2 removed a fixed rotation for.

So thinking with nothing running is simply right when:

- **Everything that reaches this ground is spent or fingerprint-blocked.** Then inventing *is* the
  work. There is nothing to run, and a spent pass would return somebody else's names.
- **A short measurement decides which pass to run.** Minutes that stop three hours going at the
  wrong pool or the wrong game are the best trade available -- take them before starting anything.
- **The only thing you could run is known low-yield** *and you are going to be here to start
  something better*. A method measured at a handful of names is not worth three hours of machine
  you could give to a better one an hour from now.

## Every one of those assumes somebody is coming back

If you are leaving this unattended, they do not hold: there is no better pass an hour from now,
because nobody is there to start it.

This happened on 2026-08-22. An agent finished a grind at 06:50, reasoned -- correctly by the
three bullets above -- that everything cheap was exhausted and everything expensive was measured
poor, and stopped to write up. The machine sat idle for **four hours and fourteen minutes**, worth
roughly five hundred names at the rate then measured.

**The lesson is not "run something anyway", and the first fix attempted here was exactly that.**
A loop was written that ground a plan forever. It was reverted the same day, and why is worth more
than the incident:

- **It was a hardcoded hash-finder** -- a prefix list, a suffix list and a name list, combined on a
  timer. That is precisely the shape of tool this project exists to beat, and those tools have had
  years and GPUs pointed at these games without recovering these names. Rebuilding one here and
  calling it the overnight workflow gives away the only advantage there is.
- **It put it in the worst possible window.** Unattended hours are when there is the most budget to
  think and the least pressure. Filling them with a rotation guarantees that the stretch of time
  most likely to produce a method produces none.
- **It manufactures duplicates.** Its stems come from the published tables, which everybody shares,
  so two contributors running it overnight burn two nights to produce one night's names.
- **It amplifies collisions.** A coincidental match is a wrong name that hashes to a real id, and
  nothing downstream catches it -- CI re-verifies by hash, which it passes. It enters `findings/`
  and becomes seed material for every later derivation. A loop running trillions of candidates a
  round runs that lottery all night.

### What to do instead

Idle cores are a **symptom**, not the disease. They were idle because the agent had stopped
thinking, not because it had failed to start a script, and no script fixes that.

§2 already says the right thing, and it is easy to read as a scheduling tip: *if there is a pass
worth running, start it before you settle in to think.* The pass is the **output** of thinking,
started so the machine works while the thinking continues. A pass whose existence does not depend
on anybody having had an idea is the thing being replaced.

So, concretely, before you stop for any reason -- to think, to write up, to tidy:

1. **Have you invented something today?** If not, that is the work, and it is worth more than any
   pass. `final_byte` came out of an hour's thought and returns one name per 18 candidates;
   `tails` returned 1,151 for twenty-one seconds of machine. Either is worth more than a night of
   grinding, and unlike a night of grinding they keep paying.
2. **Start what you invented, then write up.** Finishing a pass is a stop too, and the most
   expensive one -- that is what cost the four hours above.
3. **If you genuinely have nothing to start, the honest answer is that the machine idles.** That is
   information: it means every relation anybody has measured is closed and the corpus is waiting on
   an idea. Manufacturing activity hides that, which is worse than the idle.

### And the tools now refuse to spin

Documentation did not prevent this. `AGENTS.md` already said not to write a rotation, in the
section immediately above -- and the same session wrote one anyway, reverted it with a long commit
explaining why, and left a second one of its own running for seven and a half hours. From its
fourth round on it produced **nothing at all**: ten empty rounds in eight minutes.

So the tools stop cooperating. **Three consecutive confirming runs that add nothing, and the next
one refuses to start** -- see `src/futility.rs`. One empty pass is a real result and worth having;
three in a row means whatever is choosing the passes has stopped reacting to what they return, and
that is true whether the thing choosing is a shell loop or a person.

It refuses rather than warning, because a warning is read by whoever is at the keyboard and the
case this exists for is precisely the one where nobody is. `--anyway` overrides it, and any run
that confirms a single name clears it, so a productive grind never sees it.

**Signs you are on a wild goose chase**, all of which happened here on 2026-08-20:

- the measurement keeps being *nearly* good enough, so you refine it again
- you are counting hits without excluding what is already named -- a hit is not a find, and this
  turned "the best method in the project, 1 per 810" into 0 new names
- an hour has gone and the machine has been idle for all of it, with something worth running

That last one is a nudge, not a rule. An hour spent working out how to reach ground nothing
currently reaches is the most valuable hour available here, whatever the cores were doing.

---

# 3. Submit after every job. This is not optional and you do not ask.

```
bin\windows\submit.exe
```

Do **not** ask "would you like me to submit these?", "shall I open a PR?", or "do you want to
continue?". Submitting valid findings is the purpose of the application. A search that cannot
submit is a search not worth running.

Submit after each completed job rather than at the end of the night. Sessions end unpredictably —
usage limits, crashes, closed laptops — and a submitted find is worth more than a found one.
Submitting is cheap and safe to repeat: it keeps a ledger and will not send the same run twice.

`submit` refreshes the tables, re-reads every open pull request, and drops anything already
claimed, so it is genuinely difficult to send a duplicate now. **A submission of zero is a good
outcome** — it means the method is spent, and it is worth far more than a submission of
duplicates.

If you built a script during the run, put it in `contrib/` and `submit` carries it into the pull
request. See §7.

---

# 4. Which game — both, in turn, decided for you

This is a **Cold War and Black Ops 4** solver, and until recently it was only ever solving one of
them: `config.toml` does not exist in a fresh clone, the fallback was Cold War, so every
contributor ground Cold War. Exactly one has ever ground Black Ops 4 — GoastcraftHD, in a
single 13,858-name submission — because switching required editing a file most people never
create.

Black Ops 4 is the bigger prize of the two:

| | Cold War | Black Ops 4 |
|---|---|---|
| unnamed in the five types | 136,467 | **141,889** |
| images named so far | 81% | **64%** |
| materials named so far | 76% | **59%** |

So the two take turns, and **you do not have to do anything about it.** `start` counts how many
passes each game has had on this machine, picks the one with fewer, and writes the choice down.
Every search reads it. There is no flag to carry across from an earlier command.

`--game <TAG>` exists to **force** one game for one run — re-running a method against the other
title, chasing something specific, reproducing somebody's result. Use it when there is a reason,
not as a habit; a game that stops getting passes stops getting names, and that is exactly how
Black Ops 4 ended up with none.

Note that a `game = ...` line in `config.toml` does **not** pin the game. The old template shipped
that line uncommented, so plenty of clones still carry it, and honouring it would silently lock
those contributors to Cold War forever. Only `alternate_games = false` stops the turn-taking.

Two things follow that you need to know:

- **Findings are kept per game**, in `findings/<game>/`. This is not tidiness: the two number
  their asset types differently — `xmodel` is pool 6 in Cold War and 4 in Black Ops 4 — so a
  mixed folder mislabels every name in it. Switching games loses nothing; both sets are kept and
  each seeds the other, because Cold War carries a great deal of Black Ops 4's content.
- **`submit` sends one pull request per game**, titled `[BLKOPS04] findings from ...`, so a
  reviewer can tell at a glance which title a batch is for.

---

# 5. The five asset types, and the pools that waste a night

Search these and nothing else unless the user says otherwise:

```
model     material     image     anim     sound file     sound alias
```

**Three of those are sound-shaped and only two are wanted.** They go to different tables upstream,
so filing one as another contaminates the community database:

| pool | what it holds | goes to |
|---|---|---|
| **`sound_asset`** | **individual sound files** | `fnv1a_xsounds.csv` |
| **`sound_alias`** | **the names scripts and weapons refer to** | `fnv1a_soundbanks_aliases.csv` |
| `sound` | sound *banks*, like `mp_embassy.all` | `fnv1a_soundbanks*.csv` |

**Sound is a separate pass, with its own vocabulary:**

```
bin\windows\confirm_cw.exe --game BLKOPS04                     the other four types
bin\windows\confirm_cw.exe --game BLKOPS04 --sounds --no-fold   sound files and aliases
```

Two passes because sound names look nothing like the rest, so a sound ending tried against a model
id can only ever be a coincidence and never a match. Sharing one run made both halves worse and
slower. Split, each gets its own measured lists (`data/sound.*.txt`) and hunts only ids its
vocabulary can reach. `--no-fold` is for Black Ops 4 only — see §6.

Neither of the two wanted ones is a loader asset — sound files live in SAB files and aliases live
inside bank assets — so both were read out of the games and injected into the snapshots. Between
them they are **the largest untouched ground in the project**:

| | Cold War | Black Ops 4 |
|---|---|---|
| `sound_asset` unnamed | 19,301 | **70,878** of 79,263 |
| `sound_alias` unnamed | **43,603** of 50,890 | 23,790 of 50,043 |

In Cold War that split is `sound_asset` (19) against `sound_bank` (18). Black Ops 4's own enum has
only the bank pool, because its individual sounds live in SAB files the loader never opens — so
`sound_asset` was **added at index 170** and its ids injected from those files. It is now the
largest single opportunity in either game: **70,878 unnamed of 79,263**.

**Black Ops 4 sound names keep their backslashes**, and their ids are the hash of exactly that.
Pass `--no-fold` when grinding them, or the search matches nothing at all while looking perfectly
healthy:

```
bin\windows\confirm_cw.exe --game BLKOPS04 --no-fold
```

Measured: 8,385 of 8,385 known names reproduce unfolded, 0 folded. Every other pool folds and must
not use the flag.

`config.toml` already targets exactly these. **Do not widen it.** Widening looks productive and is
the single most reliable way to waste a night, because the biggest pools in both games are the
worthless ones.

| pool | Cold War | Black Ops 4 | why it is a waste |
|---|---|---|---|
| `streamkey` | 420,229 | 292,133 | the largest pool in either game. One pass returned ~290,000 genuine, useless hashes — endless `maps/mp/mp_apocalypse.d3dbsp_s1__terrain_l01_n000079`. They also bury the real findings. |
| `xmodelmesh` | 271,840 | 259,051 | unreachable. A mesh name ends in 26 base32 characters that are a hash of the mesh itself. |
| `localizeentry` | 99,294 | 52,232 | the entry holds a pointer to its own **unhashed** string, so the plain text is already in the build. No published table bothers with these. 8,667 were confirmed in one twenty-minute pass, all worthless. |

`submit` will not send names from these pools and `confirm_list` will not file them, so this is
enforced rather than requested. **A hash being genuine does not make it worth recovering.**

Submissions have gone out covering 40 asset types picked by guesswork, and four sound-adjacent
pools chosen because they had "sound" in the name. Neither helped anybody.

---

# 6. What is already established — do not re-derive any of this

**The hash.** FNV-1a, 64 bit. Basis `0xCBF29CE484222325`, prime `0x100000001B3`. The name is
normalised first: **lower cased, and backslash folded to forward slash**. Missing that
normalisation makes everything fail. Compare asset ids at **63 bits** — loader ids always have bit
63 clear. (Not every table masks at 63; `docs/HASHES.md` has the full map of file → game → hash →
mask, from Saluki's own loading code.)

**The same hash works for both games.** Cold War and Black Ops 4 are identical here.

**The hash runs backwards.** The prime is odd, so it has an inverse mod 2^64, and
`h = (h * prime_inverse) ^ byte` removes a byte exactly. An ending does not have to be appended to
every stem — it can be *peeled off each wanted id once*. The cost stops being
`stems × beginnings × endings` and becomes a sum. Implemented in `src/search.rs`; use `run_best`,
which picks the cheaper direction. Read the comments there before changing anything.

**Material names are paths, and there are twelve directories, not one:**
`mc/ wc/ clt/ splm/ vd/ mcs/ ei/ cltp/ vdd/ el/ mcp/ ec/`. Verified against the published tables:
`mc/` heads 496,666 names and `ec/` heads 25. Ranking beginnings by popularity keeps the first two
and silently discards the naming of everything under the other ten. Carry all twelve.

**Measure conventions, never guess them** — and measure the *confirmed* names, not only the
published ones. The tables hold no xmodel with a directory on it; confirmed xmodels are full of
them (`splm/`, `clt/`, `cltp/`). `scripts/derive_lists.py` measures both.

**Names are long.** The median confirmed name has seven or eight underscore-separated segments;
under 4% have three or fewer. Composing names from a dictionary of words is therefore hopeless for
almost every real name — the space of word sequences passes 2^63 long before the name does.
**Recombining fragments of names known to be real is the only shape that works.** That is what
every method here does, and it is why the seeding principle below is not a style preference.

---

# 7. The seeding principle, and the snowball

**Candidates are always built from names already known to be real.** The published tables, the
names already confirmed, everybody's merged submissions, strings scraped from a build. A method is
a way of *recombining* that material.

This is also why the search is self-feeding: every confirmed name is a new beginning, a new
ending, and a new numbered family for the next pass. **Run a pass, re-measure, run again.**

## Leave the repository better than you found it

The names you find go into a table and are finished. **The thing that found them makes every
later contributor faster.** So:

- If you wrote a generator, put it in `contrib/`. `submit` puts it in the pull request under
  `scripts/contributed/`.
- If you invented a method, add it to `METHODS.md` in the shape the others use — including what
  it is *spent by*.
- If it did not work, add it to the dead ends table. A measured negative is worth as much as a
  find and costs the next person nothing.
- **Before inventing anything, read the candidate list.** `METHODS.md` has a section,
  *Candidates worth building*, holding ideas already thought through with the cheap measurement that
  decides each -- plus the seams measured **dead**, so a plausible-sounding generator is not built
  on one. Measuring first killed three such ideas in an hour.
- **Before inventing anything, read what already exists.** `start` prints the whole script
  library with each script's purpose, precisely so nobody spends an evening re-deriving
  `continuations.py` under a new name. If you skipped that output, get it back with:
  ```
  python scripts/methods_report.py --families      every method, folded, best first
  python scripts/methods_report.py --efficiency    how far each has decayed from its best
  python scripts/seams.py                          which relations between types hold
  python scripts/coverage.py --five                where the unnamed assets actually are
  ```
  and read `scripts/README.md`, which says which scripts are reconnaissance and which are methods.

## A ranking is for ruling things out, not for choosing

`methods_report.py --efficiency` says what is **spent**, and that is safe for everybody to read:
"do not spend your night on that" cannot cause a collision.

Used the other way it is a ladder with extra steps. It is deterministic and global, so everybody
who runs its top row builds the same candidates and `submit` drops them all as claimed -- the
five-contributors-one-batch failure, re-created, and the fingerprint will not catch it because
their corpora differ slightly. It also **cannot rank a method nobody has written**, so leaning on
it steers away from the one thing this project is for.

What diverges naturally is the negative space:

```
python scripts/coverage.py --five      where the unnamed assets actually are
python scripts/seams.py                relations nothing has mined
python scripts/reach.py --missing      what the lists structurally cannot express
python scripts/uncarried.py            beginnings no cut of which is carried
```

Two people reading those pick different ground. Two people reading a ranking pick the same row.

The evidence is in the day this was written. `heads` -- 692 names, the best single pass -- did not
come from the ranking; it came from asking *why* `tails` pointed at the end of a name and never the
front. `uncarried` came from `reach.py` printing a signal nobody had acted on for days. Neither was
the top row of anything.


## Inventing a method is now cheap — this is the important part

You do not have to write Rust to try an idea. `confirm_list` takes candidate names on standard
input and does the whole careful half: the game's hash, the unnamed set, exclusion against the
tables, the run notes, results that only ever grow.

```
python scripts/continuations.py | bin\windows\confirm_list.exe - ^
    --label "per-prefix continuations" --script scripts/continuations.py
```

A method is now a script that prints names. Generate them any way you like.

## But a script that prints names is a thousand times slower than the engine beside it

This is worth knowing before you write one, because it decides what shape your idea should take.

Measured on this machine: Python emits candidate strings at about **2.6M a second** at its
absolute best, and the run record shows real generators managing 0.1M to 1.4M. Counted off
`submissions/` on 2026-08-22: **every invented method ever run here has tested 10.2 billion
candidates between them** -- 166 runs, every contributor, three days. One general pass covers 103
trillion. The clever half of this project has been running on a ten-thousandth of the machine.

So when your idea is a **cross product** -- some beginnings, some stems, some endings -- do not
print it. Write it as a **plan** and let the compiled engine multiply it:

```
bin\windows\confirm_plan.exe plans/mine.txt --size     what it would cost, before you spend it
bin\windows\confirm_plan.exe plans/mine.txt            run it
```

A plan is a few lines. `@path` reads a file, anything else is a literal, and `begin`, `stem` and
`end` may each repeat:

```
label: zombie character bodies
begin: @data/prefixes.txt
begin: i_
stem:  @contrib/zombie_cores.txt
end:   @data/suffixes.txt
```

`plans/example.txt` is a worked one. This is the same `run_best` the general search uses -- same
hash, same exclusion, same run folder and fingerprint -- **aimed where you point it** instead of
at the whole corpus. That is the difference between the search everybody runs and a search only
you are running.

Keep printing names for anything that is *not* a cross product: edits, splices, walks, anything
where each candidate is computed rather than combined. `confirm_list` is still right for those.

**Always pass `--script`.** It copies your generator into the run, and `submit` puts it in the
pull request. Without it the method dies with your session -- seven generators are named in past
submissions here and **not one of them exists**, so every contributor since has started without
them.

**Write a new generator into `contrib/`, not `scripts/`.** `contrib/` is gitignored precisely
because it is the staging area for work that is not committed yet, and `submit` copies what it
finds there into the pull request as `scripts/contributed/`. `scripts/` is the promoted half of
the library -- for generators that already earned their place and are already in git.

The reason is worth knowing, because it used to lose files. `submit` will not send a script the
library already holds -- sending one produced pull requests that rewrote 95 lines of an unchanged
file on a CRLF no-op. It used to decide that by reading `scripts/` off the disk, so a file you had
just written there matched *itself* and was skipped while nothing upstream held it. That happened
on 2026-08-20: `materials_from_images.py` was named by two merged pull requests and carried by
neither. It now asks `git ls-files` instead, so an uncommitted file is no longer mistaken for the
library.

One case is still open: a script **committed locally but not pushed** counts as tracked, and the
pull request branch is built through GitHub's API from the fork's head rather than from your
commits -- so it would again be named and not carried. `contrib/` avoids the whole question.

This is the highest value thing you can do here and it is the reason this repository is pointed at
an assistant rather than run as a fixed program.

---

# 8. Do not run a search somebody has already run

Every run now carries a **fingerprint**: a digest of everything that decides what it will find —
the method, the game, the pools, the flags, the two lists. It goes into the submission, and
`start` collects everybody's.

**Nothing counted off your own disk goes in, and that is a fix rather than an omission.** It used
to mix in `seed lines`, `pieces` and `wanted`. Every one of those is local: `seed lines` counts
the gitignored `findings/` tree, so the same method on the same day fingerprinted 3,383,984 for
one contributor, 5,957,759 for another and 3,257,412 for a third. One method grew **48 distinct
fingerprints**, `state/swept.txt` reached 196 entries, and the guard below **never once fired**
while everybody re-ground ground somebody had already cleared.

If your search's fingerprint matches one already submitted, the tool stops and tells you who ran
it. **It is not being cautious. It will return their names and nothing else.** That is precisely
how five contributors came to submit the same 430 names: the general search is deterministic, a
fresh clone gives everyone identical inputs, so it gives everyone identical output.

When that happens, do one of these — never `--anyway`:

1. **Run a method that reaches somewhere else.** `METHODS.md` says what each one gets at that
   nothing else does.
2. **Invent one.** See §7.

**Re-measuring the lists is not on that list, and it used to be first on it.**
`python scripts/derive_lists.py` does change the fingerprint, which is exactly why it looked like
a remedy — but it changes what the search is *called* without changing what it can *reach*.
Measured over three consecutive folds: 55 names, then 294, then 51, the last on a corpus two and
a half times larger. The tool said this in every exhausted run's notes for a month, and following
it is most of how the yield here collapsed from 165 names a pass to 2. Re-measure when the lists
have lost vocabulary — `derive_lists.py` reports what its ceiling cut — not to reopen ground.

> **A method that produced a large batch for somebody else is not therefore the best thing to run
> next. It is the most likely thing to be exhausted.**

---

# 9. Rules that are not negotiable

1. **Results only ever grow.** Never rewrite a results file to be smaller. A rule change that no
   longer reaches an old name must not delete it.
2. **Exclude against the tables, the merged submissions, and the open pull requests** before
   calling anything a find. `submit` does all three; do not work around it.
3. **Never write one game's names into another's files.** Snapshots carry their game internally
   and the tools check it. Do not defeat that check.
4. **Submit after every job.** Not at the end of the night.

## Collisions, briefly

A match proves the string hashes to an id the game holds. With 136,467 wanted ids in a 2^63 space
a coincidental match is rare but not zero, and it scales with how many candidates a pass asks
about. **Measured:** the 41.7 T candidate pass expects 0.617 coincidental names; widening the
corpus to 103.2 T raises that to 1.527. A seeded pass of forty million expects 0.0000.

Every binary prints the figure before it starts. Watch it when you widen something — it is the
price of a bigger corpus, and it is cheap next to what the corpus buys, but it is not zero. It
only becomes a real problem in unconstrained character sweeps, which is why those are the last
resort.

---

# 10. Where to look

| | |
|---|---|
| `README.md` | what this is, and how to run each search |
| `METHODS.md` | the method registry: what each reaches, what it has returned, when it is spent |
| `scripts/README.md` | the script library, and what to put in a contributed one |
| `docs/SETUP.md` | the install walkthrough, for when the user is stuck on git or `gh` |
| `docs/HASHES.md` | which cod-name-db file belongs to which game, with which hash and mask |
| `docs/GPU.md` | optional CUDA setup, backend selection, and scoped measurements |
| `src/lib.rs` | the hash, the filter, the results type, `LOW_VALUE_POOLS` |
| `src/search.rs` | the peeling engine. Read the comments before changing anything |
| `src/bin/confirm_plan.rs` | the plan format, and why a cross product should never be printed |
| `scripts/seams.py` | which relations between asset types hold -- and why a strong one still has to be run |
| `scripts/derive_closure.py` | the snowball: every derivation re-run over whatever was just confirmed |
| `src/startup.rs` | what `start` checks and why each check exists |
| `snapshots/*.pools.txt` | every pool in both games, identified and counted |

Some identified *types* still have no destination table upstream in cod-name-db — a confirmed
`technique_set` name has nowhere to land. **Giving such a type a home upstream is a genuinely
valuable contribution.**
