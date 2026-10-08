//! Confirms a plain list of candidate names against what the game holds.
//!
//! This is the piece that makes inventing a method cheap.
//!
//! Every other search here is a *method* compiled into Rust: it decides what candidates are and
//! then tries them. That is right for the handful of methods worth running for hours, and it is
//! completely wrong for the thing this project actually depends on, which is somebody having a
//! new idea about what a name might look like. Under the old shape, having an idea meant writing
//! a Rust binary, and so most ideas were never tried.
//!
//! With this, a method is a script that prints candidate names. Generate them however you like --
//! Python, awk, a language model, a text file typed by hand -- and pipe them in. The expensive,
//! careful half (the game's hash, the unnamed set, exclusion against the tables, the run notes,
//! the results that only ever grow) is done here and is the same for every idea.
//!
//! ```text
//! python scripts/continuations.py | confirm_list - --label "per-prefix continuations"
//! confirm_list candidates.txt --label "weapon families, third attempt"
//! ```
//!
//! Nothing is held in memory except one batch, so a candidate file larger than this machine's
//! RAM is fine -- and a generator that streams costs no disk at all.

use std::collections::HashMap;
use std::io::{Read, Write};
use std::path::Path;
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{Duration, Instant};

use slasher::fingerprint::{Fingerprint, SketchStream};
use slasher::loader::{loaded_assets, wanted_for_search};
use slasher::{futility, 
    config, feed, feed_raw, low_value_reason, paths, pool_label, readiness, recon, table_keys,
    tables_look_complete, Filter, Results, RunNote, ID_MASK,
};

/// Pools no rule can reach. A mesh name ends in twenty-six characters of base32 that are a hash
/// of the mesh itself, so it cannot be produced by any generator and leaving it in the wanted set
/// only doubles what a candidate can hit by coincidence.
const UNREACHABLE: &[&str] = &["xmodelmesh"];

/// How much candidate text is read and swept at a time.
///
/// Bytes rather than lines, and read as raw bytes rather than through `lines()`, because the
/// first version of this did the obvious thing and paid for it: `BufRead::lines()` allocates a
/// `String` per candidate, and at forty million candidates that allocation *was* the program.
/// Measured on this workload it capped the whole tool at 5.2M candidates/s while the hashing
/// itself is an order of magnitude faster than that. Nothing is allocated here until something
/// matches.
const CHUNK: usize = 64 << 20;

/// How often a long run writes what it has found so far.
const SAVE_EVERY: Duration = Duration::from_secs(60);

fn main() {
    readiness::require();
    futility::require();

    let began = Instant::now();

    // Fixed before searching, so the checkpoint and the final write agree on one
    // folder rather than leaving two. See `Results::write_run_as`.
    let when = slasher::stamp();
    let arguments: Vec<String> = std::env::args().skip(1).collect();

    let label = argument(&arguments, "--label").unwrap_or_else(|| "an unnamed method".to_owned());
    let describe = argument(&arguments, "--describe").unwrap_or_else(|| {
        "a candidate list generated outside the search and confirmed here".to_owned()
    });

    // The generator that produced the candidates, so it can ride along without anybody having to
    // remember a copy step afterwards. Naming it is one flag on a command already being typed,
    // and it is the difference between the next contributor inheriting a method and inheriting a
    // list of names -- which is the whole compounding argument this project rests on.
    let script = argument(&arguments, "--script");

    // Black Ops 4's SAB sound names keep their backslashes, and their ids are the hash of exactly
    // that. Folding them -- what every other asset type wants -- produces a hash that matches
    // nothing, for ever, while the run looks entirely normal. Measured: 8,385 of 8,385 known
    // names reproduce unfolded, 0 folded. See `slasher::feed_raw`.
    let fold = !arguments.iter().any(|argument| argument == "--no-fold");
    if !fold {
        println!("hashing without folding backslashes (Black Ops 4 SAB sound names)");
    }

    // Everything that is not a flag and not the value belonging to one. Positional, so that a
    // file which happens to be named the same as the label is still read -- comparing against the
    // label's text would silently drop it, and a candidate file not read is a run that reports
    // success having tested nothing.
    let sources = sources_from(&arguments);

    if sources.is_empty() {
        eprintln!(
            "usage: confirm_list <file>... [--label \"what this method is\"] [--describe \"how it \
             builds candidates\"]\n\n\
             `-` reads standard input, so a generator can be piped straight in:\n\n    \
             python scripts/continuations.py | confirm_list - --label \"per-prefix continuations\"\n\n\
             One candidate name per line. A `hash,name` line is accepted too and the name is \
             taken.\nEverything the tables already resolve is excluded, so what comes out is \
             only what is new.\n\n\
             `--script <path>` names the generator that produced them. `submit` then carries it \
             into the\npull request, so the next contributor inherits the method rather than only \
             its output."
        );
        std::process::exit(2);
    }

    // Every named file is opened *now*, before the snapshot is read and the candidates are swept.
    //
    // This used to be checked inside the sweep, which meant a mistyped filename cost the entire
    // run: the tool confirmed everything piped in, then hit the bad name and exited, discarding
    // what it had found. A run is an hour of somebody's evening. Failing on the first second of it
    // is free; failing on the last is not.
    for source in sources.iter().filter(|source| *source != "-") {
        if let Err(error) = std::fs::File::open(source) {
            eprintln!(
                "{source} could not be read: {error}\n\n\
                 Candidate sources are positional; `-` means standard input. If that was meant to \
                 be a flag's value, the flag is missing from this build's list of flags that take \
                 one -- see TAKES_A_VALUE in src/bin/confirm_list.rs."
            );
            std::process::exit(1);
        }
    }

    let (assets, _) = match loaded_assets() {
        Ok(loaded) => loaded,
        Err(reason) => {
            eprintln!("{reason}");
            std::process::exit(1);
        }
    };

    let known = table_keys();
    if !tables_look_complete(&known) {
        eprintln!("the tables read short. Check {}", paths::tables().display());
        std::process::exit(1);
    }
    println!("hashes already resolved by the tables: {}", known.len());

    let wanted = wanted_for_search(&assets, &known, UNREACHABLE);
    println!("unnamed ids a candidate could land on: {}", wanted.len());
    drop(known);
    drop(assets);

    // The filter answers the overwhelming majority of candidates without touching the map, which
    // is what lets this keep up with a generator rather than becoming the bottleneck itself.
    let policies = slasher::games::groups(&wanted);
    let filter = Filter::sized(wanted.keys(), wanted.len());

    // A run that did not fold must keep its names spelled exactly as they were hashed;
    // see `Results::keeping_spelling`. Folding them here is what left 37 submitted rows
    // whose name does not produce the id beside it.
    let mut results = Results::load(paths::findings());
    if !fold {
        results = results.keeping_spelling();
    }
    let seen = AtomicU64::new(0);
    let mut matched = 0_usize;
    let mut last_saved = Instant::now();
    let mut digest: u64 = 0;
    let mut sketch = SketchStream::new();

    let started = Instant::now();
    let threads = std::thread::available_parallelism().map(|count| count.get()).unwrap_or(8);
    println!("confirming across {threads} threads\n");

    for source in &sources {
        let mut reader: Box<dyn Read> = if source == "-" {
            Box::new(std::io::stdin())
        } else if Path::new(source).extension().and_then(|s|s.to_str()) == Some("csv")
            && Path::new(source).file_stem().and_then(|s|s.to_str()).is_some_and(|s|s.starts_with("fnv1a_")) {
            // A source database CSV contains export paths, not necessarily original names.
            Box::new(std::io::Cursor::new(slasher::read_names(Path::new(source)).join("\n").into_bytes()))
        } else {
            match std::fs::File::open(source) {
                Ok(file) => Box::new(file),
                Err(error) => {
                    eprintln!("{source} could not be read: {error}");
                    std::process::exit(1);
                }
            }
        };

        // One buffer for the whole source. `carry` is the partial last line of the previous
        // chunk, which has to be joined to the start of this one rather than dropped -- a
        // candidate cut in half by a buffer boundary is a candidate silently not tested.
        let mut buffer = vec![0_u8; CHUNK];
        let mut carry: Vec<u8> = Vec::new();

        loop {
            let filled = fill(&mut reader, &mut buffer);
            if filled == 0 {
                break;
            }

            // Only up to the last complete line; the tail becomes the next round's carry.
            let end = buffer[..filled]
                .iter()
                .rposition(|byte| *byte == b'\n')
                .map(|at| at + 1)
                .unwrap_or(0);

            let mut text: Vec<u8> = Vec::with_capacity(carry.len() + end);
            text.extend_from_slice(&carry);
            text.extend_from_slice(&buffer[..end]);

            carry.clear();
            carry.extend_from_slice(&buffer[end..filled]);

            // Sketched on this thread before the sweep takes the chunk.
            //
            // A streamed run has no candidate list to sketch, which is why `confirm_list` recorded
            // none and `scripts/overlap.py` was blind to every invented method -- the half of the
            // project the ledger exists to protect. One extra hash per candidate, single-threaded,
            // against a sweep that hashes the same candidate across sixteen: measured at well
            // under a second per forty million.
            for line in text.split(|byte| *byte == b'\n') {
                if let Ok(candidate) = std::str::from_utf8(line) {
                    let candidate = candidate.trim();
                    if !candidate.is_empty() {
                        sketch.add(candidate);
                    }
                }
            }

            let (hits, counted, chunk_digest) = sweep(&text, &filter, &wanted, threads, fold, &policies);
            digest = digest.wrapping_add(chunk_digest);
            seen.fetch_add(counted, Ordering::Relaxed);
            matched += file_them(hits, &wanted, &mut results);

            report(&seen, started);

            if last_saved.elapsed() >= SAVE_EVERY {
                last_saved = Instant::now();
                match results.write(paths::findings()) {
                    Ok(()) => println!("  checkpoint: {} names safe on disk", results.len()),
                    Err(error) => eprintln!("  a checkpoint could not be written: {error}"),
                }

                // And the run folder, which is what `submit` sends. See `write_run_as`: written
                // only at the end, an interrupted run leaves its names unsubmittable and says
                // nothing about it.
                if let Err(error) = results.write_run_as(paths::findings(), "list", &when) {
                    eprintln!("  the run folder could not be checkpointed: {error}");
                }
            }
        }

        if !carry.is_empty() {
            carry.push(b'\n');
            let (hits, counted, chunk_digest) = sweep(&carry, &filter, &wanted, threads, fold, &policies);
            digest = digest.wrapping_add(chunk_digest);
            seen.fetch_add(counted, Ordering::Relaxed);
            matched += file_them(hits, &wanted, &mut results);
        }
    }

    let candidates = seen.load(Ordering::Relaxed);
    let elapsed = started.elapsed().as_secs_f64().max(0.001);

    println!(
        "\n{candidates} candidates in {:.0}s ({:.1}M/s), {matched} matched, {} of them new",
        elapsed,
        candidates as f64 / elapsed / 1e6,
        results.added()
    );
    println!(
        "names expected to match by chance at this size: {:.4}",
        slasher::expected_by_chance(candidates, wanted.len())
    );

    results.write(paths::findings()).expect("the results");

    // Recorded whatever the outcome, including nothing: a run that finds nothing is a
    // real result, and three of them in a row is a loop. See `futility`.
    futility::record(results.added());


    // Only knowable now: a list run is defined by the candidates it was given, and they arrive on
    // a pipe. Said even when nothing was found, because "somebody already ran this and it also
    // found nothing" is exactly what the next person needs to hear.
    let fingerprint = Fingerprint::of("confirm_list")
        .with("game", &config::game())
        .with("label", &label)
        .with_count("candidates", candidates as usize)
        .with("digest", &format!("{digest:016x}"))
        .finish();

    println!("fingerprint: {fingerprint}");
    recon::note_if_swept(&fingerprint);

    // Sealed below, once written. See `Results::write_run_as`.
    match results.write_run_as(paths::findings(), "list", &when) {
        Ok(Some(folder)) => {
            println!("this run's own names: {}", folder.display());

            let _ = Results::note_run(
                &folder,
                &RunNote::new(label, describe, began.elapsed())
                    .measured("game", config::game())
                    .measured("candidates tested", candidates)
                    .measured("matched", matched)
                    .measured("new", results.added())
                    // The candidates this run actually asked about, summarised so another
                    // run can be compared with it. See `SketchStream`.
                    .measured("sketch stems", sketch.finish())
                    .measured("ids hunted", wanted.len())
                    .measured("throughput", format!("{:.1}M candidates/s", candidates as f64 / elapsed / 1e6))
                    .fingerprint(fingerprint)
                    .next_step(
                        "if this paid, feed what it found back into the generator and run it \
                         again -- every confirmed name is new vocabulary. If it did not, say so \
                         in METHODS.md under the dead ends, which is worth as much as a find.",
                    ),
            );

            // The generator that produced this is the reusable part, and this is the moment it is
            // in somebody's hand. Carried automatically when it was named.
            if let Some(path) = &script {
                match carry_along(&folder, Path::new(path)) {
                    Ok(()) => {
                        println!("carrying {path}; `submit` will put it in the pull request")
                    }
                    Err(why) => eprintln!("{path} could not be carried along: {why}"),
                }
            }

            // After the note and the script, so a folder is never sent without the generator
            // that produced it.
            if let Err(error) = Results::seal_run(&folder) {
                eprintln!("the run folder could not be marked finished: {error}");
            }
        }
        Ok(None) => println!("this run found nothing new"),
        Err(error) => eprintln!("the run folder could not be written: {error}"),
    }

    // Said whether or not anything was found, because both outcomes leave something behind that
    // is worth more than this run's names, and both are forgotten by default.
    match (&script, results.added()) {
        (None, _) => println!(
            "\nNo generator was named, so nothing reusable comes out of this run.\n\
             If a script produced these candidates, re-run it with `--script <path>` -- or drop \
             the script\nin `contrib/` -- and `submit` carries it into the pull request. Seven \
             generators are named in\npast submissions here and exist nowhere; every contributor \
             since has started without them."
        ),
        (Some(path), 0) => println!(
            "\n{path} found nothing new. That is a result, and it is only worth something if it \
             is\nwritten down: add a row to the dead ends table in METHODS.md saying what it \
             tried and what\nit returned. A measured negative costs the next contributor nothing \
             and saves them a night."
        ),
        (Some(_), _) => {}
    }

    let _ = std::io::stdout().flush();
}

/// Reads until the buffer is full or the source runs out, since one `read` need not fill it.
fn fill(reader: &mut Box<dyn Read>, buffer: &mut [u8]) -> usize {
    let mut filled = 0;

    while filled < buffer.len() {
        match reader.read(&mut buffer[filled..]) {
            Ok(0) => break,
            Ok(read) => filled += read,
            Err(error) if error.kind() == std::io::ErrorKind::Interrupted => continue,
            Err(_) => break,
        }
    }

    filled
}

/// Hashes one chunk of candidate text in parallel.
///
/// Returns what matched, how many candidates there were, and their order-independent digest.
/// The workers walk raw bytes and allocate only for a hit, which is what makes this keep up with
/// a generator rather than become the bottleneck itself.
fn sweep(
    text: &[u8],
    filter: &Filter,
    _wanted: &HashMap<u64, usize>,
    threads: usize,
    fold: bool,
    policies: &[(u64, HashMap<u64, usize>)],
) -> (Vec<(u64, String)>, u64, u64) {
    // Split the text into as many pieces as there are threads, each ending on a line boundary.
    let mut bounds = vec![0_usize];
    let step = text.len() / threads.max(1);

    for index in 1..threads {
        let from = (step * index).min(text.len());
        let at = text[from..]
            .iter()
            .position(|byte| *byte == b'\n')
            .map(|offset| from + offset + 1)
            .unwrap_or(text.len());

        if at > *bounds.last().unwrap() {
            bounds.push(at);
        }
    }
    bounds.push(text.len());

    let mut hits: Vec<(u64, String)> = Vec::new();
    let mut counted = 0_u64;
    let mut digest = 0_u64;

    std::thread::scope(|scope| {
        let mut workers = Vec::new();

        for pair in bounds.windows(2) {
            let piece = &text[pair[0]..pair[1]];

            workers.push(scope.spawn(move || {
                let mut found: Vec<(u64, String)> = Vec::new();
                let mut lines = 0_u64;
                let mut digest = 0_u64;

                for line in piece.split(|byte| *byte == b'\n') {
                    let candidate = candidate_bytes(line);
                    if candidate.is_empty() {
                        continue;
                    }

                    lines += 1;

                    // Lower cased always; backslashes folded unless this is the one pool whose
                    // names keep them. See `slasher::feed_raw`.
                    for (basis, targets) in policies {
                        let hash = if fold { feed(*basis, candidate) } else { feed_raw(*basis, candidate) };
                        digest = digest.wrapping_add(hash);
                        let id = hash & ID_MASK;
                        if filter.may_hold(id) && targets.contains_key(&id) {
                            found.push((id, String::from_utf8_lossy(candidate).into_owned()));
                        }
                    }
                }

                (found, lines, digest)
            }));
        }

        for worker in workers {
            let (found, lines, part) = worker.join().expect("a worker");
            hits.extend(found);
            counted += lines;
            digest = digest.wrapping_add(part);
        }
    });

    (hits, counted, digest)
}

/// Files what matched, dropping anything that landed in a pool not worth publishing.
fn file_them(
    hits: Vec<(u64, String)>,
    wanted: &HashMap<u64, usize>,
    results: &mut Results,
) -> usize {
    let mut kept = 0;

    for (id, name) in hits {
        let pool = pool_label(wanted[&id]);

        // A pool that has already cost somebody a night for nothing is not filed, whatever
        // generated it. Otherwise a generator that wanders into `streamkey` fills the results
        // folder with the exact thing this project learned to stop doing.
        if low_value_reason(&pool).is_some() {
            continue;
        }

        kept += 1;
        results.add(&pool, id, name);
    }

    kept
}

fn report(seen: &AtomicU64, started: Instant) {
    let count = seen.load(Ordering::Relaxed);
    let elapsed = started.elapsed().as_secs_f64().max(0.001);

    println!(
        "  {count} candidates  {:.1}M/s  {:.0}s elapsed",
        count as f64 / elapsed / 1e6,
        elapsed
    );
}

/// The candidate on a line, whether it is a bare name or a `hash,name` row.
///
/// Accepting both means a results file, a table row and a generator's raw output are all valid
/// input without anybody having to convert between them.
///
/// Bytes rather than `&str`, so a chunk of candidate text is walked without being validated as
/// utf-8 first. A trailing `\r` is trimmed here and that is not cosmetic: a candidate file
/// written on Windows carries one, it hashes into the name, and it matches nothing. It is the
/// single most likely way to waste a run.
fn candidate_bytes(line: &[u8]) -> &[u8] {
    let mut line = line;

    while let Some((last, rest)) = line.split_last() {
        if last.is_ascii_whitespace() {
            line = rest;
        } else {
            break;
        }
    }

    while let Some((first, rest)) = line.split_first() {
        if first.is_ascii_whitespace() {
            line = rest;
        } else {
            break;
        }
    }

    // A `hash,name` row: hex up to the first comma, and a name after it.
    if let Some(comma) = line.iter().position(|byte| *byte == b',') {
        let (key, rest) = line.split_at(comma);

        if !key.is_empty() && key.len() <= 16 && key.iter().all(u8::is_ascii_hexdigit) {
            let mut name = &rest[1..];
            while let Some((first, tail)) = name.split_first() {
                if first.is_ascii_whitespace() {
                    name = tail;
                } else {
                    break;
                }
            }
            return name;
        }
    }

    line
}

/// Copies the generator into the run's own folder, where `submit` looks for it.
fn carry_along(folder: &Path, script: &Path) -> std::io::Result<()> {
    let name = script.file_name().ok_or_else(|| {
        std::io::Error::new(std::io::ErrorKind::InvalidInput, "that is not a file")
    })?;

    let into = folder.join("contrib");
    std::fs::create_dir_all(&into)?;
    std::fs::copy(script, into.join(name))?;

    Ok(())
}

fn argument(arguments: &[String], flag: &str) -> Option<String> {
    let at = arguments.iter().position(|argument| argument == flag)?;
    arguments.get(at + 1).cloned()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn streaming_candidates_follow_the_target_pools_hash_policy() {
        let asset = "iw9.dst.iw9_dst_street_barricade_03.ln.75.48000.all";
        let alias = "test_alias";
        let asset_id = slasher::feed(slasher::games::IW_BASIS, asset.as_bytes()) & ID_MASK;
        let alias_id = slasher::hash64(alias) & ID_MASK;
        let ordinary = HashMap::from([(asset_id, 17)]);
        let aliases = HashMap::from([(alias_id, 364)]);
        let wanted = HashMap::from([(asset_id, 17), (alias_id, 364)]);
        let policies = vec![(slasher::games::IW_BASIS, ordinary), (slasher::BASIS, aliases)];
        let filter = Filter::new(wanted.keys());
        let text = format!("{asset}\r\n{alias}\nunknown_fixture\n");
        let (hits, counted, _) = sweep(text.as_bytes(), &filter, &wanted, 2, true, &policies);
        assert_eq!(counted, 3);
        assert_eq!(hits.into_iter().collect::<HashMap<_, _>>(), HashMap::from([(asset_id, asset.to_owned()), (alias_id, alias.to_owned())]));
        // A hash at the right value in a pool belonging to the other policy is not a find.
        let swapped = vec![(slasher::BASIS, HashMap::from([(asset_id, 17)])), (slasher::games::IW_BASIS, HashMap::from([(alias_id, 364)]))];
        assert!(sweep(text.as_bytes(), &filter, &wanted, 2, true, &swapped).0.is_empty());
    }

    fn args(list: &[&str]) -> Vec<String> {
        list.iter().map(|value| (*value).to_owned()).collect()
    }

    /// A flag's value is never mistaken for a candidate file.
    ///
    /// `--game` was missing from the list, and the cost was the whole run: `confirm_list - --game
    /// BLKOPS04` took `BLKOPS04` for a filename, confirmed 596,049 candidates happily, and *then*
    /// exited 1 trying to open it -- throwing away everything it had just found. Every contributed
    /// method aimed at one game hit this.
    #[test]
    fn flag_values_are_not_sources() {
        assert_eq!(sources_from(&args(&["-", "--game", "BLKOPS04"])), vec!["-"]);
        assert_eq!(
            sources_from(&args(&["-", "--label", "m", "--script", "s.py", "--game", "BLKOPSCW"])),
            vec!["-"]
        );

        // Real files still arrive, including one named like a flag's value.
        assert_eq!(sources_from(&args(&["names.txt", "--label", "names.txt"])), vec!["names.txt"]);
        assert_eq!(sources_from(&args(&["a.txt", "b.txt"])), vec!["a.txt", "b.txt"]);

        // Every flag that takes a value must be listed, or its value becomes a phantom source.
        for flag in TAKES_A_VALUE {
            assert_eq!(sources_from(&args(&["-", flag, "VALUE"])), vec!["-"], "{flag} kept its value");
        }
    }

    fn candidate_of(line: &str) -> String {
        String::from_utf8_lossy(candidate_bytes(line.as_bytes())).into_owned()
    }

    /// Both input shapes are accepted, so a results file can be piped back in unchanged.
    #[test]
    fn a_row_and_a_bare_name_both_yield_the_name() {
        assert_eq!(candidate_of("1a2b3c,mc/mtl_thing"), "mc/mtl_thing");
        assert_eq!(candidate_of("  mc/mtl_thing  "), "mc/mtl_thing");
        assert_eq!(candidate_of(""), "");
    }

    /// A name that happens to contain a comma but no leading hash is not truncated at it.
    #[test]
    fn a_comma_in_a_name_is_not_mistaken_for_a_key() {
        assert_eq!(candidate_of("not_hex,thing"), "not_hex,thing");
    }

    /// The generator has to land where `submit` looks for it, which is `contrib/` inside the
    /// run's own folder. Getting this path wrong loses the script silently, which is exactly how
    /// seven of them came to exist nowhere.
    #[test]
    fn a_named_generator_lands_where_submit_looks() {
        let dir = std::env::temp_dir().join(format!("carry_{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();

        let script = dir.join("mine.py");
        std::fs::write(&script, b"print('candidates')
").unwrap();

        let run = dir.join("run_20260819-000000_list");
        std::fs::create_dir_all(&run).unwrap();

        carry_along(&run, &script).unwrap();

        let landed = run.join("contrib").join("mine.py");
        assert!(landed.is_file(), "the generator should be at {}", landed.display());
        assert_eq!(std::fs::read(&landed).unwrap(), b"print('candidates')
");

        let _ = std::fs::remove_dir_all(&dir);
    }

    /// A file written on Windows carries a trailing carriage return, which hashes into the name
    /// and matches nothing. Trimming it is the difference between a run and a wasted run.
    #[test]
    fn a_windows_line_ending_does_not_reach_the_hash() {
        assert_eq!(candidate_of("mc/mtl_thing\r"), "mc/mtl_thing");
        assert_eq!(candidate_of("1a2b,mc/mtl_thing\r"), "mc/mtl_thing");
    }
}

/// Flags that are followed by a value, which is therefore not a candidate file.
///
/// `--game` was missing, and the cost was total: `confirm_list - --game BLKOPS04` took `BLKOPS04`
/// for a filename, confirmed the whole run happily, and *then* exited 1 trying to open it --
/// throwing away every name it had just found. Any contributed method aimed at one game hit this.
const TAKES_A_VALUE: &[&str] = &["--label", "--describe", "--script", "--game"];

/// Everything that is not a flag and not the value belonging to one.
///
/// Positional, so that a file which happens to be named the same as the label is still read --
/// comparing against the label's text would silently drop it, and a candidate file not read is a
/// run that reports success having tested nothing.
fn sources_from(arguments: &[String]) -> Vec<String> {
    let mut sources: Vec<String> = Vec::new();
    let mut skip_next = false;

    for argument in arguments {
        if skip_next {
            skip_next = false;
            continue;
        }

        if argument.starts_with("--") {
            skip_next = TAKES_A_VALUE.contains(&argument.as_str());
            continue;
        }

        sources.push(argument.clone());
    }

    sources
}
