//! Recovers sound asset names, which are a path with a fixed set of tails on the end.
//!
//! A sound asset is named
//! `vox/scripted/mpl/ngs2/vox_ngs2_ss_gunship_40_kill_1_01.rn75.pc.en.snd`. Everything from the
//! first dot is a tail out of a closed set: a two letter marker, `75`, the platform, the
//! language, `snd`. There are a couple of hundred such tails across every sound table, and the
//! same recording exists under most of them.
//!
//! The general search cannot reach these at all: it cuts its pieces at underscores and slashes
//! and treats a dot as the end of a name, so it can never put a dotted tail back on. That is why
//! tens of thousands of the game's sound assets are unnamed while the tables hold most of the
//! recordings under some other tail.
//!
//! The tails are measured, never guessed -- every distinct one any sound table holds, however
//! rarely, since the whole list is small enough to be free. The stems are every sound name with
//! its tail taken off, from the tables and from what was scraped out of the builds.

use std::collections::HashSet;

use slasher::loader::{loaded_assets, unnamed_in};
use slasher::search::{candidate_space, Meet};
use slasher::fingerprint::{Fingerprint, Sketch};
use slasher::{futility, all_table_names, config, folder_names, paths, pool_index, pool_label, readiness, recon, table_keys, tables_look_complete, Results, RunNote};

/// What marks the end of a sound name's own part and the start of the tail.
const TAIL: char = '.';

/// The pools a sound name can land in.
///
/// Four pools rather than one, and a submission saying "searched 4 pools: sound, sound_asset,
/// sound_bank, sound_duck" has been read as scope drift. It is not, and the numbers are the whole
/// argument: in Cold War `sound_asset` holds 97,217 ids while `sound_bank` holds 107 and
/// `sound_duck` 191, and `sound` is not a filled pool at all. Adding the other three widens the
/// wanted set by **0.3%**, which is free -- they are peeled in the same batch as the rest -- and
/// they are real sound names when they land.
///
/// The rule this illustrates is worth keeping: widening is only cheap when the pools being added
/// are small. Widening into `streamkey` would add 420,229 ids, quadrupling the wanted set and the
/// coincidence rate with it. `python scripts/coverage.py` is how to tell the two cases apart, and
/// it should be run before adding anything here.
const POOLS_SEARCHED: &[&str] = &["sound_asset", "sound", "sound_bank", "sound_duck"];

/// Every tail any sound name carries, as everything from its first dot.
///
/// No threshold. The list runs to a few hundred, and a rare tail is exactly the one a published
/// table is least likely to already name.
fn tails(names: &[String]) -> Vec<String> {
    let mut seen: HashSet<String> = HashSet::new();

    for name in names {
        if let Some(at) = name.find(TAIL) {
            let tail = name[at..].to_lowercase();
            if tail.len() < 40 {
                seen.insert(tail);
            }
        }
    }

    seen.into_iter().collect()
}

/// Every sound name with its tail taken off, plus the pieces of one that a sibling might share.
///
/// A sound sits in a directory tree rather than under a flat prefix, so the pieces worth keeping
/// are the whole path and the path with its leading directories peeled away -- the same file
/// often appears under `vox/scripted/operators/` and under `vox/scripted/`.
fn stems(names: &[String]) -> Vec<String> {
    let mut seen: HashSet<String> = HashSet::new();

    for name in names {
        let name = name.to_lowercase();
        let body = match name.find(TAIL) {
            Some(at) => &name[..at],
            None => &name[..],
        };

        if body.len() < 4 {
            continue;
        }

        seen.insert(body.to_owned());

        for (index, byte) in body.bytes().enumerate() {
            if byte == b'/' && index + 1 < body.len() {
                seen.insert(body[index + 1..].to_owned());
            }
        }
    }

    seen.into_iter().collect()
}

fn main() {
    readiness::require();
    futility::require();

    let began = std::time::Instant::now();
    let searched: Vec<usize> = POOLS_SEARCHED.iter().filter_map(|kind| pool_index(kind)).collect();

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

    let mut wanted = std::collections::HashMap::new();
    for pool in &searched {
        wanted.extend(unnamed_in(&assets, &known, *pool));
    }
    println!(
        "unnamed in {POOLS_SEARCHED:?}: {} of {} loaded",
        wanted.len(),
        assets.iter().filter(|(_, pool)| searched.contains(pool)).count()
    );
    drop(known);

    // Every name any table holds, which is where the tails and most of the stems come from, and
    // everything scraped out of a build, which is where the rest come from.
    // `paths::harvest()` once, not twice. It used to be listed under two labels, "the alpha" and
    // "the retail build", but it is one path -- so every string in it was read and cut into tails
    // and stems a second time for nothing.
    let mut vocabulary = all_table_names();
    for folder in [paths::harvest(), paths::borrowed()].into_iter().flatten() {
        vocabulary.extend(folder_names(folder));
    }
    vocabulary.extend(strings);

    let endings = tails(&vocabulary);
    let pieces = stems(&vocabulary);
    println!("tails measured: {}, stems: {}", endings.len(), pieces.len());

    let fingerprint = Fingerprint::of("confirm_sounds")
        .with("game", &config::game())
        .with_list("tails", &endings)
        .finish();
    println!("fingerprint: {fingerprint}");
    recon::warn_if_swept(&fingerprint);

    let mut results = Results::load(paths::findings());

    // A sound name is a path in its own right and carries no beginning, so the only opening is
    // no opening at all.
    let search = Meet::new(&[], &endings);
    for (id, name) in search.run(&pieces, &wanted) {
        results.add(&pool_label(wanted[&id]), id, name);
    }

    println!("this run added {}", results.added());

    // Recorded whatever the outcome, including nothing: a run that finds nothing is a
    // real result, and three of them in a row is a loop. See `futility`.
    futility::record(results.added(), None);

    results.write(paths::findings()).expect("the results");

    match results.write_run(paths::findings(), "sounds") {
        Ok(Some(folder)) => {
            println!("this run's own names: {}", folder.display());
            let _ = Results::note_run(
                &folder,
                &RunNote::new(
                    "sound dotted tails (confirm_sounds)",
                    "confirmed sound stems recombined with every observed dotted tail, which the \
                     general search cannot reach because it treats a dot as the end of a name",
                    began.elapsed(),
                )
                .measured("game", config::game())
                .measured("tails", endings.len())
                .measured("stems", pieces.len())
                .measured("ids hunted", wanted.len())
                // Spelled as `confirm_list` spells it, so `methods_report.py` can rank this
                // against every other method. Without it a run is ranked by how long it took.
                .measured(
                    "candidates tested",
                    candidate_space(0, endings.len(), pieces.len(), true),
                )
                .measured("new", results.added())
                // See `confirm_plan`. Sound runs carried no sketch, so the overlap ledger
                // could not compare two contributors grinding the same sound vocabulary.
                .measured("sketch stems", Sketch::of(&pieces))
                .measured("sketch endings", Sketch::of(&endings))
                .fingerprint(&fingerprint),
            );
        }
        Ok(None) => println!("this run found nothing new"),
        Err(error) => eprintln!("the run folder could not be written: {error}"),
    }
}
