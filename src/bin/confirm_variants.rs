//! Finds the other members of a numbered or lettered family.
//!
//! Assets come in families that count: `p9_rus_crate_01_wood_a`, `_02`, `_03`; `..._lod0`
//! through `_lod6`; a part that is `_a` in one material and `_b` in the next. A published table
//! holds some members of a family and not others, and the ones it holds say exactly what the
//! ones it does not are called.
//!
//! Every other search here builds a name as a beginning, a stem and an ending, so it can only
//! ever vary what is at the two ends. A family number is usually in the middle, and no amount of
//! cutting at underscores reaches it: cutting `p9_rus_crate_01_wood_a` gives pieces that either
//! stop before the number or start after it, and neither can put a different one back.
//!
//! So this varies a name in place. Each run of digits is counted through, each single letter
//! token is stepped through the alphabet, and the width of what was there is kept, because
//! `_01` and `_1` are different names.
//!
//! `swaps` varies a whole word instead of a number: each token of a name is replaced in turn by
//! every common token the game uses elsewhere, which is what reaches
//! `vm_smg_season6_t9_sprint_in` from `vm_ar_season6_t9_sprint_in`. It is a much wider search
//! than the numbers, so it is asked for separately.
//!
//! Nothing is invented either way: every variant is a name the game already uses with one field
//! changed to another the game also uses.

use std::collections::{HashMap, HashSet};
use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
use std::time::{Duration, Instant};

use slasher::loader::{loaded_assets, wanted_for_search};
use slasher::fingerprint::{Fingerprint, Sketch};
use slasher::{futility, config, expected_by_chance, hash64, paths, pool_label, readiness, recon, table_keys, tables_look_complete, Filter, ID_MASK, Results, RunNote};

/// How far a family is counted. Most stop in the low tens; a few run to the hundreds.
const HIGHEST: u32 = 256;

/// How far two fields are counted when both are varied at once. The pair multiplies, so it is
/// held to the range nearly every family stays inside.
const HIGHEST_PAIR: u32 = 32;

/// How many of the tokens the game uses are worth substituting in. The list is ranked by use,
/// and the tail of it is single occurrences that multiply the work without widening the reach.
const COMMON_TOKENS: usize = 1024;

/// Mesh names end in a hash of the mesh and cannot be reached by varying anything.
const UNREACHABLE: &[&str] = &["xmodelmesh"];

const REPORT_EVERY: Duration = Duration::from_secs(30);

/// Every way one field of a name can be varied, as the name with that field replaced.
///
/// The callback is handed each variant in a buffer that is reused, so a run of hundreds of
/// millions of them costs no allocation at all.
fn variants(name: &str, mut visit: impl FnMut(&str)) {
    let bytes = name.as_bytes();
    let mut buffer = String::with_capacity(name.len() + 4);

    let mut at = 0;
    while at < bytes.len() {
        if bytes[at].is_ascii_digit() {
            let start = at;
            while at < bytes.len() && bytes[at].is_ascii_digit() {
                at += 1;
            }

            // A long run of digits is an identifier rather than a family number, and counting
            // through one produces nothing but noise.
            let width = at - start;
            if width <= 3 {
                for number in 0..=HIGHEST {
                    buffer.clear();
                    buffer.push_str(&name[..start]);
                    widened(&mut buffer, number, width);
                    buffer.push_str(&name[at..]);
                    visit(&buffer);
                }
            }

            continue;
        }

        // A single letter standing as its own token: `_a_`, `_b_`, and the same at either end.
        let alone = bytes[at].is_ascii_lowercase()
            && (at == 0 || bytes[at - 1] == b'_')
            && (at + 1 == bytes.len() || bytes[at + 1] == b'_');

        if alone {
            for letter in b'a'..=b'z' {
                buffer.clear();
                buffer.push_str(&name[..at]);
                buffer.push(letter as char);
                buffer.push_str(&name[at + 1..]);
                visit(&buffer);
            }
        }

        at += 1;
    }

    // Two numbers at once. A family often counts on two axes -- a set number and a piece number,
    // a floor and a room -- and changing either alone lands outside it.
    let runs = digit_runs(bytes);
    if runs.len() >= 2 {
        for first in 0..runs.len() - 1 {
            for second in first + 1..runs.len() {
                let (a, b) = (runs[first], runs[second]);
                if a.1 - a.0 > 2 || b.1 - b.0 > 2 {
                    continue;
                }

                for left in 0..=HIGHEST_PAIR {
                    for right in 0..=HIGHEST_PAIR {
                        buffer.clear();
                        buffer.push_str(&name[..a.0]);
                        widened(&mut buffer, left, a.1 - a.0);
                        buffer.push_str(&name[a.1..b.0]);
                        widened(&mut buffer, right, b.1 - b.0);
                        buffer.push_str(&name[b.1..]);
                        visit(&buffer);
                    }
                }
            }
        }
    }
}

/// Where each run of digits in a name starts and ends.
fn digit_runs(bytes: &[u8]) -> Vec<(usize, usize)> {
    let mut runs = Vec::new();
    let mut at = 0;

    while at < bytes.len() {
        if bytes[at].is_ascii_digit() {
            let start = at;
            while at < bytes.len() && bytes[at].is_ascii_digit() {
                at += 1;
            }
            runs.push((start, at));
        } else {
            at += 1;
        }
    }

    runs
}

/// Writes a number at the width the one it replaces was written to, since `_01` and `_1` are
/// different names and neither is worth guessing between.
fn widened(buffer: &mut String, number: u32, width: usize) {
    match width {
        1 => buffer.push_str(&number.to_string()),
        2 => buffer.push_str(&format!("{number:02}")),
        _ => buffer.push_str(&format!("{number:03}")),
    }
}

/// The tokens the game uses most, as the whole segments its names are built from.
fn common_tokens(names: &[String], most: usize) -> Vec<String> {
    let mut counted: HashMap<&str, usize> = HashMap::new();

    for name in names {
        for token in name.split(|c: char| c == '_' || c == '/') {
            if (2..=20).contains(&token.len()) {
                *counted.entry(token).or_default() += 1;
            }
        }
    }

    let mut ranked: Vec<(&str, usize)> = counted.into_iter().collect();
    ranked.sort_unstable_by(|a, b| b.1.cmp(&a.1));
    ranked.truncate(most);

    ranked.into_iter().map(|(token, _)| token.to_lowercase()).collect()
}

/// Every name that is this one with a single token replaced by another the game uses.
fn swaps(name: &str, tokens: &[String], mut visit: impl FnMut(&str)) {
    let bytes = name.as_bytes();
    let mut buffer = String::with_capacity(name.len() + 20);

    let mut start = 0;
    for at in 0..=bytes.len() {
        let boundary = at == bytes.len() || bytes[at] == b'_' || bytes[at] == b'/';
        if !boundary {
            continue;
        }

        if at > start {
            for token in tokens {
                buffer.clear();
                buffer.push_str(&name[..start]);
                buffer.push_str(token);
                buffer.push_str(&name[at..]);
                visit(&buffer);
            }
        }

        start = at + 1;
    }
}

fn main() {
    readiness::require();
    futility::require();

    let began = Instant::now();
    let (assets, strings) = match loaded_assets() {
        Ok(loaded) => loaded,
        Err(reason) => {
            eprintln!("{reason}");
            return;
        }
    };

    let known = table_keys();
    if !tables_look_complete(&known) {
        eprintln!("the tables read short. Check {}", paths::tables().display());
        return;
    }

    let wanted = wanted_for_search(&assets, &known, UNREACHABLE);
    println!("unnamed assets a variant could be: {}", wanted.len());
    drop(known);

    // Every name known to exist, from the tables that are this game and from what has been
    // confirmed. A confirmed name is the better seed of the two: it is a family member nobody
    // had, so its siblings are the ones nobody has either.
    // One load, one extend. This used to load `paths::findings()` a second time under the name
    // `from_materials` and append the identical list again, so "names to vary" counted every
    // confirmed name twice and was only right by accident of the dedupe below. The same mistake
    // has now been found and fixed in five places: here, `images_from_materials`, `confirm_cw`,
    // `confirm_sounds` and `confirm_localize` -- and in `derive_lists.py`, where it doubled the
    // measured corpus and halved every threshold that holds the confirmed takes in check.
    let mut results = Results::load(paths::findings());

    let mut seeds: Vec<String> = slasher::all_table_names();
    // `seed_names`, not `all_names`: a confirmed-but-unrepresentative name is kept and
    // submitted, but must not teach this pass what a name looks like. See `odd_for_pool`.
    seeds.extend(results.seed_names());
    seeds.extend(strings);

    let mut seen: HashSet<u64> = HashSet::new();
    seeds.retain(|name| !name.is_empty() && seen.insert(hash64(name)));
    drop(seen);
    println!("names to vary: {}", seeds.len());

    let arguments: Vec<String> = std::env::args().skip(1).collect();
    let swapping = arguments.iter().any(|value| value == "swaps");

    // How many tokens to substitute in can be given on the command line, since the cost is
    // linear in it and the right number is a question of how long there is rather than of
    // anything measurable.
    let most = arguments
        .iter()
        .find_map(|value| value.parse::<usize>().ok())
        .unwrap_or(COMMON_TOKENS);

    let tokens = if swapping {
        let tokens = common_tokens(&seeds, most);
        println!("substituting the {} most used tokens", tokens.len());
        tokens
    } else {
        Vec::new()
    };

    let fingerprint = Fingerprint::of(if swapping { "confirm_variants/swaps" } else { "confirm_variants/numbers" })
        .with("game", &config::game())
        // `most` rather than `tokens.len()`, and it has to be one of the two: it is the only
        // trace the command line leaves here, so without it `confirm_variants swaps` and
        // `confirm_variants swaps 4000` fingerprint identically and the wider of the two searches
        // is reported as already swept. A number typed at the command line is not a measurement
        // of this machine's disk -- everybody who types it gets the same one.
        // Zero when the run is not swapping, because `most` is read only in that mode: fed
        // unconditionally, `confirm_variants` and `confirm_variants 500` would run byte-identical
        // number searches under two fingerprints, and the second would not be recognised as the
        // repeat it is.
        .with_count("tokens", if swapping { most } else { 0 })
        .with_list("seeds", &seeds)
        .finish();
    println!("fingerprint: {fingerprint}");
    recon::warn_if_swept(&fingerprint);

    let policies = slasher::games::groups(&wanted);
    let policies = &policies;
    let filter = Filter::new(wanted.keys());

    let threads = std::thread::available_parallelism()
        .map(|count| count.get())
        .unwrap_or(8);
    let done = AtomicUsize::new(0);
    let tried = AtomicU64::new(0);
    let finished = std::sync::atomic::AtomicBool::new(false);
    let total = seeds.len();

    let mut collected: Vec<(u64, String)> = Vec::new();
    let started = Instant::now();

    std::thread::scope(|scope| {
        let reporter = scope.spawn(|| {
            let mut last = Instant::now();
            while !finished.load(Ordering::Relaxed) {
                std::thread::sleep(Duration::from_millis(250));
                if last.elapsed() < REPORT_EVERY {
                    continue;
                }
                last = Instant::now();

                let seen = done.load(Ordering::Relaxed);
                let share = seen as f64 / total as f64;
                let elapsed = started.elapsed().as_secs_f64();
                println!(
                    "  {:>5.1}%  {seen}/{total} names  {:.1}B variants  {:.0}s left",
                    share * 100.0,
                    tried.load(Ordering::Relaxed) as f64 / 1e9,
                    if share > 0.0 { elapsed / share - elapsed } else { 0.0 }
                );
            }
        });

        let size = total.div_ceil(threads).max(1);
        let mut workers = Vec::new();

        for chunk in seeds.chunks(size) {
            let filter = &filter;
            let done = &done;
            let tried = &tried;
            let tokens = &tokens;

            workers.push(scope.spawn(move || {
                let mut hits: Vec<(u64, String)> = Vec::new();
                let mut counted = 0_u64;

                for (index, name) in chunk.iter().enumerate() {
                    let lowered = name.to_lowercase();
                    let mut look = |variant: &str| {
                        counted += 1;
                        for (basis, targets) in policies {
                            let id = slasher::feed(*basis, variant.as_bytes()) & ID_MASK;
                            if filter.may_hold(id) && targets.contains_key(&id) {
                                hits.push((id, variant.to_owned()));
                            }
                        }
                    };

                    if swapping {
                        swaps(&lowered, &tokens, &mut look);
                    } else {
                        variants(&lowered, &mut look);
                    }

                    if index % 4096 == 0 {
                        done.fetch_add(4096, Ordering::Relaxed);
                        tried.fetch_add(counted, Ordering::Relaxed);
                        counted = 0;
                    }
                }

                tried.fetch_add(counted, Ordering::Relaxed);
                hits
            }));
        }

        for worker in workers {
            collected.extend(worker.join().expect("a worker"));
        }

        finished.store(true, Ordering::Relaxed);
        let _ = reporter.join();
    });

    let count = tried.load(Ordering::Relaxed);
    println!(
        "tried {count} variants in {:.0}s, {} matched",
        started.elapsed().as_secs_f64(),
        collected.len()
    );
    println!(
        "names expected to match by chance at this size: {:.3}",
        expected_by_chance(count, wanted.len())
    );

    for (id, name) in collected {
        results.add(&pool_label(wanted[&id]), id, name);
    }

    println!("this run added {}", results.added());

    // Recorded whatever the outcome, including nothing: a run that finds nothing is a
    // real result, and three of them in a row is a loop. See `futility`.
    futility::record(results.added());

    results.write(paths::findings()).expect("the results");

    match results.write_run(paths::findings(), if swapping { "swaps" } else { "variants" }) {
        Ok(Some(folder)) => {
            println!("this run's own names: {}", folder.display());
            let _ = Results::note_run(
                &folder,
                &RunNote::new(
                    if swapping { "family walking, whole words (swaps)" } else { "family walking, numbers in place (variants)" },
                    if swapping {
                        "each token of a name already known to be real replaced in turn by every \
                         common token the game uses elsewhere"
                    } else {
                        "each number or letter field of a name already known to be real counted \
                         through in place, keeping the width of what was there"
                    },
                    began.elapsed(),
                )
                .measured("game", config::game())
                .measured("ids hunted", wanted.len())
                // `count` is the number this run actually tried, and it has been computed
                // since the first version -- printed to the terminal and then dropped. Under
                // the label `confirm_list` uses, so the two can be ranked against each other.
                .measured("candidates tested", count)
                .measured("new", results.added())
                // The vocabulary this walk actually had. `seeds` are the names it varied,
                // `tokens` what it substituted in -- between them they decide everything it
                // could reach, which is what `scripts/overlap.py` compares.
                .measured("sketch stems", Sketch::of(&seeds))
                .measured("sketch endings", Sketch::of(&tokens))
                .fingerprint(&fingerprint),
            );
        }
        Ok(None) => println!("this run found nothing new"),
        Err(error) => eprintln!("the run folder could not be written: {error}"),
    }
}
