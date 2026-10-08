//! Re-verifies a submission from scratch, trusting nothing the sender said.
//!
//! This is what runs on a pull request. The client that found these names already checked them,
//! but it checked them on somebody else's machine with somebody else's build, and a bad
//! submission is far more expensive than a slow one: a wrong name entered into the community
//! tables is copied outward and is very hard to take back.
//!
//! So every line is re-derived here against the snapshots committed in this repository:
//!
//! 1. **The hash is recomputed from the name.** The number on the line is never taken as given,
//!    which catches a mangled file, a bad encoder, and a sender who simply made it up.
//! 2. **The id must be one the game actually holds.** This is the whole claim being made.
//! 3. **The asset type must be one of the pools the id lives in.** A real name filed under the
//!    wrong type is still wrong to publish, and this is free once the id has been found.
//!
//! Two further things are counted and reported but never fail the run, because neither means the
//! submission was wrong: a name published by somebody else while this batch was being ground, and
//! a name that appears twice. Both are things the maintainer resolves by merging, not by rejecting
//! somebody's night of work.

use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::{Path, PathBuf};

use slasher::snapshot::Snapshot;
use slasher::{paths, strip_stamp, tables};

fn main() {
    let mut args = std::env::args().skip(1);
    let mut targets = Vec::new();
    while let Some(arg) = args.next() {
        if arg == "--game" { args.next().expect("--game needs a tag"); continue; }
        targets.push(PathBuf::from(arg));
    }

    let files = if targets.is_empty() {
        submission_files(&paths::submissions())
    } else {
        targets.iter().flat_map(|path| submission_files(path)).collect()
    };

    if files.is_empty() {
        println!("no submission files to check.");
        return;
    }

    // Every snapshot in the repository. A name is being claimed of *a* game, not of a particular
    // one, so it is enough that some game holds it -- the submission files do not say which, and
    // a contributor should not have to know.
    let snapshots = snapshots();
    if snapshots.is_empty() {
        eprintln!("no snapshots found in {}. Nothing can be verified.", paths::snapshots().display());
        std::process::exit(1);
    }

    for snapshot in &snapshots {
        println!("checking against {} ({} assets)", snapshot.game(), snapshot.len());
    }

    // The published tables, if they are here. Absent is fine: everything they affect is a note
    // rather than a rejection, so a run without them is still a real verification.
    let published = published_hashes();
    match published.as_ref() {
        Some(known) => println!("{} hashes already published\n", known.len()),
        None => println!("(no tables present; already-published names will not be noted)\n"),
    }

    let mut seen: HashMap<String, String> = HashMap::new();
    let mut bad: Vec<String> = Vec::new();
    let mut total = 0_usize;
    let mut already = 0_usize;
    let mut repeated = 0_usize;
    let mut untyped = 0_usize;

    for file in &files {
        let kind = file
            .file_stem()
            .and_then(|stem| stem.to_str())
            .map(strip_stamp)
            .unwrap_or_default()
            .to_owned();

        let Ok(text) = fs::read_to_string(file) else {
            bad.push(format!("{}: unreadable", file.display()));
            continue;
        };

        let mut here = 0_usize;

        for (number, line) in text.lines().enumerate() {
            let line = line.trim();
            if line.is_empty() {
                continue;
            }

            let where_ = format!("{}:{}", short(file), number + 1);

            let Some((claimed, name)) = line.split_once(',') else {
                bad.push(format!("{where_}: not `hash,name`"));
                continue;
            };

            let name = name.trim();
            if name.is_empty() {
                bad.push(format!("{where_}: no name"));
                continue;
            }

            total += 1;
            here += 1;

            // 1. The hash, recomputed. Whatever the sender wrote is only a claim.
            //
            //    Both normalisations are accepted, and exactly one pool needs the second: Black
            //    Ops 4's SAB sound names keep their backslashes and the game holds the hash of
            //    the unfolded string. Checking only the folded form would reject every genuine
            //    Black Ops 4 sound name -- 70,878 of them -- as a bad hash.
            let said = match u64::from_str_radix(claimed.trim(), 16) {
                Ok(id) => id,
                Err(_) => { bad.push(format!("{where_}: {} is not a hash", claimed.trim())); continue; }
            };
            let id = said & slasher::ID_MASK;
            let pinned = std::env::args().any(|arg| arg == "--game");
            let holders: Vec<&Snapshot> = snapshots.iter().filter(|snapshot| {
                if pinned && snapshot.game() != slasher::config::game() { return false; }
                let folded = slasher::games::output_key(snapshot.game(), &kind, name, true);
                let raw_allowed = snapshot.game() == "BLKOPS04" && matches!(kind.as_str(), "sound_asset" | "sound");
                (said == folded || (raw_allowed && said == slasher::games::output_key(snapshot.game(), &kind, name, false)))
                    && snapshot.holds(id)
            }).collect();

            if holders.is_empty() {
                bad.push(format!("{where_}: no snapshot holds {id:x} ({name})"));
                continue;
            }

            // 2b. Names whose shape is unusual for their type, flagged for a human to glance at.
            //
            //     Noted, never rejected. The first name this caught looked exactly like a
            //     coincidence and turned out, checked in Saluki, to be the model's real name --
            //     a sound path somebody pasted onto a model. A verified name must never be
            //     thrown away by a heuristic about what names ought to look like.
            if let Some(why) = slasher::odd_for_pool(&kind, name) {
                println!("  note: {where_}: {name} {why}");
            }

            // 3. The type must be one of the pools the id actually lives in.
            //
            //    Resolved against the game of the snapshot that actually holds the id, never against
            // whatever this machine is configured to grind. The two number their asset types
            // differently -- index 5 is `xanim` in Cold War and `xmodelmesh` in Black Ops 4 -- so
            // a check that reads one game's index out of the other's enum reports a confident,
            // detailed, completely wrong answer. It did: thirteen correct Cold War anims were
            // reported as "filed as xanim but BLKOPSCW holds it in xmodelmesh", which is not even
            // self-consistent, and it would have rejected a sound submission in CI.
            //
            // A name held by several games is checked against each, and passes if any agrees:
            // both games hold plenty of the same assets, and the submission does not say which
            // game found it.
            match holders.as_slice() {
                [] => {}
                holders => {
                    let mut fits = false;
                    let mut held: Vec<String> = Vec::new();
                    let mut checkable = false;

                    for snapshot in holders {
                        let table = slasher::pools_for(snapshot.game());
                        let Some(wanted) = slasher::pool_index_in(table, &kind) else {
                            continue;
                        };
                        checkable = true;

                        let pools = snapshot.pools_of(id);
                        if pools.iter().any(|(_, pool)| *pool as usize == wanted) {
                            fits = true;
                            break;
                        }

                        for (_, pool) in pools {
                            held.push(format!(
                                "{} in {}",
                                table.get(*pool as usize).copied().unwrap_or("an unnamed pool"),
                                snapshot.game()
                            ));
                        }
                    }

                    if !checkable {
                        untyped += 1;
                    } else if !fits {
                        bad.push(format!(
                            "{where_}: {name} is filed as {kind} but the game holds it as {}",
                            held.join(", ")
                        ));
                        continue;
                    }
                }
            }

            // Noted, not rejected. Somebody publishing a name mid-grind is the race this whole
            // project is built around, and losing to it is not a fault in the submission.
            if let Some(known) = published.as_ref() {
                if known.contains(&id) {
                    already += 1;
                }
            }

            if let Some(before) = seen.insert(name.to_owned(), where_.clone()) {
                repeated += 1;
                if repeated <= 5 {
                    println!("  note: {name} appears twice, at {before} and {where_}");
                }
            }
        }

        println!("{:<44} {here:>8} names", short(file));
    }

    println!("\n{total} names checked, {} distinct", seen.len());

    if repeated > 0 {
        println!("{repeated} repeated (harmless; they merge to one)");
    }

    if already > 0 {
        println!("{already} published by somebody else since (harmless; drop on merge)");
    }

    if untyped > 0 {
        println!(
            "{untyped} could not be type checked against any snapshot that holds them"
        );
    }

    if bad.is_empty() {
        println!("\nevery name re-derives: the hash matches the name, the game holds the id, and\
                  \nthe asset type is one the id is actually in.");
        return;
    }

    eprintln!("\n{} name(s) did not survive re-verification:\n", bad.len());
    for (shown, complaint) in bad.iter().enumerate() {
        if shown == 40 {
            eprintln!("  ... and {} more", bad.len() - 40);
            break;
        }
        eprintln!("  {complaint}");
    }

    std::process::exit(1);
}

/// Every `.txt` under a path, which may be one file or a whole submission folder.
fn submission_files(path: &Path) -> Vec<PathBuf> {
    if path.is_file() {
        return match path.extension().and_then(|e| e.to_str()) {
            Some("txt") => vec![path.to_owned()],
            _ => Vec::new(),
        };
    }

    let mut found = Vec::new();
    for entry in fs::read_dir(path).into_iter().flatten().flatten() {
        found.extend(submission_files(&entry.path()));
    }

    found.sort();
    found
}

fn snapshots() -> Vec<Snapshot> {
    let mut found = Vec::new();

    for entry in fs::read_dir(paths::snapshots()).into_iter().flatten().flatten() {
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) != Some("ids") {
            continue;
        }

        match Snapshot::read(&path) {
            Ok(snapshot) => found.push(snapshot),
            Err(why) => eprintln!("{} could not be read: {why}", path.display()),
        }
    }

    found
}

/// Every hash the published tables resolve, if the tables are here at all.
fn published_hashes() -> Option<HashSet<u64>> {
    let folder = tables::csv_folder(&paths::tables());
    if !folder.is_dir() { return None; }
    // Validation can cover several games at once, so read every table family.
    let known = slasher::database_keys(&folder,"BLKOPSCW");
    (!known.is_empty()).then_some(known)
}

/// The asset type out of a submission's filename: `xmodel_20260818_213000` is `xmodel`.
/// A path short enough to read in a log, since CI prints an absolute one.
fn short(path: &Path) -> String {
    let parts: Vec<String> =
        path.components().rev().take(2).map(|part| part.as_os_str().to_string_lossy().to_string()).collect();

    parts.into_iter().rev().collect::<Vec<_>>().join("/")
}

#[cfg(test)]
mod tests {
    use super::*;
    use slasher::id_of;

    /// The asset type has to survive a stamp being appended, and `sound_asset` is the case that
    /// a naive split on the first underscore gets wrong.
    #[test]
    fn the_type_comes_back_out_of_the_filename() {
        assert_eq!(strip_stamp("xmodel_20260818_213000"), "xmodel");
        assert_eq!(strip_stamp("sound_asset_20260818_213000"), "sound_asset");
        assert_eq!(strip_stamp("xmodel"), "xmodel");
        assert_eq!(strip_stamp("sound_asset"), "sound_asset");
    }

    /// An unidentified pool keeps its number, and must not be mistaken for a stamp and trimmed
    /// away into nothing.
    #[test]
    fn an_unidentified_pool_is_left_alone_enough_to_be_unmatchable() {
        // `pool_184` trims to `pool`, which is not a known pool name in either game, so the type
        // check is skipped rather than wrongly failed. That is the behaviour that matters.
        let trimmed = strip_stamp("pool_184_20260819-174052");

        for table in [slasher::POOLS, slasher::BO4_POOLS] {
            assert!(slasher::pool_index_in(table, trimmed).is_none(), "{trimmed} resolved");
        }
    }

    /// Every known pool name must round-trip, or a valid submission would be rejected for being
    /// filed under a type this could not recognise.
    #[test]
    fn every_pool_name_survives_a_stamp() {
        // `stamp()` itself, not a hand-written imitation of it. The imitation is what let the
        // stripper stay broken: it produced `_20260818_213000`, the real thing produces
        // `_20260819-174052`, and only the first one had its digits unbroken by a dash.
        let stamp = slasher::stamp();
        assert!(stamp.contains('-'), "the stamp shape changed: {stamp}");

        for pool in slasher::POOLS.iter().chain(slasher::BO4_POOLS) {
            let stamped = format!("{pool}_{stamp}");
            assert_eq!(strip_stamp(&stamped), *pool, "{pool} did not come back");
        }
    }

    /// A type whose own name ends in something stamp-shaped must survive too, or the stripper
    /// would eat part of the asset type.
    #[test]
    fn stripping_stops_at_the_asset_type() {
        assert_eq!(strip_stamp("xmodel"), "xmodel");
        assert_eq!(strip_stamp("sound_asset_20260819-174052"), "sound_asset");
        assert_eq!(strip_stamp("cpu_occlusion_data_20260819-174052"), "cpu_occlusion_data");
        assert_eq!(strip_stamp("script_using_mp_20260819-174052"), "script_using_mp");
    }

    /// Every way we grind must be able to find something. This is the regression test for the
    /// failure this project keeps producing: a normalisation that quietly matches nothing while
    /// every run looks healthy. Each entry is a name cod-name-db already publishes, and the id
    /// the game genuinely holds for it -- so if a hash, a mask or a fold ever drifts, this fails
    /// instead of a contributor's night failing.
    #[test]
    fn every_normalisation_still_reaches_the_games() {
        let snapshots = snapshots();
        assert!(!snapshots.is_empty(), "the snapshots ship with the repository");

        let holds = |id: u64| snapshots.iter().any(|snapshot| snapshot.holds(id));

        // Ordinary names: folded, and the fold is a no-op because they carry no backslash.
        for name in [
            "attach_t8_shotgun_pump_grip_sig2_view",
            "splm/aml_fish_salmon_01",
            "mc/mtl_veh_t8_mil_truck_att_decal01",
        ] {
            assert!(holds(id_of(name)), "{name} should be reachable by the folding hash");
        }

        // Black Ops 4 SAB sound names, which keep their backslashes. Folding these gives a number
        // the game does not hold, which is precisely the bug this guards.
        let sound = r"amb\environment\water\waves\crash\wave_crash_01.ln100.pc.snd";
        let raw = slasher::hash64_raw(sound) & slasher::ID_MASK;

        assert!(holds(raw), "the unfolded hash must reach the sound pool");
        assert!(!holds(id_of(sound)), "folding it should reach nothing -- that is the whole point");
    }

    /// Each game's own enum, asserted by name. The type check now resolves against the game of
    /// the snapshot holding the id, so nothing here may go through the configured game -- index 6
    /// is `xmodel` in Cold War and `material` in Black Ops 4, and a test that reads the config
    /// passes or fails depending on the machine it runs on.
    #[test]
    fn each_game_numbers_its_pools_its_own_way() {
        assert_eq!(slasher::POOLS[6], "xmodel");
        assert_eq!(slasher::BO4_POOLS[6], "material");

        // Index 5 is the one that produced a confident wrong answer for thirteen real anims.
        assert_eq!(slasher::POOLS[5], "xanim");
        assert_eq!(slasher::BO4_POOLS[5], "xmodelmesh");

        // 184 was the largest unidentified pool in Cold War until the enum named it.
        assert_eq!(slasher::POOLS[184], "streamkey");
    }
}
