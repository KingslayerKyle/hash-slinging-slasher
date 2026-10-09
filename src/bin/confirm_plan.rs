//! Runs a targeted search written as a short plan file, at the compiled engine's speed.
//!
//! This exists because of a measurement. `confirm_list` made inventing a method cheap -- a method
//! became a script that prints names -- and that was the right move and remains the right move.
//! But a generator printing names in Python tops out at about 2.6M candidates a second on this
//! machine, and the run record shows real generators managing 0.1M to 1.4M. The compiled engine
//! beside it covers tens of billions in a pass.
//!
//! The consequence, counted off `submissions/` on 2026-08-22: **every invented method ever run
//! here has tested 10.2 billion candidates between them, across 166 runs and every contributor.**
//! One general pass covers 103 trillion. So the half of this project that is supposed to be the
//! clever half has been running on a ten-thousandth of the machine, and the only method that
//! could use the engine was the one hard-coded shape nobody can retarget -- which was ground out
//! in the first two days and has been fingerprint-blocked ever since.
//!
//! A plan is the same three lists the engine already multiplies -- beginnings, stems, endings --
//! except that *you choose them*. Not every prefix in the game and every piece of every name, but
//! the eleven prefixes and the four hundred stems belonging to the family you are actually
//! hunting. That is the difference between a blind sweep and an aimed one, and the run record
//! puts aimed methods three orders of magnitude ahead: a derivation returns a name per few
//! hundred candidates, a blind sweep one per few million.
//!
//! ```text
//! confirm_plan plans/zombie_bodies.txt
//! confirm_plan plans/zombie_bodies.txt --game BLKOPS04
//! confirm_plan plans/zombie_bodies.txt --size      what it would cost, without running it
//! ```
//!
//! ## The plan format
//!
//! One `key: value` per line, `#` starts a comment, and the three list keys may repeat. A value
//! beginning with `@` is a file to read one-per-line; anything else is a literal.
//!
//! ```text
//! label: zombie character bodies
//! describe: the eleven body prefixes against confirmed zombie cores
//!
//! begin: @data/prefixes.txt      # every measured beginning
//! begin: i_                      # and one written here
//! stem:  @contrib/zombie_cores.txt
//! end:   @data/suffixes.txt
//!
//! bare: yes      # is the stem alone, with no beginning and no ending, a candidate
//! fold: yes      # no for Black Ops 4 SAB sound names, which keep their backslashes
//! ```
//!
//! Nothing here is a new engine. It is `run_best` -- the same peeling search, the same hash, the
//! same exclusion, the same run folder and fingerprint -- pointed where somebody decided to point
//! it rather than where it was compiled to look.

use std::path::{Path, PathBuf};
use std::time::Instant;

use slasher::fingerprint::{Fingerprint, Sketch};
use slasher::loader::{loaded_assets, wanted_for_search};
use slasher::search::{candidate_space, run_best_with_backend_checkpointed};
use slasher::gpu;
use slasher::{futility, 
    config, paths, pool_label, readiness, recon, stamp, table_keys, tables_look_complete, Results,
    RunNote,
};

/// Pools no rule can reach; the same set every other search excludes. See `confirm_list`.
const UNREACHABLE: &[&str] = &["xmodelmesh"];

/// How many pieces a pass is cut into before it writes what it has found.
///
/// The forward cost is linear in stems, so slicing is free in that direction; the peeling
/// direction pays its `endings x wanted` term per call, so a plan that peels is better off in few
/// slices. Eight is the compromise `images_from_materials` settled on for the same reason: a kill
/// costs at most an eighth of the pass rather than all of it.
const SLICES: usize = 8;

/// One plan, read off disk.
#[derive(Default)]
struct Plan {
    label: String,
    describe: String,
    beginnings: Vec<String>,
    stems: Vec<String>,
    endings: Vec<String>,
    bare: bool,
    fold: bool,
    game: Option<String>,
}

/// What a plan line asked for, or why it could not be honoured.
fn values_of(value: &str, base: &Path) -> Result<Vec<String>, String> {
    let Some(path) = value.strip_prefix('@') else {
        return Ok(vec![value.to_owned()]);
    };

    // Relative to the repository root, so a plan reads the same wherever it is run from. A plan
    // that only works from one directory is a plan that fails at 3am on somebody else's machine.
    let path = base.join(path.trim());
    let text = std::fs::read_to_string(&path)
        .map_err(|error| format!("{} could not be read: {error}", path.display()))?;

    let table=path.file_stem().and_then(|s|s.to_str()).unwrap_or("");
    let database_csv=path.extension().and_then(|s|s.to_str())==Some("csv") && table.starts_with("fnv1a_");
    let lines: Vec<String> = if database_csv { slasher::database::names(table,&text) } else { text
        .lines()
        .map(|line| line.trim())
        .filter(|line| !line.is_empty() && !line.starts_with('#'))
        // A `hash,name` line is accepted and the name taken, exactly as `confirm_list` does, so a
        // findings file can be used as a stem list without being reshaped first.
        .map(|line| line.split_once(',').map_or(line, |(_, name)| name.trim()).to_owned())
        .collect() };

    if lines.is_empty() {
        return Err(format!("{} held no usable lines", path.display()));
    }

    Ok(lines)
}

fn read_plan(path: &Path) -> Result<Plan, String> {
    let text = std::fs::read_to_string(path)
        .map_err(|error| format!("{} could not be read: {error}", path.display()))?;

    let root = paths::root();
    let mut plan = Plan { bare: true, fold: true, ..Plan::default() };

    for (number, line) in text.lines().enumerate() {
        let line = line.split('#').next().unwrap_or("").trim();
        if line.is_empty() {
            continue;
        }

        let Some((key, value)) = line.split_once(':') else {
            return Err(format!(
                "{}:{}: `{line}` is not `key: value`. Keys are label, describe, begin, stem, end, \
                 bare, fold and game.",
                path.display(),
                number + 1
            ));
        };

        let value = value.trim();
        match key.trim().to_ascii_lowercase().as_str() {
            "label" => plan.label = value.to_owned(),
            "describe" => plan.describe = value.to_owned(),
            "begin" => plan.beginnings.extend(values_of(value, &root)?),
            "stem" => plan.stems.extend(values_of(value, &root)?),
            "end" => plan.endings.extend(values_of(value, &root)?),
            "bare" => plan.bare = matches!(value.to_ascii_lowercase().as_str(), "yes" | "true" | "1"),
            "fold" => plan.fold = matches!(value.to_ascii_lowercase().as_str(), "yes" | "true" | "1"),
            "game" => plan.game = Some(value.to_ascii_uppercase()),
            other => {
                return Err(format!(
                    "{}:{}: `{other}` is not a plan key. Keys are label, describe, begin, stem, \
                     end, bare, fold and game.",
                    path.display(),
                    number + 1
                ))
            }
        }
    }

    if plan.label.is_empty() {
        return Err(format!(
            "{} has no `label:`. The label is what the run notes carry and what \
             `methods_report.py` groups by, so a run without one cannot be told from any other.",
            path.display()
        ));
    }

    if plan.stems.is_empty() {
        return Err(format!(
            "{} has no `stem:` lines, so there is nothing to search. A plan needs stems; \
             beginnings and endings are both optional.",
            path.display()
        ));
    }

    // Deduplicated, because the cost is a product: a stem list holding the same stem twice does
    // the whole beginnings-by-endings cross product twice for it, and a findings file concatenated
    // with a table is full of repeats. Measured on the material corpus elsewhere in this
    // repository: 48.8% of stems were duplicates.
    for list in [&mut plan.beginnings, &mut plan.stems, &mut plan.endings] {
        list.sort_unstable();
        list.dedup();
    }

    Ok(plan)
}

fn main() {
    let mut arguments: Vec<String> = std::env::args().skip(1).collect();
    if arguments.iter().any(|argument| argument == "--help" || argument == "-h") {
        usage();
        return;
    }
    let (backend, gpu_check) = gpu::parse_backend_options(&mut arguments).unwrap_or_else(|reason| {
        eprintln!("{reason}");
        std::process::exit(2);
    });
    if gpu_check {
        if !arguments.is_empty() {
            eprintln!("--gpu-check is a standalone diagnostic; omit plan, game, and search arguments.");
            std::process::exit(2);
        }
        match gpu::probe(backend.device) {
            Ok(device) => {
                println!("{device}");
                println!("CUDA support check passed. --backend auto also checks workload cost before selecting the GPU.");
            }
            Err(reason) => {
                eprintln!("{reason}\nCPU searches remain available. See docs/GPU.md for setup and build instructions.");
                std::process::exit(1);
            }
        }
        return;
    }
    let path = plan_path(&arguments).unwrap_or_else(|reason| {
        eprintln!("{reason}");
        usage();
        std::process::exit(2);
    });
    readiness::require();
    futility::require();
    let began = Instant::now();

    let size_only = arguments.iter().any(|argument| argument == "--size");

    let plan = match read_plan(&path) {
        Ok(plan) => plan,
        Err(reason) => {
            eprintln!("{reason}");
            std::process::exit(1);
        }
    };

    // A plan's `game:` line checks rather than sets. `config::game()` reads `--game` out of the
    // command line itself and is the one place that decides, so a second route to the same
    // setting would be a second answer to it.
    //
    // Checking still matters, and more than it looks: a plan whose stems are one game's confirmed
    // names is meaningless against the other's ids, and it fails *silently* -- a full pass that
    // simply finds nothing, which reads exactly like a spent method. Refusing costs a re-run with
    // one flag; not refusing costs the pass.
    let active = config::game();
    if let Some(pinned) = &plan.game {
        if *pinned != active {
            eprintln!(
                "{} is a plan for {pinned}, and this run is against {active}.\n\n\
                 A plan's stems belong to the game they came from, so running it against the \
                 other finds\nnothing and looks like an exhausted method rather than a mistake. \
                 Run it as:\n\n    confirm_plan {} --game {pinned}",
                path.display(),
                path.display()
            );
            std::process::exit(2);
        }
    }

    println!("plan: {}", plan.label);
    println!(
        "  {} beginning(s), {} stem(s), {} ending(s), bare {}, fold {}",
        plan.beginnings.len(),
        plan.stems.len(),
        plan.endings.len(),
        if plan.bare { "yes" } else { "no" },
        if plan.fold { "yes" } else { "no" }
    );

    let candidates =
        candidate_space(plan.beginnings.len(), plan.endings.len(), plan.stems.len(), plan.bare);
    println!("  candidates: {candidates}");

    // A plan that asks nothing, refused before it looks like a spent method.
    //
    // The engine takes its opening count as `beginnings + bare`, so a plan with neither has no
    // column to iterate and tests not one candidate. It does not fail: it runs, finds nothing,
    // writes a note, and reads exactly like ground somebody has already cleared. That happened --
    // a 31,747,647,770-candidate plan scanned zero in six seconds and exited reporting success.
    if candidates == 0 {
        eprintln!(
            "\nThis plan would test nothing, so it has not been run.\n\n\
             It has no `begin:` lines and `bare: no`, and the search builds its candidates as\n\
             beginning + stem + ending -- with no beginning and the bare stem excluded there is\n\
             nothing left to build. Either add a beginning, or set `bare: yes`, which is the\n\
             empty beginning and is what a stem-and-ending plan wants."
        );
        std::process::exit(2);
    }

    if !plan.fold {
        println!("  hashing without folding backslashes (Black Ops 4 SAB sound names)");
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

    println!(
        "names expected to match by chance at this size: {:.4}",
        slasher::expected_by_chance(candidates, wanted.len())
    );

    if size_only {
        println!("\n--size given, so nothing was searched and nothing was written.");
        return;
    }

    // By content, never by count. A plan reopens whenever its lists change, and a fingerprint
    // carrying only how many stems there were would say two entirely different plans of the same
    // size were the same search -- and would differ between machines for one plan whose stems
    // come from the local findings. See the note at the top of `fingerprint.rs`.
    let fingerprint = Fingerprint::of("confirm_plan")
        .with("game", &config::game())
        .with("label", &plan.label)
        .with("fold", if plan.fold { "yes" } else { "no" })
        .with("bare", if plan.bare { "yes" } else { "no" })
        .with_list("beginnings", &plan.beginnings)
        .with_list("stems", &plan.stems)
        .with_list("endings", &plan.endings)
        .finish();
    println!("fingerprint: {fingerprint}");
    recon::warn_if_swept(&fingerprint);

    let mut results = Results::load(paths::findings());
    if !plan.fold {
        results = results.keeping_spelling();
    }

    let when = stamp();
    // Optional backends choose against the complete workload, then checkpoint bounded
    // batches internally. Pre-slicing would disguise a useful GPU job as tiny CPU jobs.
    let slices = if backend.backend == gpu::Backend::Cpu {
        SLICES.min(plan.stems.len().max(1))
    } else {
        1
    };
    let size = plan.stems.len().div_ceil(slices).max(1);
    let mut last_saved = Instant::now();
    gpu::reset_usage();

    for (index, slice) in plan.stems.chunks(size).enumerate() {
        println!(
            "\nslice {}/{} -- {} stems",
            index + 1,
            plan.stems.len().div_ceil(size),
            slice.len()
        );

        run_best_with_backend_checkpointed(
            &plan.beginnings, &plan.endings, slice, &wanted, plan.bare, plan.fold, &backend,
            &mut |batch| {
                for (id, name) in batch {
                    results.add(&pool_label(wanted[id]), *id, name.clone());
                }
                if last_saved.elapsed().as_secs() >= 60 {
                    last_saved = Instant::now();
                    if let Err(error) = results.write(paths::findings()) {
                        eprintln!("  the aggregate files could not be checkpointed: {error}");
                    }
                    if let Err(error) = results.write_run_as(paths::findings(), "plan", &when) {
                        eprintln!("  the run folder could not be checkpointed: {error}");
                    }
                }
            },
        ).unwrap_or_else(|reason| {
            if let Err(error) = results.write(paths::findings()) {
                eprintln!("could not save verified results: {error}");
            }
            if let Err(error) = results.write_run_as(paths::findings(), "plan", &when) {
                eprintln!("could not save the incomplete run: {error}");
            }
            eprintln!("search failed: {reason}\nEarlier verified batches were checkpointed; this run is incomplete.");
            std::process::exit(1);
        });

        // The aggregate first, then the run folder. A checkpointed folder carries `.incomplete`
        // and is skipped by every walk until it is sealed, so between the two writes the
        // aggregate is the only copy a recovery could find. See `images_from_materials`, where
        // getting this ordering wrong lost a slice outright.
        if let Err(error) = results.write(paths::findings()) {
            eprintln!("  the aggregate files could not be written: {error}");
        }

        match results.write_run_as(paths::findings(), "plan", &when) {
            Ok(Some(_)) => println!("  checkpoint: {} name(s) from this run are safe", results.added()),
            Ok(None) => println!("  nothing found yet, so there is no run folder to write"),
            Err(error) => eprintln!("  the run folder could not be checkpointed: {error}"),
        }
    }

    println!("\nthis run added {}", results.added());

    // Recorded whatever the outcome, including nothing: a run that finds nothing is a
    // real result, and three of them in a row is a loop. See `futility`.
    futility::record(results.added());


    if let Err(error) = results.write(paths::findings()) {
        eprintln!("the aggregate files could not be written: {error}");
    }

    match results.write_run_as(paths::findings(), "plan", &when) {
        Ok(Some(folder)) => {
            println!("this run's own names: {}", folder.display());

            let describe = if plan.describe.is_empty() {
                "a targeted beginning + stem + ending search, with all three lists chosen by the \
                 plan rather than measured from the whole corpus"
                    .to_owned()
            } else {
                plan.describe.clone()
            };

            let _ = Results::note_run(
                &folder,
                &RunNote::new(plan.label.clone(), describe, began.elapsed())
                    .computed_on(gpu::usage_summary())
                    .measured("game", config::game())
                    .measured("beginnings", plan.beginnings.len())
                    .measured("endings", plan.endings.len())
                    .measured("stems", plan.stems.len())
                    .measured("ids hunted", wanted.len())
                    // Spelled as `confirm_list` spells it, because `methods_report.py` ranks the
                    // two against each other and a method that does not record this cannot be
                    // compared with one that does.
                    .measured("candidates tested", candidates)
                    .measured("new", results.added())
                    // Not a fingerprint, and it must never block a run. The fingerprint says
                    // "identical or not", which is blind to the commoner waste: a plan sharing
                    // nine tenths of its stems with one somebody ran last night. These let the
                    // next person measure that before spending the hour -- see
                    // `scripts/overlap.py`.
                    .measured("sketch beginnings", Sketch::of(&plan.beginnings))
                    .measured("sketch stems", Sketch::of(&plan.stems))
                    .measured("sketch endings", Sketch::of(&plan.endings))
                    .fingerprint(&fingerprint)
                    .next_step(
                        "a plan is spent at these three lists and no other. Change what it aims \
                         at -- a different family, a different pool's stems, the endings that pool \
                         actually wears -- rather than widening it: widening is what turned the \
                         general search into a method everybody runs and nobody gains from. \
                         `scripts/seams.py` says which relations are worth aiming at.",
                    ),
            );

            if let Err(error) = Results::seal_run(&folder) {
                eprintln!("the run folder could not be marked finished: {error}");
            }
        }
        Ok(None) => println!("this run found nothing new"),
        Err(error) => eprintln!("the run folder could not be written: {error}"),
    }
}

fn usage() {
    println!(
        "usage: confirm_plan <plan file> [--game TAG] [--size]\n\
         [--backend cpu|auto|cuda] [--cuda-device N] [--gpu-min-candidates N]\n\
         confirm_plan --gpu-check [--cuda-device N]\n\n\
         CPU is the default. Auto checks support and workload cost before selecting CUDA.\n\
         --gpu-check checks support without searching; --size describes a plan without searching.\n\
         A plan contains label:, begin:, stem:, and end: lines; @path reads a factor list.\n\
         See plans/example.txt and docs/GPU.md."
    );
}

/// GPU flags and their values have already been removed by the shared parser.
fn plan_path(arguments: &[String]) -> Result<PathBuf, String> {
    let mut path = None;
    let mut args = arguments.iter();
    while let Some(argument) = args.next() {
        match argument.as_str() {
            "--game" => match args.next() {
                Some(value) if !value.starts_with('-') && !value.is_empty() => (),
                _ => return Err("--game requires a game tag".into()),
            },
            "--size" | "--anyway" => (),
            flag if flag.starts_with('-') => return Err(format!("unknown argument: {flag}")),
            value if !value.is_empty() && path.is_none() => path = Some(PathBuf::from(value)),
            other => return Err(format!("unexpected argument: {other}")),
        }
    }
    path.ok_or_else(|| "a plan file is required".into())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn backend_and_game_values_cannot_be_mistaken_for_a_plan() {
        let mut args: Vec<String> = ["--game", "BLACKOP7", "--backend", "auto", "--cuda-device", "0",
            "--gpu-min-candidates", "100000000", "plans/example.txt", "--size"]
            .iter().map(|value| (*value).into()).collect();
        let (options, check) = gpu::parse_backend_options(&mut args).unwrap();
        assert_eq!(options.backend, gpu::Backend::Auto);
        assert!(!check);
        assert_eq!(plan_path(&args).unwrap(), PathBuf::from("plans/example.txt"));
    }

    #[test]
    fn malformed_plan_arguments_are_rejected_before_searching() {
        for args in [vec!["--game"], vec!["--game", "--size"], vec!["one", "two"],
            vec!["--backned", "cuda", "one"], vec!["--size"]] {
            assert!(plan_path(&args.into_iter().map(String::from).collect::<Vec<_>>()).is_err());
        }
    }

    fn plan_from(text: &str) -> Result<Plan, String> {
        let path = std::env::temp_dir().join(format!("plan_{}_{}.txt", std::process::id(), text.len()));
        std::fs::write(&path, text).expect("a temporary plan");
        let read = read_plan(&path);
        let _ = std::fs::remove_file(&path);
        read
    }

    /// The three lists are what the search multiplies, so a plan that reads them wrongly does not
    /// fail -- it searches somewhere else and reports success. Every part of the format is pinned.
    #[test]
    fn a_plan_reads_its_three_lists() {
        let plan = plan_from(
            "# a comment\n\
             label: zombie bodies\n\
             describe: the eleven body prefixes\n\
             begin: i_\n\
             begin: mc/\n\
             stem: wpn_ak47\n\
             stem: wpn_m16\n\
             end: _c   # trailing comments are not part of the value\n\
             bare: no\n\
             fold: no\n\
             game: blkops04\n",
        )
        .expect("a plan that parses");

        assert_eq!(plan.label, "zombie bodies");
        assert_eq!(plan.describe, "the eleven body prefixes");
        assert_eq!(plan.beginnings, vec!["i_".to_owned(), "mc/".to_owned()]);
        assert_eq!(plan.stems, vec!["wpn_ak47".to_owned(), "wpn_m16".to_owned()]);
        assert_eq!(plan.endings, vec!["_c".to_owned()], "a trailing comment must not join the value");
        assert!(!plan.bare);
        assert!(!plan.fold);
        assert_eq!(plan.game.as_deref(), Some("BLKOPS04"));
    }

    /// `bare` and `fold` default to yes, which is what every pool but Black Ops 4's SAB sounds
    /// wants. Defaulting `fold` the other way would match nothing, for ever, while looking healthy.
    #[test]
    fn the_defaults_are_what_most_pools_want() {
        let plan = plan_from("label: x\nstem: wpn_ak47\n").expect("a minimal plan");
        assert!(plan.bare);
        assert!(plan.fold);
        assert!(plan.beginnings.is_empty());
        assert!(plan.endings.is_empty());
    }

    /// A plan with no stems searches nothing, and a plan with no label cannot be told from any
    /// other run in the report. Both are refused rather than run.
    #[test]
    fn a_plan_that_could_not_search_is_refused() {
        assert!(plan_from("label: x\n").is_err(), "no stems");
        assert!(plan_from("stem: wpn_ak47\n").is_err(), "no label");
        assert!(plan_from("label: x\nstem: a\nnonsense\n").is_err(), "not key: value");
        assert!(plan_from("label: x\nstem: a\nwrong: 1\n").is_err(), "unknown key");
    }

    /// Duplicate entries are removed, because the cost is a product: one repeated stem does the
    /// whole beginnings-by-endings cross product twice for nothing.
    #[test]
    fn the_lists_are_deduplicated() {
        let plan = plan_from("label: x\nstem: a_bcd\nstem: a_bcd\nbegin: i_\nbegin: i_\n")
            .expect("a plan that parses");
        assert_eq!(plan.stems, vec!["a_bcd".to_owned()]);
        assert_eq!(plan.beginnings, vec!["i_".to_owned()]);
    }

    /// An `@file` is read one name per line, and a `hash,name` line gives up its name -- so a
    /// findings file is usable as a stem list without being reshaped first.
    #[test]
    fn an_at_file_is_read_as_a_list() {
        let folder = paths::root();
        let name = format!("plan_list_{}.txt", std::process::id());
        let path = folder.join(&name);
        std::fs::write(&path, "# comment\nwpn_ak47\n1234abcd,wpn_m16\n\n").expect("a list file");

        let plan = plan_from(&format!("label: x\nstem: @{name}\n"));
        let _ = std::fs::remove_file(&path);

        let plan = plan.expect("a plan that parses");
        assert_eq!(plan.stems, vec!["wpn_ak47".to_owned(), "wpn_m16".to_owned()]);
    }
}
