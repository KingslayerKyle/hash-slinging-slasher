//! Scratch probe: can Cold War techset names be reached as `<base>#<8 hex>`?
//!
//! Black Ops III ships its techsetdefs unhashed, and a techset's runtime name is the def name
//! under a material-class directory with a 32-bit tag appended: `mc/lit_weapon_camo#e6142445`.
//! The tag is derived from the compiled techset, so it cannot be predicted from the name -- but
//! unlike a mesh entry's 26-character tail, 32 bits is small enough to sweep whole. If Cold War
//! kept the convention, every BO3 base name can be proved or ruled out exactly, tag and all.
//!
//! Reads a list of candidate base names (already carrying any directory prefix), and for each
//! one hashes all 4,294,967,296 possible tags against the unnamed techset ids. The per-digit
//! hash states are reused down the eight positions, so a full sweep costs about 4.6 billion
//! multiplies per base rather than 39 billion.

use std::collections::HashMap;
use std::path::Path;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;
use std::time::Instant;

use slasher::loader::{loaded_assets, unnamed_in};
use slasher::fingerprint::{Fingerprint, Sketch};
use slasher::{config, expected_by_chance, feed, paths, pool_index, pool_label, read_list, readiness, recon, table_keys, Filter, ID_MASK, Results, RunNote};

const HEX: [u8; 16] = *b"0123456789abcdef";

#[inline(always)]
fn step(hash: u64, byte: u8) -> u64 {
    feed(hash, &[byte])
}

/// Every tag under one base name, against the filter. Returns `(id, full name)` hits.
fn sweep(base: &str, filter: &Filter, wanted: &HashMap<u64, usize>) -> Vec<(u64, String)> {
    let mut hits = Vec::new();
    let seed = step(slasher::games::hash(&slasher::config::game(), "techset", base, true), b'#');

    for a in HEX {
        let s1 = step(seed, a);
        for b in HEX {
            let s2 = step(s1, b);
            for c in HEX {
                let s3 = step(s2, c);
                for d in HEX {
                    let s4 = step(s3, d);
                    for e in HEX {
                        let s5 = step(s4, e);
                        for f in HEX {
                            let s6 = step(s5, f);
                            for g in HEX {
                                let s7 = step(s6, g);
                                for h in HEX {
                                    let id = step(s7, h) & ID_MASK;
                                    if filter.may_hold(id) && wanted.contains_key(&id) {
                                        let tag: String =
                                            [a, b, c, d, e, f, g, h].iter().map(|&x| x as char).collect();
                                        hits.push((id, format!("{base}#{tag}")));
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    hits
}

fn main() {
    readiness::require();

    let began = Instant::now();

    // The streaming property the sweep depends on, checked rather than trusted.
    assert_eq!(feed(slasher::games::hash(&slasher::config::game(), "techset", "mc/a", true), b"bc#0"), slasher::games::hash(&slasher::config::game(), "techset", "mc/abc#0", true));

    let list = std::env::args().nth(1).expect("a file of candidate base names");
    let bases = read_list(Path::new(&list));
    println!("{} candidate base names from {list}", bases.len());

    let (assets, _) = match loaded_assets() {
        Ok(loaded) => loaded,
        Err(reason) => {
            eprintln!("{reason}");
            return;
        }
    };

    let known = table_keys();
    // Cold War calls the pool `techset`; Black Ops 4 calls it `technique_set`.
    let pool = pool_index("techset")
        .or_else(|| pool_index("technique_set"))
        .expect("the techset pool");
    let label = pool_label(pool);
    let wanted = unnamed_in(&assets, &known, pool);
    println!(
        "techset ids in the snapshot: {}, unnamed: {}",
        assets.iter().filter(|(_, index)| *index == pool).count(),
        wanted.len()
    );

    let candidates = bases.len() as u64 * (1u64 << 32);
    println!(
        "sweeping {candidates} candidates ({:.2}T); expected by chance: {:.6}",
        candidates as f64 / 1e12,
        expected_by_chance(candidates, wanted.len())
    );

    // Bare names first -- if Cold War dropped the tag, this is the whole answer, instantly.
    let mut results = Results::load(paths::findings());
    for base in &bases {
        let id = slasher::games::hash(&slasher::config::game(), "techset", base, true) & ID_MASK;
        if wanted.contains_key(&id) {
            println!("  HIT (no tag) {id:x},{base}");
            results.add(&label, id, base.clone());
        }
    }

    let fingerprint = Fingerprint::of("techset_probe")
        .with("game", &config::game())
        .with_list("bases", &bases)
        .finish();
    println!("fingerprint: {fingerprint}");
    recon::warn_if_swept(&fingerprint);

    let filter = Filter::sized(wanted.keys(), wanted.len());
    let next = AtomicUsize::new(0);
    let found: Mutex<Vec<(u64, String)>> = Mutex::new(Vec::new());
    let done = AtomicUsize::new(0);

    std::thread::scope(|scope| {
        for _ in 0..std::thread::available_parallelism().map(|n| n.get()).unwrap_or(8) {
            scope.spawn(|| loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(base) = bases.get(index) else { break };

                let hits = sweep(base, &filter, &wanted);
                if !hits.is_empty() {
                    let mut all = found.lock().unwrap();
                    for (id, name) in &hits {
                        println!("  HIT {id:x},{name}");
                    }
                    all.extend(hits);
                }

                let so_far = done.fetch_add(1, Ordering::Relaxed) + 1;
                if so_far % 100 == 0 {
                    let pace = so_far as f64 / began.elapsed().as_secs_f64();
                    println!(
                        "  {so_far}/{} bases swept, {:.1}/s, {:.0}s left",
                        bases.len(),
                        pace,
                        (bases.len() - so_far) as f64 / pace
                    );
                }
            });
        }
    });

    let found = found.into_inner().unwrap();
    println!(
        "\n{} names found in {}",
        found.len(),
        slasher::human_duration(began.elapsed())
    );

    if !found.is_empty() {
        for (id, name) in &found {
            results.add(&label, *id, name.clone());
        }
    }

    results.write(paths::findings()).expect("the results");
    match results.write_run(paths::findings(), "techsets") {
        Ok(Some(folder)) => {
            println!("this run's own names: {}", folder.display());
            let _ = Results::note_run(
                &folder,
                &RunNote::new(
                    "BO3 techset tag sweep (techset_probe)",
                    "every Black Ops III techsetdef base name given every possible 32-bit tag -- \
                     the tag space is small enough to sweep whole, so each base is proved or \
                     ruled out exactly",
                    began.elapsed(),
                )
                .measured("game", config::game())
                // The bases it swept tags against -- the only list that decides what this
                // probe can reach, so it is what `scripts/overlap.py` compares.
                .measured("sketch stems", Sketch::of(&bases))
                .fingerprint(&fingerprint),
            );
        }
        Ok(None) => println!("this run found nothing new"),
        Err(error) => eprintln!("the run folder could not be written: {error}"),
    }
}
