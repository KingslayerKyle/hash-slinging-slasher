//! What you have actually found, said in a way that is worth reading.
//!
//! The searches print accounting: rows, added, totals. That is what you need while tuning a rule
//! and it is not what you want at the end of a night. A name recovered here is a real thing that
//! nobody had -- it was lost, and now it is not -- and a column of numbers hides that completely.
//!
//! So this shows the names. Not all of them, which would be a wall; a spread across the types,
//! chosen to show the ones that look like something. Seeing `ges_command_acknowledge_dw` come out
//! of nothing is the part that makes someone want to run it again, and no total conveys it.
//!
//! Needs nothing but the findings folder: no game, no loader, no network.

use std::collections::BTreeMap;
use std::fs;
use std::path::{Path, PathBuf};

use slasher::paths;

/// How many names to show per type. Enough to see the shape of what was found, few enough that
/// the whole report still fits on a screen.
const SHOW: usize = 4;

/// How wide the bar for the biggest type is drawn.
const BAR: usize = 34;

fn main() {
    let findings = std::env::args().nth(1).map(PathBuf::from).unwrap_or_else(paths::findings);

    if !findings.exists() {
        println!("nothing found yet -- {} does not exist.", findings.display());
        println!("run a search first:  cargo run --release --bin confirm_cw");
        return;
    }

    // Every type, and every name filed under it. Run folders are read too but counted separately,
    // since they are subsets of the merged set rather than extra findings.
    let mut by_type: BTreeMap<String, Vec<String>> = BTreeMap::new();
    let mut runs: Vec<(String, usize)> = Vec::new();

    gather(&findings, &mut by_type, &mut runs, true);

    let total: usize = by_type.values().map(Vec::len).sum();

    if total == 0 {
        println!("no names in {} yet.", findings.display());
        return;
    }

    println!();
    println!("  ┌────────────────────────────────────────────────────────────┐");
    println!("  │  {:>10} asset names recovered that nobody had         │", thousands(total));
    println!("  └────────────────────────────────────────────────────────────┘");
    println!();

    // The types, largest first, with a bar so the shape is visible at a glance.
    let widest = by_type.values().map(Vec::len).max().unwrap_or(1);
    let mut ordered: Vec<(&String, &Vec<String>)> = by_type.iter().collect();
    ordered.sort_by(|a, b| b.1.len().cmp(&a.1.len()));

    for (kind, names) in &ordered {
        let filled = (names.len() * BAR).div_ceil(widest.max(1));
        println!(
            "  {:<22} {:>8}  {}",
            kind,
            thousands(names.len()),
            "█".repeat(filled.max(1))
        );
    }

    // The part that is actually satisfying: the names themselves.
    println!("\n  some of what you found\n  ──────────────────────");

    for (kind, names) in ordered.iter().take(8) {
        let mut sample: Vec<&String> = names.iter().collect();

        // The ones that look like something: longest names carry the most structure, and a name
        // with structure is recognisably a real thing rather than a string.
        sample.sort_by_key(|name| std::cmp::Reverse(name.len()));

        println!("\n  {kind}");
        for name in sample.iter().take(SHOW) {
            println!("    {name}");
        }
        if names.len() > SHOW {
            println!("    ... and {} more", thousands(names.len() - SHOW));
        }
    }

    if !runs.is_empty() {
        runs.sort();
        let sessions = runs.len();
        let best = runs.iter().max_by_key(|(_, count)| *count);

        println!("\n  {sessions} run(s) contributed to this.");
        if let Some((when, count)) = best {
            println!("  the best single run found {} names ({when}).", thousands(*count));
        }
        if let Some((when, count)) = runs.last() {
            println!("  the most recent found {} ({when}).", thousands(*count));
        }
    }

    println!("\n  nothing here is a guess. Every one was confirmed against the game itself.");
    println!();
}

/// Reads a findings folder: the merged files at the top, and the per-run folders under it.
///
/// The folder gets organised by hand -- types that matter moved into one folder, retired ones
/// into another -- so this walks whatever it finds rather than assuming a shape. A `superseded`
/// folder is skipped, being names deliberately retired rather than found.
fn gather(
    directory: &Path,
    by_type: &mut BTreeMap<String, Vec<String>>,
    runs: &mut Vec<(String, usize)>,
    top: bool,
) {
    let Ok(entries) = fs::read_dir(directory) else {
        return;
    };

    for entry in entries.flatten() {
        let path = entry.path();
        let name = entry.file_name().to_string_lossy().to_string();

        if path.is_dir() {
            if name == "superseded" {
                continue;
            }

            // A run folder holds only what that run was first to reach, which is the number worth
            // reporting per run -- but its names are already in the merged set, so they are not
            // added again.
            if name.starts_with("run_") {
                let count = count_names(&path);
                if count > 0 {
                    runs.push((name, count));
                }
                continue;
            }

            gather(&path, by_type, runs, false);
            continue;
        }

        if path.extension().and_then(|e| e.to_str()) != Some("txt") {
            continue;
        }

        // The pool census that sits beside a snapshot is not a findings file.
        if name.ends_with(".pools.txt") {
            continue;
        }

        let Some(kind) = path.file_stem().and_then(|s| s.to_str()) else {
            continue;
        };

        if !report_kind_allowed(&path, kind) { continue; }
        let names = by_type.entry(kind.to_owned()).or_default();
        for line in read_lines(&path) {
            names.push(line);
        }

        let _ = top;
    }
}

fn count_names(directory: &Path) -> usize {
    let Ok(entries) = fs::read_dir(directory) else {
        return 0;
    };

    entries
        .flatten()
        .filter(|entry| entry.path().extension().and_then(|e| e.to_str()) == Some("txt"))
        .filter(|entry| entry.path().file_stem().and_then(|s| s.to_str())
            .is_some_and(|kind| report_kind_allowed(&entry.path(), kind)))
        .map(|entry| read_lines(&entry.path()).len())
        .sum()
}

fn report_kind_allowed(path: &Path, kind: &str) -> bool {
    let game = path.components().rev().filter_map(|part| part.as_os_str().to_str())
        .map(str::to_ascii_uppercase).find(|part| slasher::config::GAMES.contains(&part.as_str()));
    game.is_none_or(|game| slasher::games::searchable(&game, slasher::strip_stamp(kind), false))
}

/// The names in one `hash,name` file. Read loosely: these have been written with both line
/// endings and by several different tools.
fn read_lines(path: &Path) -> Vec<String> {
    let Ok(bytes) = fs::read(path) else {
        return Vec::new();
    };

    String::from_utf8_lossy(&bytes)
        .lines()
        .filter_map(|line| {
            let line = line.trim();
            if line.is_empty() {
                return None;
            }

            match line.split_once(',') {
                Some((_, name)) if !name.trim().is_empty() => Some(name.trim().to_owned()),
                _ => Some(line.to_owned()),
            }
        })
        .collect()
}

/// `1234567` as `1,234,567`, because a seven digit achievement should not have to be counted by
/// eye.
fn thousands(value: usize) -> String {
    let digits = value.to_string();
    let mut out = String::with_capacity(digits.len() + digits.len() / 3);

    for (index, ch) in digits.chars().enumerate() {
        if index > 0 && (digits.len() - index) % 3 == 0 {
            out.push(',');
        }
        out.push(ch);
    }

    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn model_reports_follow_each_games_policy() {
        for game in slasher::config::GAMES {
            let path = PathBuf::from("findings").join(game.to_lowercase()).join("run_test").join("xmodel.txt");
            assert_eq!(report_kind_allowed(&path, "xmodel"), !slasher::games::modern(game));
            assert!(report_kind_allowed(&path, "image"));
            assert_eq!(report_kind_allowed(&path, "xmodel_20261008-010000"), !slasher::games::modern(game));
        }
    }

    #[test]
    fn thousands_are_separated() {
        assert_eq!(thousands(0), "0");
        assert_eq!(thousands(999), "999");
        assert_eq!(thousands(1_000), "1,000");
        assert_eq!(thousands(92_773), "92,773");
        assert_eq!(thousands(1_626_209), "1,626,209");
    }

    #[test]
    fn a_row_yields_its_name_not_its_hash() {
        let dir = std::env::temp_dir().join(format!("report_{}", std::process::id()));
        fs::create_dir_all(&dir).unwrap();
        let path = dir.join("xmodel.txt");
        fs::write(&path, "1a2b,p9_thing\r\n3c4d,p9_other\n").unwrap();

        assert_eq!(read_lines(&path), vec!["p9_thing", "p9_other"]);

        let _ = fs::remove_dir_all(&dir);
    }
}
