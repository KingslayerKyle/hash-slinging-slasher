//! What this machine is set to grind, read from `config.toml` beside the binaries.
//!
//! The searches can look for names in every pool the game has, and eventually should. But the
//! cost of a search is carried by how many ids it is looking for: the peeled batches are
//! `wanted x endings` entries, the filter is sized from it, and every candidate is tested
//! against it. Searching two hundred pools when four of them hold what is actually wanted makes
//! every pass several times slower for names nobody asked for yet.
//!
//! So which pools a search targets is a setting rather than a constant. Narrow while the types
//! that matter are still far from complete; widened later, when they are close and the rest
//! becomes the interesting part. Capturing is unaffected -- a snapshot always holds every pool,
//! because throwing away a capture is expensive and re-taking one needs the game.
//!
//! The parser understands the subset of TOML this file actually uses -- comments, a section
//! header, `key = value`, and arrays of strings -- rather than pulling in a dependency to read
//! forty lines.

use std::collections::HashSet;
use std::fs;
use std::path::Path;


/// Where the settings live, looked for beside the working directory.
const CONFIG: &str = "config.toml";

/// The asset types worth grinding first, when nothing says otherwise.
///
/// Models (BO4/CW only), animations, images, materials, sound files and sound aliases. Everything else the game
/// holds is still captured and still confirmable -- it is simply not what a search spends its time
/// on until these are close to done.
///
/// `sound_asset` and `sound_alias` are both here and are different things. Files are the audio
/// itself and go to `fnv1a_xsounds.csv`; aliases are the names scripts and weapons refer to and go
/// to `fnv1a_soundbanks_aliases.csv`. Neither is a loader asset in Black Ops 4 -- both were read
/// out of the game and injected -- and filing one as the other would put names in the wrong table
/// upstream.
pub const DEFAULT_POOLS: &[&str] =
    &["xmodel", "xanim", "image", "material", "sound_asset", "sound_alias"];

/// Which pools the searches should look in.
pub enum Targets {
    /// Every pool the game holds, including the ones nobody has named yet.
    Everything,
    /// Only these pool indexes.
    Only(HashSet<usize>),
}

impl Targets {
    /// Whether a search should be looking for ids in this pool.
    pub fn wants(&self, pool: usize) -> bool {
        match self {
            Self::Everything => true,
            Self::Only(pools) => pools.contains(&pool),
        }
    }

    /// How this reads in a run's opening lines, since a search that quietly ignores most of the
    /// game should say so rather than let the numbers be a surprise.
    pub fn describe(&self) -> String {
        match self {
            Self::Everything => "every pool".to_owned(),
            Self::Only(pools) => {
                // `crate::pools()`, not the `POOLS` constant. The two games number their asset
                // types differently, and this used to read Black Ops 4's indexes out of Cold
                // War's list -- so a correctly targeted BO4 run announced itself as hunting
                // "destructibledef, physconstraints, xmodelmesh". The search was right and the
                // line describing it was wrong, which is the worst way round: it also went into
                // every submission's notes as the record of what had been searched.
                let table = crate::pools();

                let mut names: Vec<&str> = pools
                    .iter()
                    .filter_map(|index| table.get(*index).copied())
                    .collect();
                names.sort_unstable();

                format!("{} pool(s): {}", pools.len(), names.join(", "))
            }
        }
    }
}

/// A path from the settings, if it is set to anything.
///
/// Absent rather than defaulted: a path nobody configured is a path this machine does not have,
/// and guessing at somebody's folder layout is how one person's Desktop ends up in everyone's
/// source code.
pub fn path(key: &str) -> Option<std::path::PathBuf> {
    let text = fs::read_to_string(crate::paths::root().join(CONFIG)).unwrap_or_default();
    let raw = value_of(&text, key)?;
    let raw = raw.trim().trim_matches('"').trim_matches('\'');

    if raw.is_empty() {
        return None;
    }

    Some(std::path::PathBuf::from(raw))
}

/// The tags a snapshot can carry, and therefore the games that can be ground.
pub const GAMES: &[&str] = &["BLKOPSCW", "BLKOPS04", "MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"];

/// Where `start` records which game it chose, so a search does not have to be told.
///
/// The alternation would be worthless as advice alone: it would mean every search needed a flag
/// remembered from the output of an earlier command, which is exactly the shape of instruction
/// this project keeps finding does not survive. So the decision is written down and read back.
fn chosen_path() -> std::path::PathBuf {
    crate::paths::state().join("game.txt")
}

/// Whether the alternation has been deliberately switched off.
///
/// **Deliberately, and by a key that did not exist before.** `game = "BLKOPSCW"` cannot mean this,
/// and that is the whole point: `config.example.toml` shipped that line uncommented, so anybody
/// who copied the template months ago has it. Reading it as a decision would pin every one of
/// those contributors to Cold War forever, silently -- which is the precise failure being fixed,
/// reintroduced through the back door. A new key cannot be in an old file.
pub fn alternates() -> bool {
    let text = fs::read_to_string(crate::paths::root().join(CONFIG)).unwrap_or_default();
    flag(&text, "alternate_games") != Some(false)
}

/// Which game to grind, as the tag a snapshot carries internally.
///
/// The selected game determines its snapshot, pool census and hash policies. Modern ordinary
/// assets and aliases use different offsets; shared database readers select the source table
/// family without treating export-directory spellings as original names.
///
/// Four places are asked, most explicit first:
///
/// 1. `--game BLKOPS04` on the command line -- this run, whatever anything else says.
/// 2. `state/game.txt`, which is `start`'s alternation. This outranks `config.toml` on purpose:
///    the config's `game` line is in every clone copied from the old template, and letting it win
///    would pin those contributors to one title forever.
/// 3. `config.toml`, when the alternation has been switched off with `alternate_games = false`.
/// 4. The built-in default.
pub fn game() -> String {
    let arguments: Vec<String> = std::env::args().collect();
    if let Some(at) = arguments.iter().position(|argument| argument == "--game") {
        if let Some(named) = arguments.get(at + 1) {
            let named = named.to_uppercase();

            if GAMES.contains(&named.as_str()) {
                return named;
            }

            eprintln!(
                "`--game {named}` is not a game this holds a snapshot for. It is one of: {}",
                GAMES.join(", ")
            );
            std::process::exit(2);
        }
    }

    if alternates() {
        if let Some(chosen) = fs::read_to_string(chosen_path())
            .ok()
            .map(|raw| raw.trim().to_uppercase())
            .filter(|raw| GAMES.contains(&raw.as_str()))
        {
            return chosen;
        }
    }

    let text = fs::read_to_string(crate::paths::root().join(CONFIG)).unwrap_or_default();

    value_of(&text, "game")
        .map(|raw| raw.trim().trim_matches('"').trim_matches('\'').to_uppercase())
        .filter(|raw| GAMES.contains(&raw.as_str()))
        .unwrap_or_else(|| crate::GAME.to_owned())
}

/// Records the game the alternation picked, for the searches that follow.
pub fn choose_game(game: &str) -> std::io::Result<()> {
    let path = chosen_path();
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }

    fs::write(path, game)
}

/// Reads the settings, falling back to the defaults when there is no file or it says nothing.
///
/// Resolved against the repository root like every other read of this file, and not against the
/// working directory. It used to be the one exception, which meant a pass launched from anywhere
/// but the root silently fell back to `DEFAULT_POOLS` -- searching pools the contributor had not
/// asked for, and then writing the wrong pool set into both the run notes and the fingerprint, so
/// the record of what was searched disagreed with what was searched.
pub fn targets() -> Targets {
    read_targets(&crate::paths::root().join(CONFIG))
}

/// Advanced opt-in shared by searches and submission filtering. Listing xmodel or
/// setting all_pools in an older config does not opt into modern model recovery.
pub fn search_modern_models() -> bool {
    let text = fs::read_to_string(crate::paths::root().join(CONFIG)).unwrap_or_default();
    flag(&text, "search_modern_models") == Some(true)
}

fn read_targets(path: &Path) -> Targets {
    let text = fs::read_to_string(path).unwrap_or_default();
    let game = game();
    targets_from_text(&text, &game, crate::pools_for(&game))
}

fn targets_from_text(text: &str, game: &str, table: &[&str]) -> Targets {
    let opt_in = flag(text, "search_modern_models") == Some(true);
    let allowed = |kind: &str| crate::games::searchable(game, kind, opt_in);
    if flag(text, "all_pools") == Some(true) {
        if allowed("xmodel") {
            return Targets::Everything;
        }
        return Targets::Only(table.iter().enumerate()
            .filter(|(_, kind)| allowed(kind)).map(|(index, _)| index).collect());
    }

    let listed = list(&text, "pools");
    let names: Vec<String> = if listed.is_empty() {
        DEFAULT_POOLS.iter().map(|name| (*name).to_owned()).collect()
    } else {
        listed
    };

    let mut pools = HashSet::new();
    for name in &names {
        match table.iter().position(|kind| *kind == crate::games::canonical(name)) {
            Some(index) => {
                if allowed(table[index]) { pools.insert(index); }
            }
            None => eprintln!("config.toml lists a pool this game has no name for: {name}"),
        }
    }

    Targets::Only(pools)
}

/// The value of a `key = true` line, ignoring comments.
fn flag(text: &str, key: &str) -> Option<bool> {
    value_of(text, key).and_then(|value| value.parse().ok())
}

/// The entries of a `key = ["a", "b"]` line.
fn list(text: &str, key: &str) -> Vec<String> {
    let Some(value) = value_of(text, key) else {
        return Vec::new();
    };

    value
        .trim_start_matches('[')
        .trim_end_matches(']')
        .split(',')
        .map(|entry| entry.trim().trim_matches('"').trim_matches('\'').to_owned())
        .filter(|entry| !entry.is_empty())
        .collect()
}

/// The raw right-hand side of `key = ...`, with any trailing comment removed.
fn value_of(text: &str, key: &str) -> Option<String> {
    for line in text.lines() {
        let line = line.trim();
        if line.starts_with('#') {
            continue;
        }

        let Some((name, value)) = line.split_once('=') else {
            continue;
        };

        if name.trim() != key {
            continue;
        }

        // A comment after the value, but not a `#` inside a quoted string.
        let value = match value.find('#') {
            Some(at) if value[..at].matches('"').count() % 2 == 0 => &value[..at],
            _ => value,
        };

        return Some(value.trim().to_owned());
    }

    None
}

#[cfg(test)]
mod tests {
    use super::*;
    fn pool_index(kind: &str) -> Option<usize> { crate::pool_index_in(crate::POOLS, kind) }

    #[test]
    fn model_policy_applies_to_defaults_old_lists_all_pools_and_opt_in() {
        let table = ["xmodel", "xanim", "image", "material", "sound_asset", "sound_alias", "gesture"];
        for game in GAMES {
            for config in ["", "pools = [\"xmodel\", \"xanim\", \"image\", \"material\", \"sound_asset\", \"sound_alias\"]", "all_pools = true"] {
                let targets = targets_from_text(config, game, &table);
                assert_eq!(targets.wants(0), !crate::games::modern(game), "{game}: {config}");
                for pool in 1..6 { assert!(targets.wants(pool), "{game}: pool {pool}"); }
                let opted = targets_from_text(&format!("{config}\nsearch_modern_models = true"), game, &table);
                assert!(opted.wants(0), "explicit exception: {game}");
            }
            let only_model = targets_from_text("pools = [\"xmodel\"]", game, &table);
            assert_eq!(only_model.wants(0), !crate::games::modern(game));
            assert!(!only_model.wants(1), "exclusion must not widen a configured search");
        }
    }

    #[test]
    fn the_default_is_the_five_types_that_matter() {
        let targets = targets_from_text("", "BLKOPSCW", crate::POOLS);

        assert!(targets.wants(pool_index("xmodel").unwrap()));
        assert!(targets.wants(pool_index("image").unwrap()));
        assert!(targets.wants(pool_index("sound_asset").unwrap()));
        assert!(!targets.wants(pool_index("localizeentry").unwrap()));
        assert!(!targets.wants(pool_index("gesture").unwrap()));
    }

    #[test]
    fn the_switch_opens_everything_up() {
        let text = "[search]\nall_pools = true\npools = [\"xmodel\"]\n";
        let dir = std::env::temp_dir().join(format!("cfg_all_{}", std::process::id()));
        fs::create_dir_all(&dir).unwrap();
        let path = dir.join("config.toml");
        fs::write(&path, text).unwrap();

        let targets = targets_from_text(&fs::read_to_string(&path).unwrap(), "BLKOPSCW", crate::POOLS);
        assert!(targets.wants(pool_index("localizeentry").unwrap()));
        assert!(targets.wants(999));

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn a_listed_set_replaces_the_default_rather_than_adding_to_it() {
        let dir = std::env::temp_dir().join(format!("cfg_list_{}", std::process::id()));
        fs::create_dir_all(&dir).unwrap();
        let path = dir.join("config.toml");
        fs::write(&path, "pools = [\"localizeentry\", \"xanim\"]  # what I want\n").unwrap();

        let targets = targets_from_text(&fs::read_to_string(&path).unwrap(), "BLKOPSCW", crate::POOLS);
        assert!(targets.wants(pool_index("localizeentry").unwrap()));
        assert!(targets.wants(pool_index("xanim").unwrap()));
        assert!(!targets.wants(pool_index("xmodel").unwrap()));

        let _ = fs::remove_dir_all(&dir);
    }

    /// The turn-taking is on unless a key that could not be in an old file says otherwise.
    ///
    /// This is the guard on a nasty one. `config.example.toml` shipped `game = "BLKOPSCW"`
    /// uncommented, so clones copied from it months ago still carry it -- and if that counted as
    /// "this contributor chose Cold War", every one of them would be locked to Cold War forever
    /// without ever being told. `alternate_games` did not exist then, so it cannot be in an old
    /// file, which is the entire reason it is a separate key rather than a reading of `game`.
    #[test]
    fn an_old_config_naming_a_game_does_not_stop_the_turn_taking() {
        let legacy = "[search]\ngame = \"BLKOPSCW\"\n";
        assert_ne!(flag(legacy, "alternate_games"), Some(false));

        let switched_off = "[search]\ngame = \"BLKOPSCW\"\nalternate_games = false\n";
        assert_eq!(flag(switched_off, "alternate_games"), Some(false));
    }

    /// Only a game there is a snapshot for. A typo used to fall through as a game name and then
    /// silently match nothing; now it is rejected in favour of the default.
    #[test]
    fn a_game_the_snapshots_do_not_hold_is_not_accepted() {
        for game in GAMES {
            assert!(GAMES.contains(game));
        }

        assert!(!GAMES.contains(&"BLKOPS03"));
        assert!(!GAMES.contains(&""));
    }

    #[test]
    fn comments_and_quotes_are_not_taken_as_values() {
        assert_eq!(value_of("# pools = [\"no\"]\npools = [\"yes\"]", "pools").unwrap(), "[\"yes\"]");
        assert_eq!(flag("all_pools = false # not yet", "all_pools"), Some(false));
    }
}

/// Optional subset of captured games to rotate. Absent means every installed capture.
pub fn rotation_games() -> Vec<String> {
    let text = fs::read_to_string(crate::paths::root().join(CONFIG)).unwrap_or_default();
    let games = list(&text, "games");
    for game in &games { assert!(GAMES.contains(&game.as_str()), "unsupported rotation game {game}"); }
    games
}
