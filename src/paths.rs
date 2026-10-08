//! Where everything lives.
//!
//! Every path here is **relative to the repository by default**, so a fresh clone works with no
//! setup and nothing about one person's machine is baked into the code. Anything that does depend
//! on a particular machine -- where a game build was unpacked --
//! is read from `config.toml` and simply absent for most people, because most people are grinding
//! against a captured snapshot and never touch a game file.
//!
//! A search that cannot find its tables reports every published name in the game as a new
//! discovery, so the one rule here is that a missing path is reported rather than guessed at.

use std::path::PathBuf;

use crate::config;

/// Where each thing lives when nobody has configured it: all inside the repository, so a fresh
/// clone works untouched and nothing about one person's machine is implied by the code.
pub const DEFAULT_TABLES: &str = "tables";
pub const DEFAULT_SNAPSHOTS: &str = "snapshots";
pub const DEFAULT_FINDINGS: &str = "findings";
pub const DEFAULT_SUBMISSIONS: &str = "submissions";

/// The hash tables, as csv. These say what the community already resolves, which is the whole of
/// the difference between a discovery and a name somebody published last week.
pub fn tables() -> PathBuf {
    config::path("tables").unwrap_or_else(|| root().join(DEFAULT_TABLES))
}

/// The captured asset ids, one file per game. This is what a name is confirmed against, and the
/// only thing here that cannot be regenerated without owning the game.
pub fn snapshots() -> PathBuf {
    config::path("snapshots").unwrap_or_else(|| root().join(DEFAULT_SNAPSHOTS))
}

/// What this machine has confirmed: a file per asset type, plus a folder per run holding only
/// what that run was the first to reach. The run folders are what gets submitted.
/// Where this machine's confirmed names go, **for the game being ground**.
///
/// Per game, and that is a correctness requirement rather than tidiness. The two games number
/// their asset types differently -- `xmodel` is 6 in Cold War and 4 in Black Ops 4 -- so a name is
/// filed under a label that only means anything alongside the game it came from. A single flat
/// folder made switching `game` in config.toml silently mix the two into one `material.txt`, and
/// `submit` would then send them as one batch under whichever game happened to be configured at
/// the time. That is exactly the thing rule 3 in AGENTS.md says must never happen, and until this
/// it was one edited config line away.
pub fn findings() -> PathBuf {
    findings_root().join(config::game().to_lowercase())
}

/// The folder holding every game's findings.
///
/// Two callers want this rather than one game's. **Seeding**: a name confirmed in one game is
/// good candidate material for the other, because Cold War carries a great deal of Black Ops 4's
/// content -- so a search reads all of them and writes only its own. **Submitting**: a session
/// may have ground both, and the run folder's path is what says which game each batch is.
pub fn findings_root() -> PathBuf {
    config::path("findings").unwrap_or_else(|| root().join(DEFAULT_FINDINGS))
}

/// Which game a path under the findings root belongs to, by the folder it sits in.
///
/// The path is the record. A run folder carries no game inside it, and inferring one from the
/// config at submission time is how a batch ends up labelled with the wrong game hours later.
pub fn game_of(path: &std::path::Path) -> Option<String> {
    let root = findings_root();
    let rest = path.strip_prefix(&root).ok()?;

    Some(rest.components().next()?.as_os_str().to_string_lossy().to_uppercase())
}

/// Moves a flat `findings/` from before the per-game split into the game it was ground under.
///
/// Everything written before the split was Cold War, because that was the only default there was.
/// Left where it is, it would be read as seeds and never submitted, so it is moved rather than
/// abandoned -- results only ever grow.
pub fn migrate_flat_findings() -> Option<String> {
    let root = findings_root();
    let into = root.join(crate::GAME.to_lowercase());

    if into.exists() {
        return None;
    }

    let mut strays: Vec<PathBuf> = Vec::new();
    for entry in std::fs::read_dir(&root).ok()?.flatten() {
        let path = entry.path();
        let name = entry.file_name().to_string_lossy().to_string();

        let is_result = path.extension().and_then(|e| e.to_str()) == Some("txt");
        let is_run = path.is_dir() && name.starts_with("run_");

        if is_result || is_run {
            strays.push(path);
        }
    }

    if strays.is_empty() {
        return None;
    }

    std::fs::create_dir_all(&into).ok()?;

    for stray in &strays {
        if let Some(name) = stray.file_name() {
            let _ = std::fs::rename(stray, into.join(name));
        }
    }

    Some(format!(
        "moved {} existing result file(s) and run folder(s) into {} -- findings are now kept per \
         game, because the two number their asset types differently and mixing them mislabels \
         every name",
        strays.len(),
        into.display()
    ))
}

/// Where a run's own findings are gathered before being sent.
pub fn submissions() -> PathBuf {
    config::path("submissions").unwrap_or_else(|| root().join(DEFAULT_SUBMISSIONS))
}

/// The measured beginnings and endings, generated by `scripts/derive_lists.py`. Committed, so a
/// fresh clone can search before it has measured anything itself.
pub const SUFFIX_LIST: &str = "data/suffixes.txt";
pub const PREFIX_LIST: &str = "data/prefixes.txt";

/// The same, measured from the sound and alias tables instead.
///
/// A separate pair rather than a bigger shared one. The lists are capped because coincidental
/// matches scale with `stems x beginnings x endings`, and that budget is real -- but a sound
/// ending tried against a model id can only ever be a coincidence, never a match. Sharing one
/// ceiling therefore made both halves worse: sound displaced endings covering 115,606 published
/// names, and in return the model passes carried endings that could not match what they hunted.
/// Measured apart, each search spends its whole budget on vocabulary that can actually reach its
/// own targets.
pub const SOUND_SUFFIX_LIST: &str = "data/sound.suffixes.txt";
pub const SOUND_PREFIX_LIST: &str = "data/sound.prefixes.txt";

/// Where this machine's view of the world is kept: what is claimed, what has been swept, and
/// whether the startup checks passed. Always inside the repository, never beside the caller.
pub fn state() -> PathBuf {
    root().join("state")
}

/// The repository the tools are running in, found at runtime.
///
/// **Every default above goes through this**, and that is not tidiness. The paths used to be
/// relative to the working directory, so running `bin\windows\start.exe` from inside
/// `bin\windows` -- which is exactly how somebody double-clicking it arrives -- cloned the whole
/// of cod-name-db into `bin/windows/cod-name-db`, wrote findings there, and left the real
/// repository untouched. Nothing errored. It simply did all of its work in the wrong place, which
/// is the worst way for this to fail, because the next run does it again.
///
/// Never baked in at compile time: a binary built on one machine must still find `data/` on
/// another, and the committed `bin/windows/` executables are exactly that. Run from the
/// repository -- as every documented command is -- the working directory is it; otherwise the
/// executable's own ancestors are tried, because `bin/windows/` and `target/release/` both sit
/// two levels inside.
pub fn root() -> PathBuf {
    let here = PathBuf::from(".");
    if here.join(SUFFIX_LIST).exists() {
        return here;
    }

    if let Ok(exe) = std::env::current_exe() {
        let mut ancestor = exe.parent();
        while let Some(directory) = ancestor {
            if directory.join(SUFFIX_LIST).exists() {
                return directory.to_path_buf();
            }
            ancestor = directory.parent();
        }
    }

    here
}

// --- Only needed by whoever owns a game build. Absent for everyone else. ---

/// Strings scraped out of a game build. The only source of real asset names for a title whose
/// build is unhashed, and irrelevant to anyone grinding from a snapshot.
pub fn harvest() -> Option<PathBuf> {
    config::path("harvest")
}

/// A folder of names borrowed from another title. Cold War carries a great deal of Black Ops 4's
/// content, so those names are candidates here even though they are never measured for
/// conventions.
pub fn borrowed() -> Option<PathBuf> {
    config::path("borrowed")
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A fresh clone must work with no configuration at all, and must not reach outside itself.
    ///
    /// The defaults are asserted rather than the resolved paths, because a machine with a
    /// `config.toml` resolves to whatever that says -- which is the whole point of having one.
    #[test]
    fn the_defaults_are_inside_the_repository() {
        for default in [
            DEFAULT_TABLES,
            DEFAULT_SNAPSHOTS,
            DEFAULT_FINDINGS,
            DEFAULT_SUBMISSIONS,
        ] {
            let path = PathBuf::from(default);
            assert!(path.is_relative(), "{default} should be relative");
            assert!(!default.contains(':'), "{default} should not name a drive");
            assert!(!default.starts_with(".."), "{default} should not escape the repository");
        }
    }

    /// Findings live under the game they were ground for, and the path is what says which.
    ///
    /// This is the guard on rule 3 in AGENTS.md. Before the split, changing `game` in config.toml
    /// wrote Black Ops 4 names into the same `material.txt` as Cold War's, and `submit` sent them
    /// as one batch under whichever game happened to be configured at the time.
    #[test]
    fn a_run_folder_says_which_game_it_belongs_to() {
        let root = findings_root();

        for game in crate::config::GAMES {
            let run = root.join(game.to_lowercase()).join("run_20260819-000000_all");
            assert_eq!(game_of(&run).as_deref(), Some(*game), "for {game}");
        }
    }

    /// A path outside the findings tree has no game, rather than being given a wrong one.
    #[test]
    fn a_path_outside_the_findings_tree_has_no_game() {
        assert_eq!(game_of(std::path::Path::new("somewhere/else/run_x")), None);
    }

    /// The machine-specific ones are absent rather than wrong when nobody has set them.
    #[test]
    fn a_path_nobody_configured_is_absent() {
        // Whatever this machine's config says, these must be Options rather than a guess at
        // somebody's Desktop.
        let _ = harvest();
        let _ = borrowed();
    }
}

/// Vocabulary measured from this game's capture, separate from the committed legacy corpus.
pub fn vocabulary(list: &str) -> PathBuf {
    let game = crate::config::game();
    if crate::games::modern(&game) {
        root().join("data/modern").join(game.to_lowercase()).join(std::path::Path::new(list).file_name().unwrap())
    } else { root().join(list) }
}
