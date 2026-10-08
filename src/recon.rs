//! What everybody else is doing right now, asked of GitHub rather than guessed at.
//!
//! The local clone can only ever know what has been *merged*. It cannot know what is sitting in
//! an open pull request, and that is exactly where a duplicate comes from: two contributors
//! grind the same evening, the first opens a pull request, the second's clone has no idea, and
//! the second sends the same names an hour later. That has happened here byte for byte: five
//! submissions carry the same 430 names, and two more carry the same 372.
//! `python scripts/methods_report.py --duplicates` lists them.
//!
//! So before a search, and again before a submission, the open pull requests are read and every
//! name in them is treated as already claimed. It costs a few seconds and it is the difference
//! between a night's work and a night's duplicate.
//!
//! Everything here goes through `gh`, which is already a hard requirement for submitting, so
//! this adds no new dependency and no token handling of its own.

use std::collections::{BTreeMap, HashSet};
use std::path::{Path, PathBuf};
use std::process::Stdio;

use crate::{github, hash64, hash64_raw, ID_MASK};

/// One open submission somebody else has in flight.
pub struct OpenSubmission {
    pub number: u64,
    pub author: String,
    pub title: String,
    /// Every name the pull request adds, as it was written.
    pub names: Vec<String>,
    /// The run fingerprints its notes declare, when it declares any.
    pub fingerprints: Vec<String>,
}

/// The whole picture: what is merged, what is in flight, and what has already been swept.
#[derive(Default)]
pub struct Landscape {
    /// Every id already claimed by a merged submission or an open pull request.
    pub claimed: HashSet<u64>,
    /// How many of those came from open pull requests rather than the local clone.
    pub claimed_in_flight: usize,
    /// The open submissions themselves, for reporting.
    pub open: Vec<OpenSubmission>,
    /// Every run fingerprint that has already been submitted, and who ran it.
    pub swept: BTreeMap<String, String>,
    /// Set when GitHub could not be reached, so callers can say "unknown" rather than "none".
    pub offline: Option<String>,
}

impl Landscape {
    /// Whether a name has already been claimed by anybody.
    pub fn holds(&self, name: &str) -> bool {
        spellings_of(name).iter().any(|hash| self.claimed.contains(hash))
    }

    /// Whether this exact search has already been run and submitted by somebody.
    pub fn already_swept(&self, fingerprint: &str) -> Option<&str> {
        self.swept.get(fingerprint).map(String::as_str)
    }
}

/// Where the reconnaissance is cached between programs, so `submit` does not have to redo what
/// `start` did minutes ago -- and so an offline `submit` still has the last known picture.
pub fn cache() -> PathBuf {
    crate::paths::state().join("claimed.txt")
}

/// The file recording which searches have already been run to exhaustion by somebody.
pub fn swept_cache() -> PathBuf {
    crate::paths::state().join("swept.txt")
}

/// Reads the whole landscape: merged submissions from disk, open pull requests from GitHub.
///
/// `submissions` is the local folder, which after an update holds every merged batch. It is read
/// from disk rather than the API because it is already here and a few thousand files over the
/// network for information sitting on the same disk is a poor trade.
pub fn survey(repo: &str, submissions: &Path) -> Landscape {
    let mut landscape = Landscape::default();

    let merged = names_under(submissions);
    println!("  merged submissions on disk: {} name(s)", merged.len());
    for name in &merged {
        claim_all_offsets(&mut landscape.claimed, name);
    }

    for fingerprint in fingerprints_under(submissions) {
        landscape.swept.insert(fingerprint.0, fingerprint.1);
    }

    match open_pull_requests(repo) {
        Ok(open) => {
            let mut in_flight = 0;

            for submission in &open {
                for name in &submission.names {
                    if !landscape.holds(name) {
                        in_flight += 1;
                    }
                    claim_all_offsets(&mut landscape.claimed, name);
                }

                for fingerprint in &submission.fingerprints {
                    landscape
                        .swept
                        .insert(fingerprint.clone(), format!("{} (open #{})", submission.author, submission.number));
                }
            }

            landscape.claimed_in_flight = in_flight;
            landscape.open = open;
        }
        Err(why) => {
            landscape.offline = Some(why);
        }
    }

    landscape
}

/// Writes the landscape where the other programs can read it without asking GitHub again.
pub fn save(landscape: &Landscape) -> std::io::Result<()> {
    let path = cache();
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }

    let mut text = String::with_capacity(landscape.claimed.len() * 18);
    let mut ordered: Vec<&u64> = landscape.claimed.iter().collect();
    ordered.sort_unstable();

    for id in ordered {
        text.push_str(&format!("{id:x}\n"));
    }

    std::fs::write(path, text)?;

    let mut swept = String::new();
    for (fingerprint, who) in &landscape.swept {
        swept.push_str(&format!("{fingerprint},{who}\n"));
    }
    std::fs::write(swept_cache(), swept)
}

/// The claimed ids from a previous survey, for a program that could not reach GitHub itself.
pub fn load_cached() -> HashSet<u64> {
    std::fs::read_to_string(cache())
        .unwrap_or_default()
        .lines()
        .filter_map(|line| u64::from_str_radix(line.trim(), 16).ok())
        .collect()
}

/// The swept fingerprints from a previous survey.
pub fn load_cached_swept() -> BTreeMap<String, String> {
    std::fs::read_to_string(swept_cache())
        .unwrap_or_default()
        .lines()
        .filter_map(|line| {
            let (fingerprint, who) = line.trim().split_once(',')?;
            Some((fingerprint.to_owned(), who.to_owned()))
        })
        .collect()
}

/// Stops a search that somebody has already run to exhaustion under identical inputs.
///
/// This is the direct fix for the worst thing in this project's history: five contributors
/// submitting the same 430 names, two of them byte for byte. Nobody was careless. The general
/// search is deterministic, a fresh clone gives everybody the same inputs, and so it gives
/// everybody the same answer. The only way to stop the second person wasting their night is to
/// tell them, before it starts, that this search is already spent -- and point them somewhere
/// that is not.
pub fn warn_if_swept(fingerprint: &str) {
    if say_if_swept(fingerprint) && !std::env::args().any(|argument| argument == "--anyway") {
        std::process::exit(2);
    }
}

/// The same, without stopping.
///
/// For a search whose fingerprint cannot be known until it has run. `confirm_list` is the case:
/// its fingerprint includes a digest of the candidates, and the candidates arrive on a pipe, so
/// there is nothing to check until they have all been read. That is survivable because a list run
/// is seconds rather than an hour, and because `submit` drops the names anyway — but it still has
/// to be said, or the next run repeats it too.
pub fn note_if_swept(fingerprint: &str) {
    say_if_swept(fingerprint);
}

/// Says who already ran this, and whether anybody did.
fn say_if_swept(fingerprint: &str) -> bool {
    let Some(who) = load_cached_swept().get(fingerprint).cloned() else {
        return false;
    };

    eprintln!(
        "\nthis exact search has already been run to exhaustion and submitted by {who}.\n\n\
         Every input that decides what it finds is identical -- the same method, the same \
         game, the\nsame pools, the same beginnings and the same endings -- so it will return \
         their names and\nnothing else. Four contributors have already submitted the same 430 \
         names this way.\n\n\
         Re-measuring the lists is not the way out, though it does change this fingerprint: \
         three\nconsecutive folds returned 55 names, then 294, then 51, the last on a corpus \
         two and a half\ntimes larger. Do something that reaches new ground instead:\n\n  \
         - run a method that reaches elsewhere:  see METHODS.md, which says what each one gets at\n    \
         that nothing else does\n\n  \
         - invent one. That is the highest-value thing anybody does here, and the reason this\n    \
         repository is pointed at an assistant rather than run as a fixed program.\n\n\
         (or pass --anyway to run it regardless, knowing what it will return.)"
    );

    true
}

/// Every id a submitted name could be filed under, so a claim is recognised however it was
/// hashed.
///
/// Two normalisations, two maskings, four ids. The masking is because an asset id has had bit 63
/// cleared and the name's own hash may not have.
///
/// **The folding is the one that cost a pool.** Black Ops 4's SAB sound names keep their
/// backslashes and their ids are the hash of exactly that string -- 8,385 of the 8,385 known ones
/// reproduce unfolded and 0 fold (`AGENTS.md` §6). This function recorded only the folded
/// spelling, so every BO4 sound name anybody submitted was filed under an id no game holds:
/// `holds` answered false for all of them, `wanted_for_search` never dropped those ids, and two
/// contributors grinding the 70,878-id `sound_asset` pool -- the largest unnamed ground in the
/// project -- would each find and each submit the same names with nothing able to notice. Cheap
/// insurance in both directions: a name with no backslash hashes identically either way, so the
/// extra spelling costs nothing at all for every other pool.
fn spellings_of(name: &str) -> [u64; 4] {
    let folded = hash64(name);
    let raw = hash64_raw(name);

    [folded, folded & ID_MASK, raw, raw & ID_MASK]
}

/// Records a name under every spelling it could be claimed as. See [`spellings_of`].
fn claim(into: &mut HashSet<u64>, name: &str) {
    into.extend(spellings_of(name));
}

fn claim_all_offsets(into: &mut HashSet<u64>, name: &str) {
    claim(into, name);
    let hash = crate::feed(crate::games::IW_BASIS, name.as_bytes());
    into.extend([hash, hash & ID_MASK]);
}

/// Every open pull request against the repository, with the names each one adds.
///
/// The diff is read rather than the files, for two reasons: it is one call per pull request
/// instead of one per file, and it carries only what the branch *adds*, so a pull request that
/// happens to touch an existing file does not claim that whole file's contents.
fn open_pull_requests(repo: &str) -> Result<Vec<OpenSubmission>, String> {
    let listed = gh(&[
        "api",
        &format!("repos/{repo}/pulls?state=open&per_page=100"),
        "--jq",
        r#".[] | "\(.number)\t\(.user.login)\t\(.title)""#,
    ])?;

    let mut open = Vec::new();

    for line in listed.lines() {
        let mut fields = line.splitn(3, '\t');
        let Some(number) = fields.next().and_then(|value| value.parse::<u64>().ok()) else {
            continue;
        };
        let author = fields.next().unwrap_or("somebody").to_owned();
        let title = fields.next().unwrap_or("").to_owned();

        let diff = gh(&["pr", "diff", &number.to_string(), "--repo", repo]).unwrap_or_default();
        let (names, fingerprints) = added_by(&diff);

        open.push(OpenSubmission { number, author, title, names, fingerprints });
    }

    Ok(open)
}

/// The names and fingerprints a unified diff adds.
///
/// Only `+` lines, and only ones shaped like a submitted row: `<hex>,<name>`. A `+++` header is
/// not a name and neither is prose out of a notes file.
fn added_by(diff: &str) -> (Vec<String>, Vec<String>) {
    let mut names = Vec::new();
    let mut fingerprints = Vec::new();

    for line in diff.lines() {
        let Some(added) = line.strip_prefix('+') else {
            continue;
        };

        if added.starts_with("++") {
            continue;
        }

        let added = added.trim();

        if let Some(value) = added.strip_prefix("- fingerprint: ") {
            fingerprints.push(value.trim().to_owned());
            continue;
        }

        let Some((key, name)) = added.split_once(',') else {
            continue;
        };

        // A row is a hash and a name. Anything else on a `+` line is prose.
        if key.len() > 16 || key.is_empty() || u64::from_str_radix(key.trim(), 16).is_err() {
            continue;
        }

        let name = name.trim();
        if !name.is_empty() {
            names.push(name.to_owned());
        }
    }

    (names, fingerprints)
}

/// Every name in every `.txt` under a submissions tree.
fn names_under(directory: &Path) -> Vec<String> {
    let mut names = Vec::new();
    let mut stack = vec![directory.to_path_buf()];

    while let Some(here) = stack.pop() {
        let Ok(entries) = std::fs::read_dir(&here) else {
            continue;
        };

        for entry in entries.flatten() {
            let path = entry.path();

            if path.is_dir() {
                stack.push(path);
                continue;
            }

            if path.extension().and_then(|extension| extension.to_str()) == Some("txt") {
                names.extend(crate::read_names(&path));
            }
        }
    }

    names
}

/// The `- fingerprint: ...` lines in every submission's notes, and who submitted them.
fn fingerprints_under(directory: &Path) -> Vec<(String, String)> {
    let mut found = Vec::new();
    let mut stack = vec![directory.to_path_buf()];

    while let Some(here) = stack.pop() {
        let Ok(entries) = std::fs::read_dir(&here) else {
            continue;
        };

        for entry in entries.flatten() {
            let path = entry.path();

            if path.is_dir() {
                stack.push(path);
                continue;
            }

            if path.extension().and_then(|extension| extension.to_str()) != Some("md") {
                continue;
            }

            let who = here
                .file_name()
                .map(|name| name.to_string_lossy().to_string())
                .unwrap_or_else(|| "a previous submission".to_owned());

            let Ok(text) = std::fs::read_to_string(&path) else {
                continue;
            };

            for line in text.lines() {
                if let Some(value) = line.trim().strip_prefix("- fingerprint: ") {
                    found.push((value.trim().to_owned(), who.clone()));
                }
            }
        }
    }

    found
}

fn gh(arguments: &[&str]) -> Result<String, String> {
    let output = github::command()
        .args(arguments)
        .stderr(Stdio::piped())
        .output()
        .map_err(|error| format!("gh could not be run: {error}"))?;

    if !output.status.success() {
        return Err(String::from_utf8_lossy(&output.stderr).trim().to_owned());
    }

    Ok(String::from_utf8_lossy(&output.stdout).trim().to_owned())
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A diff yields the rows it adds and nothing else -- not the file headers, not removed
    /// rows, and not the prose around them.
    #[test]
    fn only_added_rows_count_as_claimed() {
        let diff = "\
diff --git a/submissions/x/material_1.txt b/submissions/x/material_1.txt
--- /dev/null
+++ b/submissions/x/material_1.txt
@@ -0,0 +1,2 @@
+1a2b3c4d,mc/mtl_thing_01
+55,mc/mtl_thing_02
-99,removed_name
 context,not_added
+- fingerprint: abc123
+Every name here was confirmed against the game.
";

        let (names, fingerprints) = added_by(diff);

        assert_eq!(names, vec!["mc/mtl_thing_01", "mc/mtl_thing_02"]);
        assert_eq!(fingerprints, vec!["abc123"]);
    }

    /// A claimed name is recognised under either spelling of its top bit, which is the whole
    /// reason both are stored.
    #[test]
    fn a_claimed_name_is_found_again() {
        let mut landscape = Landscape::default();
        claim(&mut landscape.claimed, "mc/mtl_test_thing");

        assert!(landscape.holds("mc/mtl_test_thing"));
        assert!(!landscape.holds("mc/mtl_test_other"));
    }

    /// A Black Ops 4 SAB name is claimed under the id the game actually holds -- the hash of the
    /// unfolded string. Filing only the folded spelling is what let two contributors grind the
    /// largest sound pool in the project and submit each other's names undetected.
    #[test]
    fn a_backslash_name_is_claimed_under_the_id_the_game_holds() {
        let name = r"vox\scripted\mpl\vox_thing";

        let mut landscape = Landscape::default();
        claim(&mut landscape.claimed, name);

        // The id a `--no-fold` search hunts, and the id it would have been filed under before.
        assert!(landscape.claimed.contains(&(hash64_raw(name) & ID_MASK)));
        assert!(landscape.claimed.contains(&(hash64(name) & ID_MASK)));
        assert!(landscape.holds(name));
    }

    /// And the extra spelling costs nothing for the names that have no backslash: they hash the
    /// same either way, so the set holds exactly what it held before.
    ///
    /// Asserted as the ids themselves rather than as a count. `2` is only right when bit 63 of
    /// this particular name's hash happens to be set -- rename the fixture and a correct
    /// implementation would fail the test.
    #[test]
    fn a_name_without_a_backslash_is_unchanged_by_it() {
        let name = "mc/mtl_plain_name";

        let mut landscape = Landscape::default();
        claim(&mut landscape.claimed, name);

        let folded = hash64(name);
        assert_eq!(landscape.claimed, HashSet::from([folded, folded & ID_MASK]));
    }
}
