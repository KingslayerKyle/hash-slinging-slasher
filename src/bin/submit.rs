//! Sends what was found, after checking it is all still new.
//!
//! Two things make this more than a `git push`.
//!
//! **The tables move while you work.** A name that was unpublished when a pass started can be in
//! the tables by the time it finishes, because other people are submitting too. So the tables are
//! refreshed *here*, immediately before the pull request, and anything that has since been
//! published is simply dropped from the batch. Nothing is re-searched -- the candidates were
//! already confirmed against the game and that has not changed; the only question is whether they
//! are still *new*, and that is a set difference costing seconds.
//!
//! **Sessions end abruptly.** An assistant on a usage limit stops mid-job, so submitting is done
//! after every job rather than at the end of a night. That makes this safe to run repeatedly: it
//! keeps a ledger of what has already gone, and a run that was already sent is skipped rather than
//! sent twice. If a session dies, the next one submits the backlog.
//!
//! Filenames carry the date and time to the second, so two submissions never collide.

use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::OnceLock;

use slasher::{
    config, expected_by_chance, github, low_value_reason, paths, recon, stamp, strip_stamp,
    tables, ID_MASK,
};

/// Where findings go. Set `submit_repo` in `config.toml` to override.
const DEFAULT_REPO: &str = "KingslayerKyle/hash-slinging-slasher";

/// Scripts a run wants to contribute, if it left any here.
///
/// The single best thing a night can leave behind is not its names -- it is the thing that found
/// them. A script in a pull request makes the next contributor's first hour smarter; a list of
/// names only makes the tables bigger. So anything dropped in this folder rides along.
const CONTRIBUTED: &str = "contrib";

/// The largest a contributed file may be before it is treated as working data rather than a
/// method.
///
/// Generous on purpose -- a long generator with a long docstring is a good thing and must not trip
/// this. What it stops is a stem list, a core dump, a scraped corpus: the inputs a method was
/// built from, which regenerate in a minute and would otherwise sit in everybody's clone for ever.
const BIGGEST_SCRIPT: u64 = 256 * 1024;

/// The ledger of run folders already sent, so nothing is submitted twice.
const LEDGER: &str = ".submitted";

/// The ledger of scripts already carried into a pull request: content digest, then the name the
/// library holds it under.
///
/// `already_in_library` answers "is this script on my disk", and that is the wrong question
/// within a night of grinding. A script is only on disk under its library name once the pull
/// request carrying it has been merged *and* pulled back down, which is hours later; four
/// submissions in the eight minutes before that all see an empty library and each stamp a fresh
/// copy. Measured on this repository on 2026-08-21: `scripts/contributed/` held 43 files that
/// were 12 distinct scripts, with `soundxfer` and `aliasswap` carried six times each.
///
/// The source comment on `tracked_scripts` calls this unfixable without fetching upstream bytes.
/// It is not: what a submission needs to know is what *it* has already sent, and that is a purely
/// local fact this machine has always had and never wrote down.
const SCRIPT_LEDGER: &str = ".contributed";

/// Where a `_yyyymmdd-hhmmss` stamp starts in a submission's filename, if it has one.
///
/// Deliberately not `strip_stamp`, which is right for a script name and wrong for a pool name:
/// it cannot tell the `_184` of `pool_184` from a stamp and eats both.
struct StampSuffix;

impl StampSuffix {
    fn find(&self, text: &str) -> Option<usize> {
        // Bytes throughout, and no `&str` slicing until the shape has been checked.
        //
        // Slicing `text[at..]` first panics on any filename where that byte offset falls inside a
        // multibyte character -- and this runs over every `.txt` in `submissions/`, which is other
        // people's filenames. It would abort `submit` in `recover_stranded`, before anything was
        // sent, which is the worst moment for this binary to die. The shape is pure ASCII, so it
        // can be recognised without ever building a string.
        let bytes = text.as_bytes();
        // `_` + 8 digits + `-` + 6 digits
        let width = 1 + 8 + 1 + 6;
        if bytes.len() < width {
            return None;
        }

        let at = bytes.len() - width;
        let stamp = &bytes[at..];

        let shaped = stamp[0] == b'_'
            && stamp[1..9].iter().all(u8::is_ascii_digit)
            && stamp[9] == b'-'
            && stamp[10..].iter().all(u8::is_ascii_digit);

        // `at` is a char boundary whenever the shape matched, because every byte from `at` on is
        // ASCII -- so a caller slicing there is safe.
        shaped.then_some(at)
    }
}

const STAMP_SUFFIX: StampSuffix = StampSuffix;

fn main() {
    // Every game's findings, not just the configured one. A session may have ground both, and a
    // run left unsent because the config moved on afterwards is a run lost.
    let findings = paths::findings_root();
    let outbox = paths::submissions();

    // 1. Who we are. Without this the whole night has nowhere to go, which is why `preflight`
    //    checks it before any searching rather than leaving it until now.
    let Some(who) = github_user() else {
        match github::locate() {
            Some(gh) => eprintln!("not signed in to GitHub. Sign in with:\n    {}", gh.login_hint()),
            None => eprintln!(
                "the GitHub CLI (`gh`) is not installed. On Windows: winget install --id \
                 GitHub.cli (anywhere else, https://cli.github.com), then `gh auth login`."
            ),
        }
        eprintln!("(this is what `preflight` warns about before a grind starts.)");
        std::process::exit(1);
    };
    println!("submitting as {who}");

    // 2. Anything a killed pass left behind, gathered up first so it can be sent like any other
    //    run. See `recover_stranded` -- this used to be lost silently.
    recover_stranded(&findings, &outbox);

    // 3. What has not been sent yet.
    let sent = already_sent(&outbox);
    let pending: Vec<PathBuf> = run_folders(&findings)
        .into_iter()
        .filter(|folder| {
            let name = folder.file_name().unwrap_or_default().to_string_lossy().to_string();
            !sent.contains(&name)
        })
        .collect();

    if pending.is_empty() {
        println!("nothing new to submit -- every run here has already been sent.");
        return;
    }

    println!("{} run(s) not yet submitted", pending.len());

    // 4. Refresh the tables *now*, so the batch is judged against what the community has this
    //    minute rather than whenever the session started.
    println!("\nrefreshing the tables before sending, in case anything was published meanwhile");
    let table_folder = match tables::ensure(&paths::tables(), true) {
        Ok(_) => tables::csv_folder(&paths::tables()),
        Err(why) => {
            eprintln!("\n{why}");
            eprintln!("refusing to submit against tables that may be stale.");
            std::process::exit(1);
        }
    };

    // 4b. What everybody else has claimed, asked of GitHub *now*.
    //
    //     The tables only know what has been merged and published upstream, which lags by days.
    //     The thing that actually causes duplicates is faster than that: somebody grinding on the
    //     same evening whose pull request is open but not yet merged. Nothing on this disk can
    //     know about that, and it has already happened repeatedly here: five submissions carry the
    //     same 430 names and two more carry the same 372, byte for byte.
    //     `python scripts/methods_report.py --duplicates` lists them.
    let repo = config::path("submit_repo")
        .map(|path| path.display().to_string())
        .unwrap_or_else(|| DEFAULT_REPO.to_owned());

    println!("\nreading what other people have in flight");
    let landscape = recon::survey(&repo, &outbox);

    if let Some(why) = &landscape.offline {
        eprintln!(
            "  [warn] GitHub would not answer ({why}), so open pull requests could not be read.\n  \
             [warn] Falling back to the last survey `start` saved, which may be hours old."
        );
    } else {
        println!(
            "  {} open submission(s); {} name(s) claimed in them and not yet merged",
            landscape.open.len(),
            landscape.claimed_in_flight
        );
    }

    // 5. One batch per game, and one pull request per game.
    //
    //    A name means nothing without the game it came from: the two number their asset types
    //    differently, so `xmodel` is pool 6 in Cold War and 4 in Black Ops 4. A batch mixing the
    //    two cannot state its own game truthfully, and a reviewer cannot tell at a glance which
    //    title a submission is for. The run folder's path says which game it was ground under,
    //    and that is what groups them here.
    let mut by_game: std::collections::BTreeMap<String, Vec<PathBuf>> = Default::default();
    for folder in pending {
        let game = paths::game_of(&folder).expect("run must live under its game's findings directory");
        assert!(config::GAMES.contains(&game.as_str()), "unsupported submission game {game}");
        by_game.entry(game).or_default().push(folder);
    }

    let cached = recon::load_cached();
    let mut opened = 0;

    for (game, runs) in &by_game {
        println!("\n--- {game} ---");
        let known = known_hashes(&table_folder, game);
        if !slasher::tables_look_complete(&known) {
            eprintln!("{game}: tables read short at {} hashes; refusing to submit", known.len());
            std::process::exit(1);
        }
        println!("{} hashes already published for {game}'s hash family", known.len());

        if let Some(url) = send(game, runs, &repo, &outbox, &who, &known, &landscape, &cached) {
            println!("\nsubmitted: {url}");
            opened += 1;
        }

        record(&outbox, runs);
    }

    if opened == 0 {
        println!("\nnothing was sent.");
    }
}

/// Pure local part of submission, shared with offline regression tests.
struct PreparedBatch {
    rows: Vec<(String, u64, String)>,
    dropped: usize,
    claimed_elsewhere: usize,
    claimed_names: HashSet<String>,
    worthless: std::collections::BTreeMap<String, usize>,
}

fn prepare_batch(game: &str, pending: &[PathBuf], known: &HashSet<u64>, landscape: &recon::Landscape, cached: &HashSet<u64>) -> PreparedBatch {
    // Drop anything already claimed: published in the tables, merged into submissions, or sitting
    // in somebody's open pull request. This is the cheap part and the whole reason a long grind
    // does not have to be redone when the world moves under it.
    let mut batch: Vec<(String, u64, String)> = Vec::new(); // (type, id as found, name)
    let mut dropped = 0_usize;
    let mut claimed_elsewhere = 0_usize;

    // The same names, counted once each. `claimed_elsewhere` tallies every occurrence across
    // every run folder, which is the right number to *report* -- it says how much of this
    // batch's work was already taken -- but the wrong one to compare against a deduplicated
    // `batch`, since a name reachable from three runs counts three times on one side and once
    // on the other.
    let mut claimed_names: HashSet<String> = HashSet::new();
    let mut worthless: std::collections::BTreeMap<String, usize> = Default::default();

    for folder in pending {
        for (kind, id, name) in names_in(folder) {
            // A pool that has already cost somebody a night for nothing does not go upstream,
            // whoever found it and however genuine the hash is. See LOW_VALUE_POOLS.
            if low_value_reason(&kind).is_some() {
                *worthless.entry(kind).or_default() += 1;
                continue;
            }

            // Both the id the run found and the hash of the name, because for every pool but
            // the one that keeps its backslashes they are the same number, and for that one they
            // are not. Excluding on either is right: a name already published is already
            // published however it was reached.
            let hash = slasher::games::hash(game, &kind, &name, true);
            let seen = |set: &HashSet<u64>| {
                set.contains(&id) || set.contains(&hash) || set.contains(&(hash & ID_MASK))
            };

            if seen(known) {
                dropped += 1;
                continue;
            }

            if landscape.holds(&name) || seen(cached) {
                claimed_elsewhere += 1;
                claimed_names.insert(name.to_lowercase());
                continue;
            }

            batch.push((kind, id, name));
        }
    }

    batch.sort();
    batch.dedup();
    PreparedBatch { rows: batch, dropped, claimed_elsewhere, claimed_names, worthless }
}

/// Serialize the exact matched keys; do not rehash display paths or truncate aliases.
fn write_batch_files(folder: &Path, when: &str, batch: &[(String,u64,String)]) -> std::io::Result<std::collections::BTreeMap<String, Vec<(u64,String)>>> {
    fs::create_dir_all(folder)?;
    let mut by_kind: std::collections::BTreeMap<String, Vec<(u64,String)>> = Default::default();
    for (kind,id,name) in batch { by_kind.entry(kind.clone()).or_default().push((*id,name.clone())); }
    for (kind,names) in &by_kind {
        let mut text=String::new();
        for (id,name) in names { text.push_str(&format!("{id:x},{name}\n")); }
        fs::write(folder.join(format!("{kind}_{when}.txt")),text)?;
    }
    Ok(by_kind)
}

fn submission_title(game: &str, who: &str, when: &str, names: usize) -> String {
    format!("[{game}] findings from {who}, {when} ({names} names)")
}

/// Sends one game's runs, and returns the pull request it opened.
#[allow(clippy::too_many_arguments)]
fn send(
    game: &str,
    pending: &[PathBuf],
    repo: &str,
    outbox: &Path,
    who: &str,
    known: &HashSet<u64>,
    landscape: &recon::Landscape,
    cached: &HashSet<u64>,
) -> Option<String> {
    let PreparedBatch { rows: mut batch, dropped, claimed_elsewhere, claimed_names, worthless } = prepare_batch(game, pending, known, landscape, cached);

    for (kind, count) in &worthless {
        println!(
            "held back {count} `{kind}` name(s): {}",
            low_value_reason(kind).unwrap_or_default()
        );
    }

    // The same name can be reached by several runs; it only needs sending once.
    batch.sort();
    batch.dedup();

    println!(
        "{} names to send\n  {dropped} dropped: published in the tables\n  {claimed_elsewhere} \
         dropped: already claimed by a merged submission or an open pull request",
        batch.len()
    );

    // What that second number means, said out loud.
    //
    // It is the only signal anywhere that somebody else is grinding the same ground right now,
    // and it was sitting in this output being read as bookkeeping. Measured over one night with
    // two agents running: the general search and `swaps` came back 70-99% claimed, while the
    // Cold War sound pass -- ground the other was not touching -- came back 3 claimed of 115.
    // Same machine, same hours. The difference was entirely which method the other one ran.
    //
    // Fingerprints stop you re-running a search somebody has *finished*. They cannot stop two
    // people running the same method at the same time, and this is what that looks like from
    // the inside.
    // Distinct names, and only the contested ones.
    //
    // Two mistakes, one after the other. First `claimed_elsewhere` was compared against a
    // deduplicated `batch` while itself counting every occurrence, so a rotation whose runs
    // overlap inflated the share. Then `dropped` was folded into the denominator to fix that,
    // which is worse: a name already published in the tables is old ground for everybody and says
    // nothing about whether somebody is grinding this method *now*. Published names dominate
    // exactly the batches that need the warning -- one submission here dropped 1,098 of them --
    // so the signal went quiet on the runs it was built for.
    //
    // The contested set is what this run found and could have sent: what is going, plus what
    // somebody else already claimed. Both counted as distinct names.
    let claimed_distinct = claimed_names.len();
    let offered = batch.len() + claimed_distinct;
    if claimed_distinct > 0 && offered >= 20 {
        let share = claimed_distinct as f64 * 100.0 / offered as f64;
        if share >= 50.0 {
            println!(
                "\n  [!] {share:.0}% of what this run found was already claimed by somebody else.\n  \
                 [!] They are grinding the same ground with the same method, and running it again\n  \
                 [!] will mostly rediscover their work. Pick a method they are not running --\n  \
                 [!] METHODS.md says what each one reaches that nothing else does."
            );
        }
    }

    if batch.is_empty() {
        println!(
            "\nnothing left to send for {game} -- every name found is already somebody's.\n\n\
             That is not a failed night, it is an honest one, and a submission of zero is worth \
             more\nthan a submission of duplicates. What it means is that this method is spent -- \
             and what\nspends a method is the ground, not the lists. Re-measuring them looks like \
             the way out\nand is not: three consecutive folds returned 55 names, then 294, then \
             51, the last on a\ncorpus two and a half times larger. Run a method that reaches \
             somewhere else, or invent\none -- METHODS.md says what each one gets at that nothing \
             else does, and `confirm_list`\ntakes candidates on standard input, so a method is a \
             script that prints names."
        );
        return None;
    }

    // Write the batch, named for the game and the moment it was sent, so nothing ever collides
    // and a folder says what it holds without being opened.
    let when = stamp();
    let folder = outbox.join(format!("{who}_{game}_{when}"));
    if let Err(error) = fs::create_dir_all(&folder) {
        eprintln!("could not make {}: {error}", folder.display());
        std::process::exit(1);
    }

    let by_kind = write_batch_files(&folder, &when, &batch).unwrap_or_else(|error| {
        eprintln!("could not write {}: {error}", folder.display());
        std::process::exit(1);
    });
    println!("\n{:<24} {:>8}", "type", "names");
    for (kind,names) in &by_kind { println!("{kind:<24} {:>8}", names.len()); }

    // The collision estimate, recorded rather than enforced. It is vanishingly small for any
    // seeded method; it is worth carrying so a strange batch can be traced afterwards.
    let estimate = expected_by_chance(batch.len() as u64, known.len());

    // What each run has to say for itself -- which method, and how long it ground for. Written
    // by the run into its own folder; a folder without one is from an older or interrupted run.
    let accounts = run_accounts(pending);

    // How many of each asset type, so a reviewer can see the shape of a batch without opening
    // five files and counting lines. A submission of 2,000 images and one model is a different
    // thing from an even spread across the five types, and only the breakdown says which it is.
    let breakdown = per_type(&batch);

    let notes = folder.join(format!("about_{when}.md"));
    let _ = fs::write(
        &notes,
        format!(
            "# Submission {when}\n\n\
             - game: **{game}**\n\
             - from: {who}\n\
             - names: {}\n\
             - dropped as already published: {dropped}\n\
             - dropped as already claimed by a merged or open submission: {claimed_elsewhere}\n\
             - runs included: {}\n\
             - searched: {}\n\
             - platform: {}\n\
             - confirmed on: {}\n\
{breakdown}\
             - expected coincidental matches: {estimate:.6}\n\
             - checked against: the community tables, every merged submission, and the {} pull \
             request(s) open at the moment of sending\n\n\
             Every name here was confirmed against the game's own loaded assets, and checked \
             against the community tables immediately before sending.\n\
             \n## How these were found\n{accounts}",
            batch.len(),
            pending.len(),
            config::targets().describe(),
            platforms_used(pending),
            backends_used(pending),
            landscape.open.len(),
        ),
    );

    // Anything the run wants to teach the next contributor, rather than only feed them.
    let scripts = contributed_scripts(pending);
    if !scripts.is_empty() {
        println!(
            "\ncarrying {} script(s) along with the names, so the next contributor inherits the \
             method and not just its output",
            scripts.len()
        );
    }

    println!("\nwritten to {}", folder.display());

    match open_pull_request(
        repo, game, &folder, &scripts, &when, who, batch.len(), dropped, claimed_elsewhere,
        &accounts, &breakdown,
    ) {
        Ok(url) => Some(url),
        Err(why) => {
            eprintln!("\nthe pull request could not be opened: {why}");
            eprintln!("the batch is saved at {} and will be sent next time.", folder.display());
            std::process::exit(1);
        }
    }
}

/// Each pending run's account of itself, as markdown: the folder, then whatever `notes.md` its
/// run wrote about which method ran and for how long.
fn run_accounts(pending: &[PathBuf]) -> String {
    let mut accounts = String::new();

    for folder in pending {
        let name = folder.file_name().unwrap_or_default().to_string_lossy();
        let note = fs::read_to_string(folder.join("notes.md"))
            .unwrap_or_else(|_| "- method: not recorded (an older or interrupted run)\n".to_owned());
        accounts.push_str(&format!("\n### {name}\n{note}"));
    }

    accounts
}

/// The scripts a run wants to contribute, from `contrib/` beside the findings and from a
/// `contrib/` folder inside any run being submitted.
///
/// The rule this enforces is the snowball: a night that invents a way of generating candidates
/// has produced two things, and the names are the less valuable of them. A name goes into a
/// table and is finished. A script makes every later contributor's first hour better, and the
/// evidence that this compounds is in `submissions/` -- the batches that came with a method
/// written down are the ones later batches built on.
///
/// Only text, and only files with something in them: a half-written script is worse than none.
fn contributed_scripts(pending: &[PathBuf]) -> Vec<PathBuf> {
    let mut folders = vec![paths::findings().join(CONTRIBUTED), PathBuf::from(CONTRIBUTED)];
    folders.extend(pending.iter().map(|run| run.join(CONTRIBUTED)));

    let mut found = scripts_in(&folders);

    // And anything new sitting in `scripts/` itself.
    //
    // Told "add your generator to the script library", somebody writes it into `scripts/`, which
    // is the obvious and arguably correct place. Under the folder rule alone that script is then
    // silently not sent -- and silently not sent is exactly how the seven generators named in
    // past submission notes (`attachments.py`, `pathmine.py`, `crosspool.py` and the rest) came
    // to exist nowhere. Being right about where it *should* go must not be the thing that loses
    // it. Untracked only, so the library's own files are not re-sent every time.
    let mut seen: HashSet<String> = found
        .iter()
        .filter_map(|path| Some(path.file_name()?.to_str()?.to_owned()))
        .collect();

    for path in untracked_scripts() {
        let Some(name) = path.file_name().and_then(|name| name.to_str()) else {
            continue;
        };

        if seen.insert(name.to_owned()) {
            found.push(path);
        }
    }

    found.sort();
    found
}

/// Where a contributed script lands in the shared library: stamped, like everything beside it.
///
/// Five pull requests once carried five different versions of `slotswap.py` under that one bare
/// name. Four of them merged only because the contributor's branches happened to build on each
/// other; the fifth was an add/add conflict that had to be resolved by hand. That is a bad thing
/// to hand a maintainer -- resolving a conflict inside somebody else's method means reading two
/// versions of a script you did not write and picking one, and picking wrong silently discards
/// the newer work. The submission files never had this problem, because they have carried a
/// `yyyymmdd-hhmmss` stamp from the beginning. The scripts now get the same treatment.
///
/// A script that has not changed keeps the name it already has, rather than gaining a fresh
/// stamped copy every run: the point is to stop collisions, not to accumulate one file per
/// submission. So an evolving generator leaves a readable trail of versions, and a stable one
/// leaves a single file.
fn library_name(name: &str, when: &str, bytes: &[u8]) -> String {
    let (stem, extension) = name.rsplit_once('.').unwrap_or((name, "py"));
    let base = strip_stamp(stem);

    match already_in_library(base, extension, bytes) {
        Some(existing) => existing,
        None => format!("{base}_{when}.{extension}"),
    }
}

/// Whether two files are the same script, ignoring how they reached the disk.
///
/// Not a byte comparison, because on Windows that answers the wrong question. git checks a file
/// out with CRLF while a script a run just wrote has LF, so the identical script differs in every
/// line depending only on its route to the disk. Comparing raw bytes meant the library copy never
/// matched: the first real submission after the stamping went in carried
/// `image_siblings_20260819-232739.py` alongside the byte-for-byte identical
/// `image_siblings_20260819-190013.py` already sitting there, and every run afterwards would have
/// added another. A folder of identical scripts under different stamps is worse than the name
/// collision this was all meant to fix.
fn same_text(left: &[u8], right: &[u8]) -> bool {
    let bare = |bytes: &[u8]| -> Vec<u8> { bytes.iter().copied().filter(|byte| *byte != b'\r').collect() };

    bare(left) == bare(right)
}

/// The scripts git tracks in this clone, as repository-relative paths with forward slashes.
///
/// `None` when git cannot answer -- outside a checkout, or without git on the path -- and every
/// caller then falls back to trusting the disk, which is what this did before.
///
/// This exists because "the library" and "what is sitting in `scripts/`" are not the same set,
/// and treating them as one lost a generator. A file an agent writes straight into `scripts/`
/// during a run is on the disk and absent from git, so it matched *itself* and was skipped as
/// already present while nothing upstream held it: `materials_from_images.py` was named by pull
/// requests #204 and #205 on 2026-08-20 and carried by neither. Asking git instead of the
/// filesystem makes the check mean what it always said it meant.
fn tracked_scripts() -> Option<&'static HashSet<String>> {
    static TRACKED: OnceLock<Option<HashSet<String>>> = OnceLock::new();

    TRACKED
        .get_or_init(|| {
            // The local index, deliberately, and it does not solve the duplicate carrying.
            //
            // This asked `git ls-tree origin/HEAD` for a while, on the theory that comparing
            // against the upstream branch would stop a stale clone re-sending a script merged
            // five minutes earlier. It cannot, and the reason is worth leaving here so nobody
            // tries it again: `matching_in` walks `scripts/` on **disk** and this listing only
            // filters what it finds there. A script merged upstream but absent from the clone is
            // invisible whichever listing is used, so narrowing the set can only reject more disk
            // files -- that is, re-send more.
            //
            // `origin` is also the contributor's *fork* in the flow `submit` itself creates, so
            // `origin/HEAD` is a branch that lags upstream by however long since the last sync.
            //
            // Fixing the re-carrying for real means comparing content that is not on disk:
            // fetching the upstream file list *and* its bytes, or reading the open pull requests
            // `submit` already downloads for the in-flight name check. Both are real work and
            // neither belongs in a one-line change.
            let output = Command::new("git")
                .args(["ls-files", "--", "scripts"])
                .current_dir(paths::root())
                .stderr(Stdio::null())
                .output()
                .ok()?;

            if !output.status.success() {
                return None;
            }

            let listing = String::from_utf8_lossy(&output.stdout);
            let paths: HashSet<String> = listing
                .lines()
                .map(|line| line.trim().replace('\\', "/"))
                .filter(|line| !line.is_empty())
                .collect();

            // An empty answer is a real one only if git succeeded and the repository genuinely
            // holds no scripts. Treating it as "nothing is tracked" would skip every match and
            // re-send the whole library, so it is refused rather than trusted.
            if paths.is_empty() {
                None
            } else {
                Some(paths)
            }
        })
        .as_ref()
}

/// Whether git tracks this file, given the listing. Unknown listing means yes: the fallback is
/// the old disk-only behaviour, which is wrong only in the narrow case above and must not start
/// refusing to recognise a library that is genuinely there.
fn is_tracked(path: &Path, tracked: Option<&HashSet<String>>) -> bool {
    let Some(tracked) = tracked else {
        return true;
    };

    let Ok(relative) = path.strip_prefix(paths::root()) else {
        return true;
    };

    tracked.contains(&relative.to_string_lossy().replace('\\', "/"))
}

/// The library's own copy of this script, under whatever stamp it carries.
///
/// Best effort: the library is only as current as the clone, and `start` refreshes that. Missing
/// a match costs one redundant file, which is why this is allowed to give up quietly. Claiming a
/// match that is not one would overwrite somebody's version, so the comparison is deliberately
/// narrow: the same base name, the same extension, and the same text bar line endings.
fn already_in_library(base: &str, extension: &str, bytes: &[u8]) -> Option<String> {
    // Both halves of the library. A generator that earned its place is moved into `scripts/`
    // proper and listed in `scripts/README.md`; `scripts/contributed/` is where a submission
    // files one on arrival. Checking only the second meant a script promoted to the first was
    // re-sent by every run afterwards, under a fresh stamp each time -- so an overnight grind
    // would have left a folder full of dated copies of a file already sitting one level up.
    let root = paths::root().join("scripts");

    let tracked = tracked_scripts();

    for folder in [root.join("contributed"), root] {
        if let Some(found) = matching_in(&folder, base, extension, bytes, tracked) {
            return Some(found);
        }
    }

    None
}

/// The one file in this folder that is this script, byte for byte bar line endings.
fn matching_in(
    folder: &Path,
    base: &str,
    extension: &str,
    bytes: &[u8],
    tracked: Option<&HashSet<String>>,
) -> Option<String> {
    for entry in fs::read_dir(folder).ok()?.flatten() {
        let path = entry.path();

        // On the disk but not in git is not in the library -- see `tracked_scripts`.
        if !is_tracked(&path, tracked) {
            continue;
        }

        let Some(name) = path.file_name().and_then(|name| name.to_str()) else {
            continue;
        };
        let Some((stem, ending)) = name.rsplit_once('.') else {
            continue;
        };

        if ending != extension || strip_stamp(stem) != base {
            continue;
        }

        if fs::read(&path).is_ok_and(|held| same_text(&held, bytes)) {
            return Some(name.to_owned());
        }
    }

    None
}

/// How many names of each asset type, as markdown list items.
///
/// A batch's total says how big it is and nothing about what it is. 2,000 images and one model is
/// a different submission from an even spread across the five types, and only this says which --
/// otherwise a reviewer has to open every file in the folder and count its lines, which is what
/// this replaces.
///
/// Ordered by count, largest first, because the question being asked is almost always "what is
/// this batch mostly?".
fn per_type(batch: &[(String, u64, String)]) -> String {
    let mut counts: Vec<(String, usize)> = {
        let mut seen: std::collections::HashMap<&str, usize> = std::collections::HashMap::new();
        for (kind, _, _) in batch {
            *seen.entry(kind.as_str()).or_insert(0) += 1;
        }
        seen.into_iter().map(|(kind, count)| (kind.to_owned(), count)).collect()
    };

    // Largest first, then alphabetically so two types of equal size do not swap places between
    // runs -- a diff that changes for no reason is a diff nobody reads.
    counts.sort_by(|left, right| right.1.cmp(&left.1).then(left.0.cmp(&right.0)));

    counts
        .iter()
        .map(|(kind, count)| format!("- {kind}: {count}\n"))
        .collect()
}

/// Which engine confirmed the runs in this batch, read back from each run's own notes.
///
/// Written per run rather than assumed here, because a batch can mix them: a night that starts on
/// the GPU and falls back to the CPU when a driver complains is a normal outcome, not an error,
/// and the submission should say so rather than pick one.
///
/// The point is traceability. If a GPU backend is ever found to have a fault, the batches it
/// produced can be identified and re-checked rather than guessed at â€” and provenance is cheap to
/// write now and impossible to reconstruct afterwards.
fn platforms_used(runs: &[PathBuf]) -> String {
    field_across(runs, "- platform: ", "not recorded (run predates this field)")
}

/// One field, read out of every run's notes, distinct values in the order first seen.
fn field_across(runs: &[PathBuf], prefix: &str, missing: &str) -> String {
    let mut seen: Vec<String> = Vec::new();

    for run in runs {
        let Ok(notes) = fs::read_to_string(run.join("notes.md")) else {
            continue;
        };

        for line in notes.lines() {
            if let Some(value) = line.strip_prefix(prefix) {
                let value = value.trim().to_owned();
                if !value.is_empty() && !seen.contains(&value) {
                    seen.push(value);
                }
            }
        }
    }

    if seen.is_empty() {
        return missing.to_owned();
    }

    seen.join(", ")
}

fn backends_used(runs: &[PathBuf]) -> String {
    let mut seen: Vec<String> = Vec::new();

    for run in runs {
        let Ok(notes) = fs::read_to_string(run.join("notes.md")) else {
            continue;
        };

        for line in notes.lines() {
            if let Some(value) = line.strip_prefix("- confirmed on: ") {
                let value = value.trim().to_owned();
                if !value.is_empty() && !seen.contains(&value) {
                    seen.push(value);
                }
            }
        }
    }

    // A run folder written before this field existed says nothing, and answering "CPU" for it
    // would be a guess dressed as a fact.
    if seen.is_empty() {
        return "not recorded (run predates this field)".to_owned();
    }

    seen.join(", ")
}

/// Files in `scripts/` that git does not know about yet: somebody's new generator.
///
/// Asked of git rather than judged by timestamps, because "new" here means "not part of the
/// library yet", which is a question only git can answer.
fn untracked_scripts() -> Vec<PathBuf> {
    let Ok(output) = std::process::Command::new("git")
        .args(["status", "--porcelain", "--untracked-files=all", "--", "scripts"])
        .stderr(Stdio::null())
        .output()
    else {
        return Vec::new();
    };

    let mut found = Vec::new();

    for line in String::from_utf8_lossy(&output.stdout).lines() {
        let Some(path) = line.strip_prefix("?? ") else {
            continue;
        };

        let path = PathBuf::from(path.trim().trim_matches('"'));

        let sensible = matches!(
            path.extension().and_then(|extension| extension.to_str()),
            Some("py" | "rs" | "sh" | "ps1")
        );

        let has_content = path.metadata().map(|data| data.len() > 0).unwrap_or(false);

        if sensible && has_content {
            found.push(path);
        }
    }

    found
}

/// The contributable files in a set of folders, first spelling of a name winning.
fn scripts_in(folders: &[PathBuf]) -> Vec<PathBuf> {
    let mut found: Vec<PathBuf> = Vec::new();
    let mut seen: HashSet<String> = HashSet::new();

    for folder in folders {
        let Ok(entries) = fs::read_dir(&folder) else {
            continue;
        };

        for entry in entries.flatten() {
            let path = entry.path();
            if !path.is_file() {
                continue;
            }

            let sensible = matches!(
                path.extension().and_then(|extension| extension.to_str()),
                Some("py" | "rs" | "sh" | "ps1" | "md" | "txt" | "toml" | "json")
            );

            let size = entry.metadata().map(|data| data.len()).unwrap_or(0);
            let has_content = size > 0;

            // A file this large is data, not a method, and carrying it is a permanent cost to
            // everybody's clone. Measured the day this guard went in: a plan's stem list, 140,947
            // lines and 4.27 MB, rode into a pull request beside the two files of names it had
            // helped find -- because it was a `.txt` in `contrib/` and nothing looked at its size.
            //
            // The rule is the same one `contrib/` exists for: carry the thing that *finds* names,
            // not the working data it was built from. A stem list regenerates from the tables in
            // a minute; the script that writes it is what the next contributor actually needs.
            let is_data = size > BIGGEST_SCRIPT;

            let Some(name) = path.file_name().and_then(|name| name.to_str()) else {
                continue;
            };

            if is_data {
                println!(
                    "  {name} is {:.1} MB, so it is working data rather than a method and is not                      being carried.
    Contribute the script that regenerates it instead.",
                    size as f64 / (1024.0 * 1024.0)
                );
                continue;
            }

            if sensible && has_content && seen.insert(name.to_owned()) {
                found.push(path);
            }
        }
    }

    found.sort();
    found
}

/// Every `run_*` folder in a findings tree, at any depth.
/// Findings that exist on disk but belong to no run folder, gathered into one so they can be sent.
///
/// **This recovers work that was silently unsubmittable.** A pass checkpoints its names into the
/// aggregate `findings/<game>/<type>.txt` every sixty seconds, but wrote its *run folder* only on
/// finishing -- and `submit` sends run folders. So a pass killed part way through (a usage limit,
/// a closed laptop, a crash) left every name it had found on disk in a shape nothing would ever
/// send, and said nothing: the next `submit` reported "nothing new to submit" and looked like
/// success. Contributors running on constrained assistants hit this hardest, which is exactly the
/// group least able to notice it.
///
/// `write_run_as` stops it happening again. This picks up what is already stranded.
///
/// Being over-eager here is safe. Anything already published, merged or claimed is dropped before
/// sending, so the worst case of counting a name stranded when it is not is a batch that comes to
/// nothing -- against a best case of recovering somebody's whole session.
fn recover_stranded(findings: &Path, outbox: &Path) -> Vec<PathBuf> {
    // Keyed on game, type and name, never on the name alone.
    //
    // A bare name set collapses the two titles into one. Measured on this clone: 1,653 names
    // appear in both games' findings, so a name sitting in a Cold War run folder marked the
    // identical Black Ops 4 name as accounted for -- and a killed Black Ops 4 pass then had that
    // name skipped by the recovery written to save it, with no route left to send it. The same
    // collapse applied across types, a name filed under `image` shadowing the identical string
    // stranded under `material`.
    //
    // The game is taken from the directory being walked, never derived by stripping a prefix off
    // a path. An earlier version of this did the latter and passed on Windows while failing two
    // different ways on Linux -- once recovering the wrong game, once recovering nothing -- both
    // explained by `strip_prefix` coming back empty, which silently keys everything as `("", ..)`
    // and makes every name account for every other. The loop already knows which game it is in;
    // asking the filesystem a second time was the whole mistake.
    let mut accounted: HashSet<(String, String, String)> = HashSet::new();

    // Everything already sent. `submissions/<who>_<GAME>_<stamp>/`, so the game is in the name.
    for entry in fs::read_dir(outbox).into_iter().flatten().flatten() {
        let folder = entry.path();
        // `<who>_<GAME>_<stamp>`, except for the folders that predate the per-game split and
        // are `<who>_<stamp>`. Those cannot be attributed to a game from their name at all.
        //
        // An earlier version guessed Cold War for them. That is wrong and measurably so: the
        // largest of them, `GoastcraftHD_20260819-045229`, is the 13,858-name Black Ops 4 grind
        // CLAUDE.md Â§4 describes -- 2,968 of its 3,026 xmodel ids are in `findings/blkops04`.
        // Guessing made those names account for Cold War, where a genuinely stranded Cold War
        // name matching one of the 13,858 strings would then never be recovered. Silent loss, in
        // the function written to prevent it, and reachable through the 1,653 names both games
        // share.
        //
        // So an unattributable folder accounts for *nothing*. That costs churn -- its names look
        // stranded and are re-offered -- and churn is dropped at the exclusion step, where loss
        // is not recoverable at all. Under-accounting is the safe direction and this picks it
        // deliberately.
        let folder_name = entry.file_name().to_string_lossy().to_string();
        let tag = folder_name.split('_').nth(1).unwrap_or_default().to_uppercase();
        if !config::GAMES.contains(&tag.as_str()) {
            continue;
        }
        let game = tag;

        for (kind, _, name) in names_in(&folder) {
            // A submission names its files `<kind>_<stamp>.txt`, and the stamp comes off -- but
            // `strip_stamp` reduces `pool_184_20260819-174052` to `pool`, because a trailing
            // `_184` and a trailing stamp look the same to it (see validate.rs). That would key
            // an unidentified-pool name as `pool` here and `pool_184` on the findings side, so
            // the two never meet and every such name is re-recovered on every submit. Only the
            // `<stamp>` suffix is removed, and only when it looks like one.
            let kind = STAMP_SUFFIX
                .find(&kind)
                .map(|at| kind[..at].to_owned())
                .unwrap_or(kind);

            accounted.insert((game.clone(), kind.to_lowercase(), name.to_lowercase()));
        }
    }

    let mut recovered = Vec::new();

    for entry in fs::read_dir(findings).into_iter().flatten().flatten() {
        let game_folder = entry.path();
        if !game_folder.is_dir() {
            continue;
        }

        let game = entry.file_name().to_string_lossy().to_uppercase();

        // Every run folder under this game, superseded ones included. `run_folders` leaves those
        // out on purpose -- they were organised away and must not be sent again -- but this is
        // the other question, has the name been written down anywhere, and there a superseded run
        // counts. Skipping them made every `submit` rebuild a recovery folder holding names that
        // had already gone.
        // This game's run folders only. `accounted` already carries the game in its key, so
        // there is nothing to gain by copying its hundred thousand triples once per game.
        let mut here: HashSet<(String, String, String)> = HashSet::new();
        for folder in every_run_folder(&game_folder) {
            for (kind, _, name) in names_in(&folder) {
                here.insert((game.clone(), kind.to_lowercase(), name.to_lowercase()));
            }
        }

        // The aggregate files sit directly in the game folder; run folders are below it.
        let mut stranded: Vec<(String, u64, String)> = Vec::new();
        for (kind, id, name) in names_in(&game_folder) {
            let key = (game.clone(), kind.to_lowercase(), name.to_lowercase());
            if !here.contains(&key) && !accounted.contains(&key) {
                stranded.push((kind, id, name));
            }
        }

        if stranded.is_empty() {
            continue;
        }

        let into = game_folder.join(format!("run_{}_recovered", stamp()));
        if fs::create_dir_all(&into).is_err() {
            continue;
        }

        let mut by_kind: std::collections::BTreeMap<String, Vec<(u64, String)>> = Default::default();
        for (kind, id, name) in stranded {
            by_kind.entry(kind).or_default().push((id, name));
        }

        let mut wrote = 0;
        for (kind, mut rows) in by_kind {
            rows.sort_by(|a, b| a.1.to_lowercase().cmp(&b.1.to_lowercase()));

            let mut text = String::new();
            for (id, name) in &rows {
                text.push_str(&format!("{id:x},{name}\n"));
            }

            if fs::write(into.join(format!("{kind}.txt")), text).is_ok() {
                wrote += rows.len();
            }
        }

        if wrote == 0 {
            let _ = fs::remove_dir_all(&into);
            continue;
        }

        println!("recovered {wrote} name(s) a killed run left behind, into {}", into.display());
        recovered.push(into);
    }

    recovered
}


/// Every `run_*` folder, superseded ones included, for deciding what is *accounted for*.
///
/// `run_folders` is the list of runs to consider sending and rightly leaves `superseded/` out.
/// This is the other question -- has this name already been written down anywhere -- and there
/// the answer for a superseded run is yes.
fn every_run_folder(findings: &Path) -> Vec<PathBuf> {
    let mut found = Vec::new();
    let Ok(entries) = fs::read_dir(findings) else {
        return found;
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if !path.is_dir() {
            continue;
        }

        if entry.file_name().to_string_lossy().starts_with("run_") {
            // A run still being written is left out of this too, and that is the whole point.
            //
            // `run_folders` refuses to *send* an unfinished folder, so if this counted its names
            // as accounted for, a killed pass would be in neither list: not sendable, and not
            // strandable either. That is precisely the silent loss both the checkpointing and
            // this recovery exist to prevent, rebuilt out of the two fixes for it.
            //
            // Left out here, a killed run's names fall through to the aggregate files, come back
            // as stranded, and are recovered -- which is what `run_folders` already promises in
            // its own comment.
            if slasher::Results::run_unfinished(&path) {
                continue;
            }

            found.push(path);
        } else {
            found.extend(every_run_folder(&path));
        }
    }

    found
}

fn run_folders(findings: &Path) -> Vec<PathBuf> {
    let mut found = Vec::new();
    let Ok(entries) = fs::read_dir(findings) else {
        return found;
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if !path.is_dir() {
            continue;
        }

        let name = entry.file_name().to_string_lossy().to_string();
        if name.starts_with("run_") {
            // A run still being written is not a run to send. Sending one ledgers its folder
            // name, and every name the pass finds afterwards then has no route: `already_sent`
            // skips the folder for ever, and `recover_stranded` will not strand a name that
            // sits inside a run folder. Skipping it here closes both, and loses nothing if the
            // pass is abandoned -- the folder is left out of `accounted` too, so its names come
            // back as stranded and are recovered.
            if slasher::Results::run_unfinished(&path) {
                continue;
            }

            found.push(path);
        } else if name != "superseded" {
            found.extend(run_folders(&path));
        }
    }

    found.sort();
    found
}

/// The `(type, name)` pairs in one run folder.
/// The `(type, id, name)` triples in one run folder.
///
/// **The id is read, never recomputed.** A run records the id it actually matched, and that is
/// the only thing that knows which normalisation produced it. Recomputing from the name assumes
/// backslashes fold -- true for every pool but one. Black Ops 4's SAB sound names keep theirs, so
/// `wave_crash_01.ln100.pc.snd` under a folding hash gives `43802e73bbb1bef9` where the game
/// actually holds `100116a5a23b8100`. Every sound name from that game would have been submitted
/// against a key belonging to nothing.
fn names_in(folder: &Path) -> Vec<(String, u64, String)> {
    let mut found = Vec::new();
    let Ok(entries) = fs::read_dir(folder) else {
        return found;
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) != Some("txt") {
            continue;
        }

        let Some(kind) = path.file_stem().and_then(|s| s.to_str()) else {
            continue;
        };

        let Ok(bytes) = fs::read(&path) else { continue };
        for line in String::from_utf8_lossy(&bytes).lines() {
            let line = line.trim();
            if line.is_empty() {
                continue;
            }

            let (id, name) = match line.split_once(',') {
                Some((key, name)) => match u64::from_str_radix(key.trim(), 16) {
                    Ok(id) => (id, name.trim()),
                    Err(_) => continue,
                },
                None => continue,
            };

            if !name.is_empty() {
                found.push((kind.to_owned(), id, name.to_owned()));
            }
        }
    }

    found
}

/// Every hash the tables resolve: the stored key, and the hash of the stored name.
fn known_hashes(folder: &Path, game: &str) -> HashSet<u64> {
    slasher::database_keys(folder,game)
}

fn already_sent(outbox: &Path) -> HashSet<String> {
    fs::read_to_string(outbox.join(LEDGER))
        .unwrap_or_default()
        .lines()
        .map(|line| line.trim().to_owned())
        .filter(|line| !line.is_empty())
        .collect()
}

/// Notes the runs as sent. Appended, never rewritten, so a crash cannot lose the record and cause
/// the same names to be submitted twice.
fn record(outbox: &Path, sent: &[PathBuf]) {
    let _ = fs::create_dir_all(outbox);

    let mut text = fs::read_to_string(outbox.join(LEDGER)).unwrap_or_default();
    for folder in sent {
        let name = folder.file_name().unwrap_or_default().to_string_lossy();
        text.push_str(&format!("{name}\n"));
    }

    let _ = fs::write(outbox.join(LEDGER), text);
}

/// A script's identity for the ledger: its text, ignoring line endings.
///
/// The same normalisation `same_text` uses, and for the same reason -- git checks a file out with
/// CRLF while a script a run just wrote has LF, so raw bytes would call the identical script two
/// different scripts and the ledger would never match.
fn script_digest(bytes: &[u8]) -> u64 {
    let text: Vec<u8> = bytes.iter().copied().filter(|byte| *byte != b'\r').collect();
    slasher::hash64_raw(&String::from_utf8_lossy(&text))
}

/// The scripts this machine has already carried into a pull request, by content.
fn sent_scripts(outbox: &Path) -> HashMap<u64, String> {
    fs::read_to_string(outbox.join(SCRIPT_LEDGER))
        .unwrap_or_default()
        .lines()
        .filter_map(|line| {
            let (digest, name) = line.trim().split_once(' ')?;
            let digest = u64::from_str_radix(digest, 16).ok()?;
            let name = name.trim();
            (!name.is_empty()).then(|| (digest, name.to_owned()))
        })
        .collect()
}

/// Notes the scripts as carried. Appended, never rewritten, like the run ledger beside it.
///
/// Recorded only after the pull request is open, so a send that fails does not teach this machine
/// that a script it never sent is already upstream -- which would strand that generator with the
/// session, and a generator that dies with its session is the thing `contrib/` exists to prevent.
fn record_scripts(outbox: &Path, carried: &[(u64, String)]) {
    if carried.is_empty() {
        return;
    }

    let _ = fs::create_dir_all(outbox);

    let mut text = fs::read_to_string(outbox.join(SCRIPT_LEDGER)).unwrap_or_default();
    let known = sent_scripts(outbox);
    for (digest, name) in carried {
        if !known.contains_key(digest) {
            text.push_str(&format!("{digest:016x} {name}\n"));
        }
    }

    let _ = fs::write(outbox.join(SCRIPT_LEDGER), text);
}

fn github_user() -> Option<String> {
    let output = github::command()
        .args(["api", "user", "--jq", ".login"])
        .stderr(Stdio::null())
        .output()
        .ok()?;

    if !output.status.success() {
        return None;
    }

    let who = String::from_utf8_lossy(&output.stdout).trim().to_owned();
    if who.is_empty() {
        None
    } else {
        Some(who)
    }
}
/// Sends the batch and opens the pull request, doing the whole of git on the contributor's behalf.
///
/// The point of this program is that somebody who has never used git can contribute, so none of
/// the usual sequence is asked of them. There is no clone, no working copy and no `git` on the
/// machine: the branch is built through GitHub's own API out of the files just written, which
/// means the submissions folder can live anywhere and need not be a repository at all.
///
/// It is one commit rather than one per file, so a run that dies halfway leaves the fork exactly
/// as it was rather than a branch holding half a batch.
fn open_pull_request(
    repo: &str,
    game: &str,
    folder: &Path,
    scripts: &[PathBuf],
    when: &str,
    who: &str,
    names: usize,
    dropped: usize,
    claimed: usize,
    accounts: &str,
    breakdown: &str,
) -> Result<String, String> {
    let branch = format!("findings/{who}-{game}-{when}");
    let base = default_branch(repo)?;

    // The game leads the title. It is the first thing a reviewer needs, and a list of pull
    // requests cannot otherwise show which title a submission is for -- which matters now that
    // both games are ground rather than only whichever one the config happened to default to.
    let title = submission_title(game,who,when,names);

    // Push into a fork, unless this is the maintainer submitting to their own repository, where
    // there is nothing to fork and the branch simply goes straight in.
    let fork = if repo.starts_with(&format!("{who}/")) {
        repo.to_owned()
    } else {
        ensure_fork(repo, who)?
    };

    // A fork that has sat unused for a week is behind. Branching from a stale head still produces
    // a correct pull request, because the diff is taken against the merge base, so this is done
    // for tidiness and its failure is not worth stopping for.
    if fork != repo {
        let _ = gh(&["repo", "sync", &fork, "--source", repo], None);
    }

    // The files, as they will appear in the repository. One folder per submission, named for who
    // sent it and when, so two people submitting at once cannot collide.
    let mut entries = Vec::new();
    for file in files_in(folder) {
        let Some(name) = file.file_name().and_then(|n| n.to_str()) else {
            continue;
        };

        let bytes = fs::read(&file).map_err(|error| format!("could not read {name}: {error}"))?;
        let blob = make_blob(&fork, &bytes)?;
        entries.push((format!("submissions/{who}_{game}_{when}/{name}"), blob));
    }

    // Scripts go to the shared library rather than into the submission folder, because a method
    // nobody can find is a method nobody inherits. Each is stamped like the submission files
    // beside it -- see `library_name`.
    let mut landed: Vec<String> = Vec::new();

    // What this machine has already sent, which is not the same as what is on its disk. The
    // outbox is the submission folder's parent; falling back to the configured one keeps this
    // working if a caller ever hands over a folder from somewhere else.
    let outbox = folder.parent().map(Path::to_path_buf).unwrap_or_else(paths::submissions);
    let carried_before = sent_scripts(&outbox);
    let mut carried_now: Vec<(u64, String)> = Vec::new();

    for script in scripts {
        let Some(name) = script.file_name().and_then(|name| name.to_str()) else {
            continue;
        };

        let bytes = fs::read(script).map_err(|error| format!("could not read {name}: {error}"))?;

        // Already in the library, byte for byte bar line endings: send nothing at all.
        //
        // Reusing the name was not enough. The blob still went up, and since git checks the
        // library copy out with CRLF while the copy being sent has LF, the pull request rewrote
        // every line of a file whose content had not changed -- 95 insertions and 95 deletions on
        // a no-op. Two pull requests carried that before anybody looked.
        let (stem, extension) = name.rsplit_once('.').unwrap_or((name, "py"));
        if let Some(existing) = already_in_library(strip_stamp(stem), extension, &bytes) {
            println!("  {name} is already in the library as {existing}; not sending it again");
            landed.push(existing);
            continue;
        }

        // Not on disk, but this machine has sent it before -- the pull request carrying it has
        // simply not merged and come back down yet. Sending it again is what filled
        // `scripts/contributed/` with six copies of one script.
        // The ledger as it will be, not only as it was: two scripts in one batch can be the same
        // text under two names, and the second must not go up either.
        let digest = script_digest(&bytes);
        let already = carried_before.get(&digest).or_else(|| {
            carried_now.iter().find(|(seen, _)| *seen == digest).map(|(_, name)| name)
        });

        if let Some(existing) = already {
            println!("  {name} has already gone up as {existing}; not sending it again");
            landed.push(existing.clone());
            continue;
        }

        let target = library_name(name, &when, &bytes);
        let blob = make_blob(&fork, &bytes)?;
        entries.push((format!("scripts/contributed/{target}"), blob));
        landed.push(target.clone());
        carried_now.push((digest, target));
    }

    if entries.is_empty() {
        return Err("the batch folder held no files to send".to_owned());
    }

    // **Branched from upstream's head, not the fork's.** A submission is "everything upstream has,
    // plus these files", and saying so exactly is what keeps a pull request to the two text files
    // it is about. A fork that has *diverged* -- rather than merely fallen behind -- drags its own
    // extra commits into the diff, and the ones it has are binaries: a fork used to run this
    // project's own binary workflows, so `submit`'s sync above pushed `src/**` to the fork's
    // `main`, the fork's Actions rebuilt `bin/linux` and `bin/macos` there, and every later
    // submission carried that rebuild. Git cannot merge a binary, so each one conflicted against
    // whatever this repository had built since -- and one submission had to be taken by hand
    // "without the binary". The workflows now refuse to run outside this repository, but every
    // fork that already drifted stays drifted, so the fix has to hold here too.
    //
    // Upstream and its forks share one object store, so a commit created in the fork may name an
    // upstream commit as its parent. A fork detached from that network -- upstream deleted, made
    // private, or the fork turned standalone -- refuses it, and then the fork's own head still
    // produces a correct pull request. So the whole build is attempted upstream-first and retried
    // from the fork's head, rather than only the two reads being guarded: reading upstream's ref
    // is a public GET that succeeds whenever `default_branch` did, so a fallback wrapped around
    // *that* would never once have run, while the calls that actually get refused -- creating the
    // tree and the commit in the fork against a cross-repo sha -- would still have aborted the
    // submission. Which would be a regression: branching from the fork's head always worked.
    let base_from = |source: &str| -> Result<(String, String), String> {
        let parent = head_sha(source, &base)?;
        let base_tree = tree_of(source, &parent)?;
        Ok((parent, base_tree))
    };

    let build = |parent: &str, base_tree: &str| -> Result<String, String> {
        let tree = make_tree(&fork, base_tree, &entries)?;
        make_commit(&fork, &title, &tree, parent)
    };

    let commit = match base_from(repo).and_then(|(parent, tree)| build(&parent, &tree)) {
        Ok(commit) => commit,
        // Only for a refusal, never for a bad afternoon. A rate limit or a 5xx is an error too,
        // and falling back on one would quietly hand the drifted fork exactly the pull request
        // this went to the trouble of avoiding -- with nothing but a line of output to say so.
        // A sha the fork cannot see is refused as 404 or 422; those are the two worth retrying.
        Err(why) if fork != repo && refused_the_upstream_sha(&why) => {
            println!("  upstream's head was refused, branching from the fork's own: {why}");
            let (parent, base_tree) = base_from(&fork)?;
            build(&parent, &base_tree)?
        }
        Err(why) => return Err(why),
    };

    make_branch(&fork, &branch, &commit)?;

    let contributed = if landed.is_empty() {
        String::new()
    } else {
        let listed: Vec<String> = landed
            .iter()
            .map(|name| format!("- `scripts/contributed/{name}`"))
            .collect();

        format!(
            "\n\n## Tooling this run leaves behind\n\n{}\n\nThese are the scripts that produced \
             the names above. They are here so the next contributor inherits the method rather \
             than only its output.",
            listed.join("\n")
        )
    };

    let body = format!(
        "**{game}** â€” {names} asset names, confirmed against that game's own loaded assets.\n\n\
{breakdown}\n\
         **Checked against, at the moment of sending:** the community hash tables (refreshed \
         first), every merged submission in this repository, and every pull request open right \
         now. A name any of those already holds was dropped rather than sent.\n\n\
         - dropped as already published: {dropped}\n\
         - dropped as already claimed by a merged or open submission: {claimed}\n\
         - submitted by: @{who}\n\n\
         Files are named with the time they were sent, so nothing collides with an earlier batch. \
         Every hash here is re-verified against the shipped snapshot by CI; nothing is taken on \
         the word of the client that found it.\n\n\
         ## How these were found\n{accounts}{contributed}",
    );

    // `who:branch` is how GitHub names a branch that lives in somebody else's fork.
    let head = if fork == repo { branch.clone() } else { format!("{who}:{branch}") };

    let opened = gh(
        &[
            "api",
            &format!("repos/{repo}/pulls"),
            "-X",
            "POST",
            "-f",
            &format!("title={title}"),
            "-f",
            &format!("head={head}"),
            "-f",
            &format!("base={base}"),
            "-f",
            &format!("body={body}"),
            "--jq",
            ".html_url",
        ],
        None,
    );

    // Only once the pull request exists. A script recorded as carried by a send that failed would
    // never be sent by this machine again, and the generator would die with the session.
    if opened.is_ok() {
        record_scripts(&outbox, &carried_now);
    }

    opened
}

/// Every file directly inside the batch folder, in a settled order.
fn files_in(folder: &Path) -> Vec<PathBuf> {
    let mut found: Vec<PathBuf> = fs::read_dir(folder)
        .into_iter()
        .flatten()
        .flatten()
        .map(|entry| entry.path())
        .filter(|path| path.is_file())
        .collect();

    found.sort();
    found
}

/// The branch a pull request should be opened against, asked of the repository rather than assumed
/// to be `main` -- upstream has been called `master` for years in this corner of the world.
fn default_branch(repo: &str) -> Result<String, String> {
    gh(&["api", &format!("repos/{repo}"), "--jq", ".default_branch"], None)
}

/// The contributor's fork, made if they have not got one.
///
/// Forking is asynchronous: GitHub answers before the repository exists, so the fork is waited for
/// rather than used immediately. Somebody who already has a fork skips the wait entirely.
fn ensure_fork(repo: &str, who: &str) -> Result<String, String> {
    let name = repo.split('/').next_back().unwrap_or(repo);
    let fork = format!("{who}/{name}");

    if gh(&["api", &format!("repos/{fork}"), "--jq", ".name"], None).is_ok() {
        return Ok(fork);
    }

    println!("making your fork of {repo}");
    gh(&["repo", "fork", repo, "--clone=false"], None)
        .map_err(|why| format!("could not fork {repo}: {why}"))?;

    for _ in 0..30 {
        if gh(&["api", &format!("repos/{fork}"), "--jq", ".name"], None).is_ok() {
            return Ok(fork);
        }
        std::thread::sleep(std::time::Duration::from_secs(1));
    }

    Err(format!("{fork} was asked for but has not appeared after thirty seconds"))
}

/// Whether GitHub refused a cross-repository sha, rather than merely having a bad moment.
///
/// A fork shares its parent's object store, so a commit created in the fork may name an upstream
/// commit as its parent -- unless that fork has been detached from the network, when the sha is
/// simply not there and the API says so with a 404 or a 422. Every other failure is transient and
/// must not be treated as "use the fork's head instead", because the fork's head is what carries
/// the drift this branching exists to leave behind.
fn refused_the_upstream_sha(why: &str) -> bool {
    let why = why.to_lowercase();
    why.contains("404") || why.contains("422") || why.contains("not found")
}

fn head_sha(repo: &str, branch: &str) -> Result<String, String> {
    gh(
        &["api", &format!("repos/{repo}/git/ref/heads/{branch}"), "--jq", ".object.sha"],
        None,
    )
}

fn tree_of(repo: &str, commit: &str) -> Result<String, String> {
    gh(&["api", &format!("repos/{repo}/git/commits/{commit}"), "--jq", ".tree.sha"], None)
}

/// Uploads one file's bytes. Base64 rather than plain text, so a name holding something that is
/// not valid utf-8 is carried exactly rather than mangled on the way.
fn make_blob(repo: &str, bytes: &[u8]) -> Result<String, String> {
    let body = format!("{{\"content\":\"{}\",\"encoding\":\"base64\"}}", base64(bytes));
    gh(&["api", &format!("repos/{repo}/git/blobs"), "--input", "-", "--jq", ".sha"], Some(&body))
}

/// Lays the new files on top of the branch as it already stands. Without `base_tree` this would
/// describe a repository holding nothing but the submission.
fn make_tree(repo: &str, base_tree: &str, entries: &[(String, String)]) -> Result<String, String> {
    let files: Vec<String> = entries
        .iter()
        .map(|(path, blob)| {
            format!(
                "{{\"path\":{},\"mode\":\"100644\",\"type\":\"blob\",\"sha\":{}}}",
                quoted(path),
                quoted(blob)
            )
        })
        .collect();

    let body = format!(
        "{{\"base_tree\":{},\"tree\":[{}]}}",
        quoted(base_tree),
        files.join(",")
    );

    gh(&["api", &format!("repos/{repo}/git/trees"), "--input", "-", "--jq", ".sha"], Some(&body))
}

fn make_commit(repo: &str, message: &str, tree: &str, parent: &str) -> Result<String, String> {
    let body = format!(
        "{{\"message\":{},\"tree\":{},\"parents\":[{}]}}",
        quoted(message),
        quoted(tree),
        quoted(parent)
    );

    gh(&["api", &format!("repos/{repo}/git/commits"), "--input", "-", "--jq", ".sha"], Some(&body))
}

fn make_branch(repo: &str, branch: &str, commit: &str) -> Result<String, String> {
    gh(
        &[
            "api",
            &format!("repos/{repo}/git/refs"),
            "-X",
            "POST",
            "-f",
            &format!("ref=refs/heads/{branch}"),
            "-f",
            &format!("sha={commit}"),
            "--jq",
            ".ref",
        ],
        None,
    )
}

/// Runs `gh`, which already knows who the contributor is, and returns what it said.
///
/// Failures carry gh's own words rather than an exit code, because the useful part of a refused
/// request is the sentence GitHub sent back with it.
fn gh(args: &[&str], body: Option<&str>) -> Result<String, String> {
    let mut command = github::command();
    command.args(args).stdout(Stdio::piped()).stderr(Stdio::piped());

    if body.is_some() {
        command.stdin(Stdio::piped());
    }

    let mut child = command.spawn().map_err(|error| format!("gh could not be run: {error}"))?;

    if let Some(text) = body {
        use std::io::Write;
        let mut stdin = child.stdin.take().ok_or("gh would not take the request body")?;
        stdin
            .write_all(text.as_bytes())
            .map_err(|error| format!("the request body could not be sent to gh: {error}"))?;
    }

    let output = child.wait_with_output().map_err(|error| format!("gh did not finish: {error}"))?;

    if !output.status.success() {
        let said = format!(
            "{}{}",
            String::from_utf8_lossy(&output.stderr),
            String::from_utf8_lossy(&output.stdout)
        );

        return Err(said.trim().to_owned());
    }

    Ok(String::from_utf8_lossy(&output.stdout).trim().to_owned())
}

/// A json string, escaped. Only the handful of things json insists on, since everything here is a
/// path, a sha or a message this program wrote itself.
fn quoted(text: &str) -> String {
    let mut out = String::with_capacity(text.len() + 2);
    out.push('"');

    for character in text.chars() {
        match character {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }

    out.push('"');
    out
}

/// Base64, written out rather than depended on: a build with no features has no dependencies at
/// all, and that is the property that lets this be published in the first place.
fn base64(bytes: &[u8]) -> String {
    const ALPHABET: &[u8; 64] =
        b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

    let mut out = String::with_capacity(bytes.len().div_ceil(3) * 4);

    for chunk in bytes.chunks(3) {
        let a = chunk[0] as u32;
        let b = *chunk.get(1).unwrap_or(&0) as u32;
        let c = *chunk.get(2).unwrap_or(&0) as u32;
        let triple = (a << 16) | (b << 8) | c;

        out.push(ALPHABET[(triple >> 18) as usize & 63] as char);
        out.push(ALPHABET[(triple >> 12) as usize & 63] as char);
        out.push(if chunk.len() > 1 { ALPHABET[(triple >> 6) as usize & 63] as char } else { '=' });
        out.push(if chunk.len() > 2 { ALPHABET[triple as usize & 63] as char } else { '=' });
    }

    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use slasher::hash64;

    #[test]
    fn submission_exclusions_use_each_games_hash_family() {
        let root = std::env::temp_dir().join(format!("submit_scopes_{}", std::process::id()));
        fs::create_dir_all(&root).unwrap();
        let name = "modern_asset_name";
        let modern = slasher::games::hash("MODWAR22","image",name,true);
        let legacy = hash64(name);
        // Stored keys are authoritative; the spelling also excludes its correct hash family.
        fs::write(root.join("fnv1a_ximages_v2.csv"), format!("{:x},{name}\n",modern&ID_MASK)).unwrap();
        fs::write(root.join("fnv1a_ximages.csv"), "2,legacy_only_fixture\n").unwrap();
        fs::write(root.join("fnv1a_soundbanks_aliases_v2.csv"), "92b109bc210b8729,alias_fixture\n").unwrap();
        fs::write(root.join("fnv1a_xsounds_v2.csv"), "123,saluki/display/path.ln.75.all\n").unwrap();
        for game in config::GAMES {
            let known = known_hashes(&root,game);
            if slasher::games::modern(game) {
                assert!(known.contains(&modern) && known.contains(&(modern & ID_MASK)));
                assert!(!known.contains(&legacy) && !known.contains(&2));
                assert!(!known.contains(&(slasher::games::hash(game,"sound_asset","saluki/display/path.ln.75.all",true)&ID_MASK)));
            } else { assert!(!known.contains(&legacy) && known.contains(&2)); }
            assert!(known.contains(&0x92b109bc210b8729) && known.contains(&(0x92b109bc210b8729 & ID_MASK)));
            assert!(known.contains(&0x123));
        }
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn all_seven_games_preserve_matched_keys_paths_and_titles() {
        let root = std::env::temp_dir().join(format!("submit_seven_games_{}", std::process::id()));
        for game in config::GAMES {
            let run = root.join(game.to_lowercase()).join("run_20261008-010000_test");
            fs::create_dir_all(&run).unwrap();
            let alias="fly_npc_ar_able18_ubgl_reload_07";
            let sound=if game == &"BLKOPS04" { "amb\\environment\\water\\waves\\crash\\wave_crash_01.ln100.pc.snd" } else { "sound.fixture.ln.75.48000.all" };
            let rows = vec![
                ("image".to_owned(),slasher::games::output_key(game,"image","test_image",true),"test_image".to_owned()),
                ("sound_alias".to_owned(),slasher::games::output_key(game,"sound_alias",alias,true),alias.to_owned()),
                ("sound_asset".to_owned(),slasher::games::output_key(game,"sound_asset",sound,game != &"BLKOPS04"),sound.to_owned()),
            ];
            for (kind,id,name) in &rows { fs::write(run.join(format!("{kind}.txt")),format!("{id:x},{name}\n")).unwrap(); }
            let prepared=prepare_batch(game,&[run.clone()],&HashSet::new(),&recon::Landscape::default(),&HashSet::new());
            assert_eq!(prepared.rows.len(),3);
            let into=root.join(format!("contributor_{game}_20261008-010000"));
            write_batch_files(&into,"20261008-010000",&prepared.rows).unwrap();
            let roundtrip:HashSet<_>=names_in(&into).into_iter().map(|(kind,id,name)|(strip_stamp(&kind).to_owned(),id,name)).collect();
            assert_eq!(roundtrip,rows.into_iter().collect());
            assert!(submission_title(game,"contributor","20261008-010000",3).starts_with(&format!("[{game}]")));
            let alias_row=roundtrip.iter().find(|(kind,_,_)|kind=="sound_alias").unwrap();
            assert_eq!(alias_row.1> ID_MASK,slasher::games::modern(game));
        }
        assert_eq!(run_folders(&root).len(),7);
        fs::remove_dir_all(root).unwrap();
    }

    /// Optional offline audit against external captures and local tables. Never invokes main,
    /// authentication, refresh, GitHub, commits, branches or the submission ledger.
    #[test]
    #[ignore]
    fn offline_real_discovery_batches() {
        let discoveries=PathBuf::from(std::env::var("HSS_TEST_DISCOVERIES").expect("HSS_TEST_DISCOVERIES required"));
        let csv=PathBuf::from(std::env::var("HSS_TEST_CSV").expect("HSS_TEST_CSV required"));
        let claims=PathBuf::from(std::env::var("HSS_TEST_CLAIMS").expect("HSS_TEST_CLAIMS required"));
        let out=PathBuf::from(std::env::var("HSS_TEST_OUT").expect("HSS_TEST_OUT required"));
        assert!(!out.exists(),"preserving existing audit output");
        let cached:HashSet<_>=fs::read_to_string(claims).unwrap().lines().filter_map(|x|u64::from_str_radix(x.trim(),16).ok()).collect();
        let mut summary=String::from("game,packaged,note\n");
        for game in config::GAMES {
            let run=discoveries.join(game.to_lowercase());
            let expected:HashSet<_>=names_in(&run).into_iter().collect();
            assert!(!expected.is_empty());
            let known=known_hashes(&csv,game);
            assert!(slasher::tables_look_complete(&known));
            // The external database can advance after these names were discovered. Its
            // stored capture keys decide which fixtures should now be held back.
            let unpublished:HashSet<_>=expected.iter().filter(|(_,id,_)|
                !known.contains(id) && !known.contains(&(id&ID_MASK)) &&
                !cached.contains(id) && !cached.contains(&(id&ID_MASK))).cloned().collect();
            let prepared=prepare_batch(game,&[run.clone(),run.clone()],&known,&recon::Landscape::default(),&cached);
            assert_eq!(prepared.rows.iter().cloned().collect::<HashSet<_>>(),unpublished,"{game}: unpublished discoveries dropped or mutated, or published names retained");
            // A cached claim must exclude exactly its one matched row, including full-width aliases.
            if !prepared.rows.is_empty() {
            let mut one_claim=cached.clone();
            one_claim.insert(prepared.rows[0].1&ID_MASK);
            let filtered=prepare_batch(game,&[run],&known,&recon::Landscape::default(),&one_claim);
            assert_eq!(filtered.rows.len()+1,prepared.rows.len());
            }
            let into=out.join(format!("offline_{game}_20261008-010000"));
            write_batch_files(&into,"20261008-010000",&prepared.rows).unwrap();
            let roundtrip:HashSet<_>=names_in(&into).into_iter().map(|(kind,id,name)|(strip_stamp(&kind).to_owned(),id,name)).collect();
            assert_eq!(roundtrip,unpublished);
            summary.push_str(&format!("{game},{},passed exact serialization and claim exclusion; {} fixture(s) already published or claimed\n",prepared.rows.len(),expected.len()-unpublished.len()));
        }
        fs::write(out.join("audit.csv"),summary).unwrap();
    }

    #[test]
    fn reading_a_modern_alias_does_not_clear_its_top_bit() {
        let folder = std::env::temp_dir().join(format!("hss_alias_width_{}", std::process::id()));
        fs::create_dir_all(&folder).unwrap();
        let file = folder.join("sound_alias.txt");
        fs::write(&file, "92b109bc210b8729,fly_npc_ar_able18_ubgl_reload_07\n").unwrap();
        let rows = names_in(&folder);
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0].1, 0x92b109bc210b8729);
        fs::remove_file(file).unwrap();
        fs::remove_dir(folder).unwrap();
    }

    /// A run killed mid-flight is sent by nobody and recovered by somebody.
    ///
    /// This is the interaction, and it is where two separately correct fixes cancelled out.
    /// `run_folders` refuses to send a folder still marked `.incomplete`, which is right: a
    /// partial batch must not be submitted and its folder name written into the ledger. The
    /// recovery has to be the other half of that -- if it *also* treats the folder as accounted
    /// for, the names are in neither list and nothing will ever send them, which is the exact
    /// silent loss the checkpointing was added to prevent, rebuilt out of its own cure.
    ///
    /// Both halves are asserted here, because either one alone passes while the pair is broken.
    #[test]
    fn a_killed_run_is_neither_sent_nor_forgotten() {
        let root = std::env::temp_dir().join(format!("killed_{}", std::process::id()));
        let _ = fs::remove_dir_all(&root);

        let findings = root.join("findings");
        let game = findings.join("blkops04");
        let run = game.join("run_20260821-090000_images");
        let outbox = root.join("submissions");
        fs::create_dir_all(&run).unwrap();
        fs::create_dir_all(&outbox).unwrap();

        // A checkpointing pass: names in the aggregate, the same names in a run folder that is
        // still marked unfinished because the pass was killed before it sealed them.
        fs::write(game.join("xmodel.txt"), "4444444444444444,found_before_the_kill\n").unwrap();
        fs::write(run.join("xmodel.txt"), "4444444444444444,found_before_the_kill\n").unwrap();
        fs::write(run.join(slasher::INCOMPLETE), "still running\n").unwrap();

        assert!(
            run_folders(&findings).is_empty(),
            "an unfinished run must not be offered for sending"
        );

        let recovered = recover_stranded(&findings, &outbox);
        let where_to: Vec<String> = recovered.iter().map(|p| p.display().to_string()).collect();

        assert!(
            recovered.iter().any(|path| path.starts_with(&game)),
            "a killed run is refused by `run_folders` and must therefore be recovered, or its \
             names can never be sent by any route. recovered: {where_to:?}"
        );

        let _ = fs::remove_dir_all(&root);
    }

    /// The same name in both games is two names, and one being safe does not save the other.
    ///
    /// `accounted` used to be a set of bare lowercase names, so a name sitting in a Cold War run
    /// folder marked the identical Black Ops 4 name as accounted for. Measured on this clone:
    /// 1,653 names appear in both games' findings, so a killed Black Ops 4 pass could have any of
    /// them silently skipped by the recovery written to save it.
    #[test]
    fn a_name_in_one_game_does_not_account_for_the_other() {
        let root = std::env::temp_dir().join(format!("crossgame_{}", std::process::id()));
        let _ = fs::remove_dir_all(&root);

        let findings = root.join("findings");
        let cw = findings.join("blkopscw");
        let bo4 = findings.join("blkops04");
        let outbox = root.join("submissions");
        fs::create_dir_all(cw.join("run_20260820-010101_all")).unwrap();
        fs::create_dir_all(&bo4).unwrap();
        fs::create_dir_all(&outbox).unwrap();

        // Cold War holds this name in a run folder, so Cold War's copy is accounted for.
        fs::write(cw.join("xmodel.txt"), "1111111111111111,shared_between_games\n").unwrap();
        fs::write(
            cw.join("run_20260820-010101_all").join("xmodel.txt"),
            "1111111111111111,shared_between_games\n",
        )
        .unwrap();

        // Black Ops 4 holds the same name, stranded by a kill, in no run folder at all.
        fs::write(bo4.join("xmodel.txt"), "1111111111111111,shared_between_games\n").unwrap();

        let recovered = recover_stranded(&findings, &outbox);

        let where_to: Vec<String> = recovered.iter().map(|p| p.display().to_string()).collect();

        assert!(
            recovered.iter().any(|path| path.starts_with(&bo4)),
            "the Black Ops 4 copy was treated as accounted for because Cold War held the same \
             name, so a killed pass loses it with nothing said. recovered: {where_to:?}"
        );
        assert!(
            !recovered.iter().any(|path| path.starts_with(&cw)),
            "Cold War's copy sits in a run folder and should not have been recovered. \
             recovered: {where_to:?}"
        );

        let _ = fs::remove_dir_all(&root);
    }

    /// A superseded run still accounts for its names, so they are not recovered again and again.
    ///
    /// `run_folders` skips `superseded/` on purpose -- those results were organised away and must
    /// not be sent twice. Asking the *other* question with the same walk left their names looking
    /// stranded, so every `submit` built a fresh recovery folder holding names that had already
    /// gone. They died at the exclusion step, so it was churn rather than loss, but an overnight
    /// rotation submits after every job and that is dozens of folders for nothing.
    #[test]
    fn a_superseded_run_still_accounts_for_its_names() {
        let root = std::env::temp_dir().join(format!("superseded_{}", std::process::id()));
        let _ = fs::remove_dir_all(&root);

        let findings = root.join("findings");
        let game = findings.join("blkops04");
        let outbox = root.join("submissions");
        fs::create_dir_all(game.join("superseded").join("run_20260819-010101_all")).unwrap();
        fs::create_dir_all(&outbox).unwrap();

        fs::write(game.join("xmodel.txt"), "3333333333333333,filed_away_earlier\n").unwrap();
        fs::write(
            game.join("superseded")
                .join("run_20260819-010101_all")
                .join("xmodel.txt"),
            "3333333333333333,filed_away_earlier\n",
        )
        .unwrap();

        let recovered = recover_stranded(&findings, &outbox);

        assert!(
            recovered.is_empty(),
            "a name held by a superseded run was recovered again, which every submit would repeat"
        );

        let _ = fs::remove_dir_all(&root);
    }

    /// A pass killed before it wrote its run folder is recovered, and one that was not is left be.
    ///
    /// This is the failure it guards: names checkpointed into the aggregate file every sixty
    /// seconds, no run folder because the pass never finished, and `submit` sending only run
    /// folders -- so the work existed on disk and could never be sent, silently.
    #[test]
    fn a_killed_run_is_recovered_from_the_aggregate_files() {
        let root = std::env::temp_dir().join(format!("stranded_{}", std::process::id()));
        let _ = fs::remove_dir_all(&root);

        let findings = root.join("findings");
        let game = findings.join("blkops04");
        let outbox = root.join("submissions");
        fs::create_dir_all(game.join("run_20260820-010101_all")).unwrap();
        fs::create_dir_all(&outbox).unwrap();

        // Two names in the aggregate. One belongs to a run folder; the other is stranded.
        fs::write(
            game.join("xmodel.txt"),
            "1111111111111111,already_in_a_run
2222222222222222,stranded_by_a_kill
",
        )
        .unwrap();
        fs::write(
            game.join("run_20260820-010101_all").join("xmodel.txt"),
            "1111111111111111,already_in_a_run
",
        )
        .unwrap();

        let recovered = recover_stranded(&findings, &outbox);
        assert_eq!(recovered.len(), 1, "the stranded name was not recovered");

        let rows = names_in(&recovered[0]);
        assert_eq!(rows.len(), 1, "recovered the wrong number of names");
        assert_eq!(rows[0].0, "xmodel", "recovered under the wrong asset type");
        assert_eq!(rows[0].2, "stranded_by_a_kill");

        // And it must not recover the same thing twice: the folder it just wrote now accounts
        // for the name, so a second call finds nothing.
        assert!(
            recover_stranded(&findings, &outbox).is_empty(),
            "recovering twice would submit the same names again"
        );

        let _ = fs::remove_dir_all(&root);
    }

    /// The rfc's own examples, plus the two lengths that need padding. A wrong encoder here would
    /// upload a corrupted file that still looked like a successful submission.
    #[test]
    fn base64_matches_the_rfc() {
        for (plain, encoded) in [
            ("", ""),
            ("f", "Zg=="),
            ("fo", "Zm8="),
            ("foo", "Zm9v"),
            ("foob", "Zm9vYg=="),
            ("fooba", "Zm9vYmE="),
            ("foobar", "Zm9vYmFy"),
        ] {
            assert_eq!(base64(plain.as_bytes()), encoded, "encoding {plain:?}");
        }
    }

    /// Bytes above the ascii range go through untouched, which is the reason for encoding the
    /// files at all rather than sending them as text.
    #[test]
    fn base64_carries_bytes_that_are_not_text() {
        assert_eq!(base64(&[0xff, 0xfe, 0xfd]), "//79");
        assert_eq!(base64(&[0x00]), "AA==");
    }

    /// The per-type breakdown: what it says, and that its order is stable.
    ///
    /// Stability matters more than it looks. These lines go into a file that is committed, so an
    /// order that varied between runs would produce a diff that changed for no reason -- and a
    /// diff that changes for no reason is one nobody reads.
    #[test]
    fn the_breakdown_counts_each_type_largest_first() {
        let row = |kind: &str, name: &str| (kind.to_owned(), 0u64, name.to_owned());

        let batch = vec![
            row("image", "a"),
            row("xmodel", "b"),
            row("image", "c"),
            row("image", "d"),
            row("sound_alias", "e"),
            row("xmodel", "f"),
        ];

        assert_eq!(per_type(&batch), "- image: 3\n- xmodel: 2\n- sound_alias: 1\n");

        // Equal counts fall back to alphabetical, so two types of the same size cannot swap
        // places between runs.
        let tie = vec![row("xmodel", "a"), row("image", "b")];
        assert_eq!(per_type(&tie), "- image: 1\n- xmodel: 1\n");

        assert_eq!(per_type(&[]), "");
    }

    /// Working data is not a method, and is not carried into a pull request.
    ///
    /// A stem list of 140,947 lines rode into one because it was a `.txt` in `contrib/` and
    /// nothing looked at its size. Everything a contributor writes lands in that folder, so the
    /// only thing separating a generator from the corpus it was built from is this.
    #[test]
    fn working_data_is_not_carried_as_a_method() {
        let folder = std::env::temp_dir().join(format!("slasher_big_{}", std::process::id()));
        let _ = fs::remove_dir_all(&folder);
        fs::create_dir_all(&folder).expect("a temporary contrib folder");

        let generator = folder.join("generator.py");
        fs::write(&generator, "print('names')
").expect("a small script");

        let corpus = folder.join("stems.txt");
        fs::write(&corpus, vec![b'x'; (BIGGEST_SCRIPT + 1) as usize]).expect("a big list");

        // A list right at the limit is still a method: the cutoff must not punish a long
        // generator with a long docstring, which is the shape this repository wants.
        let wordy = folder.join("wordy.py");
        fs::write(&wordy, vec![b'y'; BIGGEST_SCRIPT as usize]).expect("a long script");

        let carried: Vec<String> = scripts_in(&[folder.clone()])
            .iter()
            .filter_map(|path| Some(path.file_name()?.to_str()?.to_owned()))
            .collect();

        assert!(carried.contains(&"generator.py".to_owned()), "a generator must be carried");
        assert!(carried.contains(&"wordy.py".to_owned()), "a long generator is still a generator");
        assert!(
            !carried.contains(&"stems.txt".to_owned()),
            "working data must not ride along: {carried:?}"
        );

        let _ = fs::remove_dir_all(&folder);
    }

    /// The script ledger recognises a script this machine has already sent, and does so across
    /// the line-ending change git makes on the way to disk.
    ///
    /// This is what stops four submissions in eight minutes carrying four copies of one
    /// generator. It has to survive CRLF, because the copy in `contrib/` has LF and any copy that
    /// has been through a checkout has CRLF; a digest over raw bytes would call those two
    /// different scripts and the ledger would never match a single time.
    #[test]
    fn the_script_ledger_recognises_a_script_already_sent() {
        let outbox = std::env::temp_dir().join(format!("slasher_ledger_{}", std::process::id()));
        let _ = fs::remove_dir_all(&outbox);
        fs::create_dir_all(&outbox).expect("a temporary outbox");

        let script = b"print('hello')\nprint('again')\n";
        let checked_out = b"print('hello')\r\nprint('again')\r\n";
        let different = b"print('hello')\nprint('changed')\n";

        assert!(sent_scripts(&outbox).is_empty(), "a fresh outbox has sent nothing");

        let digest = script_digest(script);
        record_scripts(&outbox, &[(digest, "soundxfer_20260821-085126.py".to_owned())]);

        let ledger = sent_scripts(&outbox);
        assert_eq!(
            ledger.get(&script_digest(checked_out)).map(String::as_str),
            Some("soundxfer_20260821-085126.py"),
            "line endings must not make one script look like two"
        );
        assert!(
            !ledger.contains_key(&script_digest(different)),
            "an edited generator is a new script and must still be carried"
        );

        // Recording the same script twice must not grow the ledger, or a night of submissions
        // leaves a file with one line per send.
        record_scripts(&outbox, &[(digest, "soundxfer_20260821-085126.py".to_owned())]);
        assert_eq!(sent_scripts(&outbox).len(), 1, "the ledger must not accumulate duplicates");

        let _ = fs::remove_dir_all(&outbox);
    }

    /// A contributed script is stamped, and re-stamping never compounds.
    ///
    /// The compounding case is the one worth pinning: a contributor pulls the library, edits
    /// `slotswap_20260819-225818.py` and submits it. Naively appending would give
    /// `slotswap_20260819-225818_20260820-0130.py`, and the run after that would add a third.
    /// The stamp is replaced, not accumulated, so the base name stays readable for ever.
    #[test]
    fn contributed_scripts_are_stamped_once() {
        let when = "20260820-013000";

        assert_eq!(library_name("slotswap.py", when, b"x"), "slotswap_20260820-013000.py");
        assert_eq!(
            library_name("slotswap_20260819-225818.py", when, b"x"),
            "slotswap_20260820-013000.py",
            "an already-stamped script must not gain a second stamp"
        );

        // A name with underscores of its own keeps them: only the stamp comes off.
        assert_eq!(
            library_name("image_siblings.py", when, b"x"),
            "image_siblings_20260820-013000.py"
        );

        // Extensionless, and non-python, both survive.
        assert_eq!(library_name("gen", when, b"x"), "gen_20260820-013000.py");
        assert_eq!(library_name("gen.sh", when, b"x"), "gen_20260820-013000.sh");
    }

    /// A file on the disk but absent from git is not the library.
    ///
    /// The case this pins cost a generator. `already_in_library` read `scripts/` off the
    /// filesystem, so a script written straight into that folder during a run matched *itself*
    /// and was skipped as already present -- while nothing upstream held it.
    /// `materials_from_images.py` was named by pull requests #204 and #205 on 2026-08-20 and
    /// carried by neither.
    ///
    /// Goes through the real folder for the same reason the test below does: the stamping had a
    /// passing unit test over a fixture and still shipped a live bug.
    ///
    /// Skips rather than fails where git cannot answer, since `tracked_scripts` then falls back
    /// to trusting the disk and there is no invariant left to assert.
    #[test]
    fn a_script_the_repository_does_not_track_is_not_the_library() {
        if tracked_scripts().is_none() {
            return;
        }

        let folder = paths::root().join("scripts");
        if !folder.is_dir() {
            return;
        }

        // Distinctive enough that it cannot collide with a real generator, and removed either
        // way below.
        let name = "zz_untracked_library_probe.py";
        let path = folder.join(name);
        let body = b"# written by a test, never committed\n";

        if path.exists() {
            return;
        }
        if fs::write(&path, body).is_err() {
            return;
        }

        let picked = library_name(name, "20260820-013000", body);
        let _ = fs::remove_file(&path);

        assert_eq!(
            picked, "zz_untracked_library_probe_20260820-013000.py",
            "an untracked file in scripts/ was treated as the library, so a new generator would \
             be silently dropped from the pull request"
        );
    }

    /// A script already in the library is recognised, against the library that actually exists.
    ///
    /// `same_text` on its own only proves the comparison; this proves the lookup around it --
    /// that `strip_stamp` recovers the base name from a stamped file, that the extension check
    /// does not reject it, and that the folder is found where `paths::root()` says. The stamping
    /// had a passing unit test and still shipped a live bug that only a real submission exposed,
    /// which is the reason this one goes through the real folder rather than a fixture.
    ///
    /// Skips rather than fails when the library is empty: a fresh clone has nothing to match, and
    /// a test that demanded otherwise would fail for everyone but us.
    #[test]
    fn a_script_already_in_the_library_is_recognised() {
        let folder = paths::root().join("scripts").join("contributed");
        let Ok(entries) = fs::read_dir(&folder) else {
            return;
        };

        let mut checked = 0;
        for entry in entries.flatten() {
            let path = entry.path();
            let Some(name) = path.file_name().and_then(|name| name.to_str()) else {
                continue;
            };
            if !name.ends_with(".py") {
                continue;
            }

            let Ok(held) = fs::read(&path) else { continue };

            // Offered back under its bare name, exactly as a contributor's `contrib/` copy would
            // arrive, and with the line endings a freshly written file carries rather than the
            // ones git checked this one out with.
            let bare = format!("{}.py", strip_stamp(name.trim_end_matches(".py")));
            let unix: Vec<u8> = held.iter().copied().filter(|byte| *byte != b'\r').collect();

            // The invariant is "reuse something already here", not "reuse this exact file".
            // Asserting the latter looked equivalent and is not: the library really does hold two
            // byte-identical copies of `soundxfer.py` under different stamps, left by two
            // submissions made 48 seconds apart before this dedup worked. Only one of them can be
            // the one returned, so the strict form made a true dedup fail -- and it failed in CI
            // on Linux while passing here, purely because the duplicates arrived between the two
            // runs. What matters is that no *new* stamp is minted.
            let picked = library_name(&bare, "20260820-013000", &unix);
            let reused = folder.join(&picked);

            assert!(
                reused.is_file(),
                "{bare} was stamped afresh as {picked} instead of reusing a library copy"
            );
            assert!(
                fs::read(&reused).is_ok_and(|held| same_text(&held, &unix)),
                "{bare} was matched to {picked}, which holds different content"
            );

            checked += 1;
        }

        if checked > 0 {
            println!("{checked} library script(s) recognised");
        }
    }

    /// The same script is the same script however it reached the disk.
    ///
    /// This is the whole of the deduplication: git hands out CRLF on Windows and a run writes LF,
    /// so a raw byte comparison says every library copy is a different script and every submission
    /// adds another stamped duplicate of it.
    #[test]
    fn line_endings_do_not_make_a_new_script() {
        assert!(same_text(b"print(1)\r\nprint(2)\r\n", b"print(1)\nprint(2)\n"));
        assert!(same_text(b"same", b"same"));
        assert!(!same_text(b"print(1)\n", b"print(2)\n"));

        // A difference that is only a *missing* line must still count as different.
        assert!(!same_text(b"a\r\nb\r\n", b"a\n"));
    }

    /// The rules a contributed script has to pass, asserted rather than trusted: a folder that
    /// is not there is normal and not an error, a build artefact is not a script, an empty file
    /// is worse than none, and the same name reached from two folders is carried once.
    #[test]
    fn only_real_scripts_are_carried() {
        let dir = std::env::temp_dir().join(format!("contrib_{}", std::process::id()));
        let _ = fs::remove_dir_all(&dir);

        let one = dir.join("one");
        let two = dir.join("two");
        fs::create_dir_all(&one).unwrap();
        fs::create_dir_all(&two).unwrap();

        fs::write(one.join("families.py"), b"print('hello')
").unwrap();
        fs::write(one.join("notes.md"), b"what it does
").unwrap();
        fs::write(one.join("a.exe"), b"MZ").unwrap();
        fs::write(one.join("empty.py"), b"").unwrap();
        fs::write(two.join("families.py"), b"a later copy
").unwrap();
        fs::write(two.join("other.rs"), b"fn main() {}
").unwrap();

        let folders = vec![one.clone(), two.clone(), dir.join("not-there")];
        let names: Vec<String> = scripts_in(&folders)
            .iter()
            .map(|path| path.file_name().unwrap().to_string_lossy().to_string())
            .collect();

        assert_eq!(names, vec!["families.py", "notes.md", "other.rs"]);

        // The first folder's copy is the one carried, not the second's.
        let carried = scripts_in(&folders)
            .into_iter()
            .find(|path| path.ends_with("families.py"))
            .unwrap();
        assert!(carried.starts_with(&one));

        let _ = fs::remove_dir_all(&dir);
    }

    /// A path or a message carrying a quote must not be able to break the request open.
    #[test]
    fn json_strings_are_escaped() {
        assert_eq!(quoted("a\"b"), "\"a\\\"b\"");
        assert_eq!(quoted("a\\b"), "\"a\\\\b\"");
        assert_eq!(quoted("a\nb"), "\"a\\nb\"");
        assert_eq!(quoted("plain"), "\"plain\"");
    }
}
