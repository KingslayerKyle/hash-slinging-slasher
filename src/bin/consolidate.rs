//! Files every string anywhere under the harvest folder by the pool the loader holds it in.
//!
//! The results of this work accumulated across a dozen run folders, a separate by-type folder
//! and a few loose files, in two different row formats and two different line endings. Merging
//! those by hand means deciding, for each file, which asset type it holds -- and one wrong
//! decision puts hashes in the wrong table, which is the one mistake that is expensive to undo.
//!
//! So no such decision is made. The asset type of a name is not a property of the file it was
//! found in; it is a property of the hash, and the loader is holding the answer. Every string is
//! taken from every file with its stored hash thrown away, hashed here, and looked for among the
//! loaded ids. Where it is found, the pool it was found in names the type. A file name never
//! gets a vote, so a misfiled row in the input cannot become a misfiled row in the output.
//!
//! Two things this is deliberately exhaustive about, because a partial answer here looks exactly
//! like a complete one:
//!
//! **Every pool, not the named ones.** `POOLS` names thirty three asset types and every earlier
//! search walked exactly those. The loader allocates `POOL_COUNT`, and Cold War fills far more
//! than thirty three of them. A pool this project never named still holds assets whose ids a
//! candidate can match, so all of them are walked and the unnamed ones are filed under their
//! index.
//!
//! **Every file, not the text ones.** A `.csv`, a `.log`, even a database, holds strings, and a
//! string is a candidate wherever it is written down. Files are read as bytes and split into
//! runs of printable characters, which treats text and binary alike and cannot skip a file for
//! being the wrong shape.
//!
//! What is left is whether a found name is a *discovery*, and the published tables answer that:
//! a hash any of them already resolves is known to the community, whoever found it. Only what
//! they do not resolve is written.
//!
//! Writing is append-only. Rewriting a result file has silently destroyed a result set here
//! before, so this never truncates one: it reads what is there, and adds only what is missing.

use std::collections::{BTreeMap, HashMap, HashSet};
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};

use slasher::cordycep::{CordycepInstance, POOL_COUNT};
use slasher::{
    hash64, paths, pool_index, table_keys, tables_look_complete, GAME, ID_MASK, POOLS,
};

/// A full load of this game. Well short of it means the loader is still mapping files, and a
/// name that failed to match would have failed only because it has not got there yet.
const A_FULL_LOAD: usize = 100_000;

/// The widest a leading field can be and still be one of our stored hashes. Sixteen hex digits
/// is a full u64; the floor keeps a short all-hex *name* -- `decaf`, `beef` -- from being read
/// as a key and thrown away.
const KEY_WIDTH: std::ops::RangeInclusive<usize> = 8..=16;

/// The shortest run of printable bytes worth treating as a string. Below this it cannot be an
/// asset name and is almost certainly a fragment of something binary.
const SHORTEST: usize = 3;

/// Pools that hold an asset under *another* asset's name rather than under a name of their own.
///
/// A model's skeleton and its collision are filed under the model's name, and a map is held in
/// every map pool at once. So a name found in one of these is not a name *of* one of these: it
/// is a model name, or a map name, that this pool also answers to.
const DERIVED: &[&str] = &[
    "xskeleton", "xcollision", "xmodelmesh", "col_map", "com_map", "game_map", "gfx_map",
];

/// What a pool is called, which for one this project has never named is its index.
fn pool_name(index: usize) -> String {
    POOLS
        .get(index)
        .map(|name| (*name).to_owned())
        .unwrap_or_else(|| format!("pool_{index}"))
}

/// How much a pool deserves to be the one a name is filed under.
///
/// A pool that names its own assets wins. Failing that an unnamed pool, which may well name its
/// own assets too -- we simply do not know what it is. A derived pool loses, because a name found
/// there is a name of something else.
fn rank(index: usize) -> u8 {
    if index >= POOLS.len() {
        1
    } else if DERIVED.contains(&POOLS[index]) {
        2
    } else {
        0
    }
}

/// The one pool a name is filed under, out of every pool holding its hash.
///
/// Among equals the lowest index wins, so the choice is the same on every run rather than
/// dependent on the order the loader was walked in.
fn primary(pools: &[usize]) -> usize {
    pools
        .iter()
        .copied()
        .min_by_key(|index| (rank(*index), *index))
        .unwrap_or(pools[0])
}

fn main() {
    let root = std::env::args()
        .nth(1)
        .map(PathBuf::from)
        .unwrap_or_else(|| paths::harvest().unwrap_or_default());
    let out = std::env::args()
        .nth(2)
        .map(PathBuf::from)
        .unwrap_or_else(|| paths::findings());

    // The loader first: there is no point reading a million strings to then discover the wrong
    // game is open, and writing one game's names into another's files is not recoverable.
    let instance = match CordycepInstance::open() {
        Ok(instance) => instance,
        Err(error) => {
            eprintln!("the loader is not readable: {error}");
            eprintln!("open Cordycep with Cold War and run `loadall`, then try again.");
            return;
        }
    };

    if instance.game_id() != GAME {
        eprintln!("the loader has {} open, not {GAME}", instance.game_id());
        return;
    }

    // Every pool an id appears in, over every pool the loader allocates. Several pools share a
    // name's hash, so this is a list rather than a single answer.
    let mut loaded: HashMap<u64, Vec<usize>> = HashMap::new();
    let mut assets = 0_usize;
    let mut named_assets = 0_usize;
    let mut filled = 0_usize;

    for index in 0..POOL_COUNT {
        let mut in_pool = 0_usize;

        for asset in instance.assets(index) {
            in_pool += 1;
            loaded
                .entry((asset.id as u64) & ID_MASK)
                .or_default()
                .push(index);
        }

        if in_pool > 0 {
            filled += 1;
            assets += in_pool;
            if index < POOLS.len() {
                named_assets += in_pool;
            }
        }
    }

    println!(
        "loaded assets: {assets} across {filled} pools, distinct ids: {}",
        loaded.len()
    );
    println!(
        "  of those, {named_assets} are in the {} pools this project names, {} in pools it does not",
        POOLS.len(),
        assets - named_assets
    );

    if assets < A_FULL_LOAD {
        eprintln!(
            "\nonly {assets} assets are loaded, far short of a full load. Every name would be \
             judged against a fraction of the game. Run `loadall` and try again."
        );
        return;
    }

    // What the community already resolves. Without this every published name in the game comes
    // out looking like a discovery, so a short read has to stop the run rather than skew it.
    let known = table_keys();
    println!("hashes the tables already resolve: {}", known.len());

    if !tables_look_complete(&known) {
        eprintln!(
            "\nthe tables read short at {} hashes, which means they moved rather than that the \
             game got smaller. Run `cargo run --release --bin fetch-tables` and try again.",
            known.len()
        );
        return;
    }

    let mut files = Vec::new();
    collect_files(Path::new(&root), &mut files);
    files.sort();

    let mut found: BTreeMap<String, BTreeMap<u64, String>> = BTreeMap::new();
    let mut tested = 0_u64;
    let mut already = 0_usize;
    let mut multi = 0_usize;
    let mut unreadable = 0_usize;

    for file in &files {
        // Read as bytes: a harvest file scraped out of a game build is not always valid UTF-8,
        // and a reader that insists on it would skip the whole file rather than the one bad
        // byte. Skipping a file silently is exactly what must not happen here.
        let Ok(bytes) = fs::read(file) else {
            unreadable += 1;
            continue;
        };

        for run in printable_runs(&bytes) {
            for candidate in strings_from_line(run) {
                tested += 1;

                let hash = hash64(&candidate);
                let id = hash & ID_MASK;

                let Some(pools) = loaded.get(&id) else {
                    continue;
                };

                // Known to the community already, whoever found it. Not a discovery.
                if known.contains(&hash) || known.contains(&id) {
                    already += 1;
                    continue;
                }

                if pools.len() > 1 {
                    multi += 1;
                }

                // A scraped line may separate its directories with backslashes. The hash folds
                // those to forward slashes, so both spellings reach the asset, but only one is
                // the spelling the published tables use, and it is the one worth writing down.
                let name = candidate.replace('\\', "/");

                found
                    .entry(pool_name(primary(pools)))
                    .or_default()
                    .entry(id)
                    .or_insert(name);
            }
        }
    }

    println!(
        "\nread {} files ({unreadable} unreadable), tested {tested} candidate strings",
        files.len()
    );

    // The one cost of testing a great many strings. It is not the clock -- hashing is cheap --
    // it is that a candidate can land on a loaded id by coincidence.
    println!(
        "names expected to match by chance at this size: {:.4}",
        tested as f64 * loaded.len() as f64 / 9.223e18
    );

    let hits: usize = found.values().map(BTreeMap::len).sum();
    println!("matched the loader: {hits} unnamed, {already} hits already in the tables");
    if multi > 0 {
        println!("{multi} hits were held in more than one pool, and are filed under the one they name");
    }

    match append(&out, &found) {
        Ok(()) => println!("\nwritten to {}", out.display()),
        Err(error) => eprintln!("\ncould not write to {}: {error}", out.display()),
    }
}

/// Every file under a folder, however deep, whatever it is called -- except the tables.
///
/// Not just the text ones: a log, a scrape with no extension, anything holding strings is worth
/// reading, because a string is a candidate wherever it is written down.
///
/// The hash tables are the exception, and skipping them is the point rather than an oversight.
/// They are what a find is measured *against*: every name in one is by definition already
/// resolved, so taking a name out of a table, hashing it, and asking the tables whether they
/// resolve it can only ever answer yes. It is a closed loop that costs millions of lookups to
/// learn nothing. What the tables are good for -- their names cut into pieces, as raw material
/// for building candidates that are *not* in them -- is the general search's job, not this one's.
fn collect_files(directory: &Path, into: &mut Vec<PathBuf>) {
    let Ok(entries) = fs::read_dir(directory) else {
        return;
    };

    for entry in entries.flatten() {
        let path = entry.path();

        if path.is_dir() {
            collect_files(&path, into);
        } else if !is_table(&path) {
            into.push(path);
        }
    }
}

/// Whether a file is one of the hash tables rather than a source of candidates.
///
/// Both forms count: the databases themselves, and the csv they are converted into, which live
/// in the csv folders `fetch-tables` pulls from `echo000/cod-name-db`.
fn is_table(path: &Path) -> bool {
    if path.extension().and_then(|e| e.to_str()) == Some("cdb") {
        return true;
    }

    path.extension().and_then(|e| e.to_str()) == Some("csv")
        && path
            .parent()
            .and_then(Path::file_name)
            .and_then(|name| name.to_str())
            .is_some_and(|name| name.starts_with("hash_csv"))
}

/// The runs of printable characters in a file.
///
/// Splitting on anything unprintable turns a text file into its lines and a binary one into the
/// strings buried in it, by the same rule, so no file has to be recognised as one or the other.
fn printable_runs(bytes: &[u8]) -> impl Iterator<Item = &str> {
    bytes
        .split(|byte| !matches!(byte, 0x20..=0x7E))
        .filter(|run| run.len() >= SHORTEST)
        .filter_map(|run| std::str::from_utf8(run).ok())
        .map(str::trim)
        .filter(|run| !run.is_empty())
}

/// The candidate strings one line offers.
///
/// A line is `name`, or `hash,name`, or `hash,type,name` depending on which search wrote it.
/// The parsed name is what we want -- but the parse is a guess about a format, and a wrong guess
/// would silently drop a real name. So the raw line is always offered as well. Testing a string
/// that is not a name costs a hash and a failed lookup; failing to test one costs the name.
fn strings_from_line(line: &str) -> Vec<String> {
    let mut out = vec![line.to_owned()];

    let Some((first, rest)) = line.split_once(',') else {
        return out;
    };

    let first = first.trim();
    if !(KEY_WIDTH.contains(&first.len()) && first.chars().all(|c| c.is_ascii_hexdigit())) {
        return out;
    }

    // `hash,type,name`, as the loose "other pools" file is written.
    if let Some((second, tail)) = rest.split_once(',') {
        if pool_index(second.trim()).is_some() && !tail.trim().is_empty() {
            out.push(tail.trim().to_owned());
            return out;
        }
    }

    let rest = rest.trim();
    if !rest.is_empty() {
        out.push(rest.to_owned());
    }

    out
}

/// Where a type's file already lives, which may not be where a fresh one would be put.
///
/// The results folder gets organised by hand -- the types that matter moved into a folder of
/// their own, the ones superseded into another. A run that ignored that would write a second
/// `material.txt` at the top level beside the one already filed away, and the set would quietly
/// be in two places. So an existing file wins wherever it is, and only a type that has never
/// been written before lands at the top.
fn existing_path(directory: &Path, kind: &str) -> PathBuf {
    let file = format!("{kind}.txt");
    let root = directory.to_path_buf();

    if root.join(&file).exists() {
        return root.join(&file);
    }

    if let Ok(entries) = fs::read_dir(&root) {
        let mut folders: Vec<PathBuf> = entries
            .flatten()
            .map(|entry| entry.path())
            .filter(|path| path.is_dir())
            .collect();

        // Sorted, so which folder wins is the same on every run rather than the order the
        // filesystem happened to hand them back in.
        folders.sort();

        for folder in folders {
            let candidate = folder.join(&file);
            if candidate.exists() {
                return candidate;
            }
        }
    }

    root.join(&file)
}

/// Adds what is missing to a file per type, and never takes anything out.
///
/// The file is read first and opened for appending, not writing: a run that crashes half way
/// leaves the previous contents whole, and a name that reached one of these files cannot be
/// removed by a later run whatever its rules decide.
fn append(directory: &Path, found: &BTreeMap<String, BTreeMap<u64, String>>) -> std::io::Result<()> {
    fs::create_dir_all(directory)?;

    println!("\n{:<24} {:>10} {:>10} {:>10}", "type", "had", "added", "now");

    let mut total = 0_usize;
    let mut added_all = 0_usize;

    for (kind, rows) in found {
        let path = existing_path(directory, kind);

        // What is already filed here, by id. Read tolerantly: these files have been written with
        // both line endings, and `lines` handles either.
        let existing: HashSet<u64> = fs::read(&path)
            .map(|bytes| {
                String::from_utf8_lossy(&bytes)
                    .lines()
                    .filter_map(|line| {
                        let (key, _) = line.trim().split_once(',')?;
                        u64::from_str_radix(key.trim(), 16).ok().map(|id| id & ID_MASK)
                    })
                    .collect()
            })
            .unwrap_or_default();

        let had = existing.len();

        let mut fresh: Vec<(&u64, &String)> =
            rows.iter().filter(|(id, _)| !existing.contains(id)).collect();
        fresh.sort_by(|a, b| a.1.to_lowercase().cmp(&b.1.to_lowercase()));

        if !fresh.is_empty() {
            let mut file = fs::OpenOptions::new().create(true).append(true).open(&path)?;
            for (id, name) in &fresh {
                writeln!(file, "{id:x},{name}")?;
            }
        }

        total += had + fresh.len();
        added_all += fresh.len();
        println!(
            "{kind:<24} {had:>10} {:>10} {:>10}",
            fresh.len(),
            had + fresh.len()
        );
    }

    println!("\ntotal: {total} ({added_all} added by this run)");

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The raw line is always a candidate, so a format this does not know about still gets tried.
    #[test]
    fn a_plain_name_is_offered_whole() {
        assert_eq!(strings_from_line("mc/mtl_test"), vec!["mc/mtl_test"]);
    }

    #[test]
    fn a_hash_is_dropped_but_the_line_is_still_offered() {
        let out = strings_from_line("5f6cbc3da781c77d,wc/wood_worn_painted_01_blue");

        assert!(out.contains(&"wc/wood_worn_painted_01_blue".to_owned()));
        assert!(out.contains(&"5f6cbc3da781c77d,wc/wood_worn_painted_01_blue".to_owned()));
    }

    /// The loose "other pools" file carries its type in the middle. We drop it and let the
    /// loader say what the type is, but the raw line survives as a candidate regardless.
    #[test]
    fn a_type_column_is_dropped() {
        let out = strings_from_line("7c3deb4485d6ba84,xmodel,bsh_boat_exterior_light_01_stk_ems");

        assert!(out.contains(&"bsh_boat_exterior_light_01_stk_ems".to_owned()));
    }

    /// A short all-hex name is a name, not a key, and must not be eaten as one.
    #[test]
    fn a_short_hex_name_is_not_mistaken_for_a_key() {
        let out = strings_from_line("beef,cafe");

        assert!(out.contains(&"beef,cafe".to_owned()));
        assert!(!out.contains(&"cafe".to_owned()));
    }

    /// A name that itself contains a comma keeps it.
    #[test]
    fn a_comma_inside_a_name_survives() {
        let out = strings_from_line("1234abcd5678ef90,ui/hint,press_to_use");

        assert!(out.contains(&"ui/hint,press_to_use".to_owned()));
    }

    /// A model's skeleton and collision are filed under the model's name, so the name belongs to
    /// the model pool and not to the pools it merely also answers to.
    #[test]
    fn a_model_name_beats_the_pools_derived_from_it() {
        let model = pool_index("xmodel").unwrap();
        let skeleton = pool_index("xskeleton").unwrap();
        let collision = pool_index("xcollision").unwrap();

        assert_eq!(primary(&[skeleton, model, collision]), model);
        assert_eq!(primary(&[collision, skeleton]), collision);
    }

    /// A map is held in every map pool at once; only one of them should get the name.
    #[test]
    fn a_map_is_filed_once() {
        let clip = pool_index("clip_map").unwrap();
        let gfx = pool_index("gfx_map").unwrap();

        assert_eq!(primary(&[gfx, clip]), clip);
    }

    /// A pool with a name of its own beats one we cannot identify, which in turn beats a pool
    /// that holds another asset's name.
    #[test]
    fn a_named_pool_beats_an_unknown_one_which_beats_a_derived_one() {
        let model = pool_index("xmodel").unwrap();
        let skeleton = pool_index("xskeleton").unwrap();
        let unknown = POOLS.len() + 151;

        assert_eq!(primary(&[unknown, model]), model);
        assert_eq!(primary(&[skeleton, unknown]), unknown);
    }

    /// A pool this project never named is filed under its index rather than dropped.
    #[test]
    fn an_unnamed_pool_is_named_for_its_index() {
        let unknown = POOLS.len();
        assert_eq!(pool_name(unknown), format!("pool_{unknown}"));
        assert_eq!(pool_name(6), "xmodel");
    }

    /// Text splits into lines and binary splits into the strings buried in it, by one rule.
    #[test]
    fn runs_are_taken_out_of_text_and_binary_alike() {
        let runs: Vec<&str> = printable_runs(b"one\ntwo\x00\x01three").collect();

        assert_eq!(runs, vec!["one", "two", "three"]);
    }


    /// A folder organised by hand keeps its organisation: a type already filed away is appended
    /// to where it lives, not written a second time at the top.
    #[test]
    fn an_existing_file_is_found_wherever_it_was_filed() {
        let dir = std::env::temp_dir().join(format!("consolidate_test_{}", std::process::id()));
        let _ = fs::remove_dir_all(&dir);
        fs::create_dir_all(dir.join("important")).unwrap();
        fs::write(dir.join("important").join("material.txt"), "1,a
").unwrap();
        fs::write(dir.join("xanim.txt"), "2,b
").unwrap();

        let root = dir.as_path();

        assert_eq!(existing_path(root, "material"), dir.join("important").join("material.txt"));
        assert_eq!(existing_path(root, "xanim"), dir.join("xanim.txt"));
        assert_eq!(existing_path(root, "brand_new"), dir.join("brand_new.txt"));

        let _ = fs::remove_dir_all(&dir);
    }

    /// A run too short to be a name is not worth testing.
    #[test]
    fn a_tiny_fragment_is_not_a_candidate() {
        let runs: Vec<&str> = printable_runs(b"ab\x00longer_name").collect();

        assert_eq!(runs, vec!["longer_name"]);
    }

    /// The tables are what a find is measured against, so feeding them back in as candidates is
    /// a closed loop: every name in one is already resolved by definition.
    #[test]
    fn the_tables_are_not_read_as_candidates() {
        assert!(is_table(Path::new(r"x\cw_name_work\hash_csv_live\fnv1a_xmodels.cdb")));
        assert!(is_table(Path::new(r"x\cw_name_work\hash_csv_live\fnv1a_xmodels.csv")));
        assert!(is_table(Path::new(r"x\cw_name_work\hash_csv_fresh\fnv1a_ximages.csv")));
    }

    /// A scrape is a source of candidates whatever it is called, including a csv that is not a
    /// converted table.
    #[test]
    fn a_scrape_is_still_read() {
        assert!(!is_table(Path::new(r"x\cw_alpha_harvest\xmodel.txt")));
        assert!(!is_table(Path::new(r"x\cw_name_work\loaded_assets.csv")));
        assert!(!is_table(Path::new(r"x\cw_name_work\logs\general.log")));
    }
}
