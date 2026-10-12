//! Derives image names from material names.
//!
//! An image is usually named for the material that uses it, with a map suffix on the end and a
//! different beginning: a material called `mc/mtl_wpn_t9_ak47_barrel` has images called
//! `i_wpn_t9_ak47_barrel_c`, `..._n`, `..._g` and so on. So the material tables, which are
//! published and complete, describe images that are not.
//!
//! That makes this a far narrower search than the general one. There is no scraping and no
//! guessing at what a name might be: the stem comes from a material known to exist, and the
//! ending comes from a table, which is asked for every ending it holds rather than only the
//! common ones. Both tables are read for endings, because an ending is an ending whichever kind
//! of asset it was seen on, and the material table holds two hundred thousand the image table
//! does not.

use slasher::loader::{loaded_assets, wanted_for_search};
use slasher::search::{candidate_space, run_best};
use slasher::fingerprint::{Fingerprint, Sketch};
use slasher::{futility, config, endings_of, paths, pool_label, readiness, recon, stamp, table_keys, table_names, tables_look_complete, Results, RunNote};

/// The tables the stems and the endings come from.
const MATERIALS: &str = "fnv1a_xmaterials";
const IMAGES: &str = "fnv1a_ximages";

/// The beginnings an image carries where its material carried something else. The empty one is
/// there because an image is as often the bare stem as the prefixed one.
const OPENINGS: &[&str] = &["i_", "", "i_mtl_", "mtl_", "c_", "i_c_"];

/// The beginnings stripped off a material name to leave the part the image shares, longest first
/// so the longest match is the one taken.
const STRIP: &[&str] = &["i_mtl_", "mtl_mtl_", "mtl_", "i_c_", "i_", "c_"];

/// Mesh entries cannot be named by any rule here: the tail of one is a hash of the mesh. They
/// are left out so that a candidate has half as many ids to land on by coincidence.
const UNREACHABLE: &[&str] = &["xmodelmesh"];

/// The parts of a material name an image might share, longest first.
///
/// A material is a path and carries a beginning the image does not: the directory goes, then
/// whichever of the known beginnings it starts with. Every step is kept, because which one the
/// image shares is not knowable in advance.
fn stems_of(name: &str) -> Vec<String> {
    let lowered = name.to_lowercase();
    let mut found: Vec<String> = Vec::new();

    let push = |value: &str, found: &mut Vec<String>| {
        if value.len() >= 4 && !found.iter().any(|held| held == value) {
            found.push(value.to_owned());
        }
    };

    push(&lowered, &mut found);

    let bare = match lowered.rsplit_once('/') {
        Some((_, rest)) => rest,
        None => &lowered,
    };
    push(bare, &mut found);

    // Past whichever beginning it has, then once more, since a doubled one occurs.
    let mut rest = bare;
    for _ in 0..2 {
        let mut stripped = rest;
        for opening in STRIP {
            if let Some(shorter) = rest.strip_prefix(opening) {
                if shorter.len() >= 4 {
                    stripped = shorter;
                    break;
                }
            }
        }

        if stripped == rest {
            break;
        }

        push(stripped, &mut found);
        rest = stripped;
    }

    found
}

/// How many slices the stems are cut into, and so how often the run folder is written.
///
/// Sixteen puts a checkpoint roughly every eight minutes on the one measured full run (8,096
/// seconds). Fewer would leave more on the floor when a pass is killed; many more would print a
/// planning line per slice for no gain, since the cost is linear either way.
const SLICES: usize = 16;

fn main() {
    readiness::require();
    futility::require();

    let began = std::time::Instant::now();
    let (assets, _) = match loaded_assets() {
        Ok(loaded) => loaded,
        Err(reason) => {
            eprintln!("{reason}");
            return;
        }
    };

    let known = table_keys();
    println!("hashes already resolved by the tables: {}", known.len());

    if !tables_look_complete(&known) {
        eprintln!("the tables read short. Check {}", paths::tables().display());
        return;
    }

    let wanted = wanted_for_search(&assets, &known, UNREACHABLE);
    println!("unnamed assets a name here could belong to: {}", wanted.len());
    drop(known);

    let endings = endings_of(&[IMAGES, MATERIALS]);
    println!("endings taken from both tables: {}", endings.len());

    // Every material known to exist: the published ones, the ones this search has found before,
    // and the ones the general search has found. A material no table holds is exactly the kind
    // whose images no table holds either.
    let mut results = Results::load(paths::findings());
    let mut materials = table_names(MATERIALS);
    println!("materials from the table: {}", materials.len());

    // One load, one extend. This used to load `paths::findings()` a second time under another
    // name and append the identical list again, so every confirmed material was cut into stems
    // twice: the printed stem count, the sizing, and `Fingerprint::with_count("stems", ..)` all
    // described an input twice the size of the real one, and the search did the duplicate work.
    let confirmed = results.names("material");
    println!("materials this machine has confirmed: {}", confirmed.len());
    materials.extend(confirmed);

    // Deduplicated across the whole corpus, not merely within one name.
    //
    // `stems_of` dedupes what a single name yields, but `mc/mtl_wpn_x` and `wc/mtl_wpn_x` both
    // give `mtl_wpn_x` and `wpn_x`. Measured over the material table: 1,586,979 stems for
    // 811,822 distinct ones, so 48.8% of them were repeats -- and the forward cost is
    // `stems x openings x (endings + 1)`, so roughly half of the 8,096-second measured run was
    // re-testing candidates it had already tested. It also made
    // `Fingerprint::with_count("stems", ..)` describe an input twice the real size.
    let mut stems: Vec<String> = materials.iter().flat_map(|name| stems_of(name)).collect();
    stems.sort_unstable();
    stems.dedup();
    println!("stems those materials offer: {}", stems.len());
    drop(materials);

    let openings: Vec<String> = OPENINGS.iter().map(|text| (*text).to_owned()).collect();

    // The stems go in by *content*. This method reopens whenever the material corpus grows --
    // METHODS.md calls it "productive after any material gain" -- so a fingerprint blind to the
    // materials would stop the run that a night of new materials had just made worth doing. What
    // it must not carry is a *count* of them, which says nothing about which materials they were
    // and differs on every machine; see the note at the top of `fingerprint.rs`.
    let fingerprint = Fingerprint::of("images_from_materials")
        .with("game", &config::game())
        .with_list("openings", &openings)
        .with_list("endings", &endings)
        .with_list("stems", &stems)
        .finish();
    println!("fingerprint: {fingerprint}");
    recon::warn_if_swept(&fingerprint);

    // Run in slices, so a kill does not cost the whole pass.
    //
    // This was the one confirming binary that wrote its run folder once, at the end. It is also
    // the longest: 8,096 seconds when it was first run to completion on 2026-08-21. A kill at two
    // hours left every name it had found on disk in a shape `submit` would never send -- the
    // silent loss the checkpointing in `confirm_cw` and `confirm_list` exists to prevent.
    //
    // Slicing rather than checkpointing inside the engine, because `Search` -- the forward
    // direction, and the one this takes -- hands each thread a chunk and joins at the end, so
    // there is no batch boundary to report from without restructuring its hot loop.
    //
    // Slicing is free *here* and would not be everywhere: the forward cost is
    // `stems x openings x (endings + 1)`, linear in stems, so N slices cost what one pass costs.
    // The peeling direction is not linear -- its `endings x wanted x PEEL_COST` term is paid per
    // call -- so slicing that would multiply the work. `run_best` prints which direction it chose;
    // this measured 4,347.6B forwards against 10,939.6B peeling, and the slices keep that ratio
    // because the peel term is fixed while the forward term shrinks with the slice.
    let when = stamp();
    let slices = SLICES.min(stems.len().max(1));
    let size = stems.len().div_ceil(slices).max(1);

    for (index, slice) in stems.chunks(size).enumerate() {
        println!("\nslice {}/{} -- {} stems", index + 1, stems.len().div_ceil(size), slice.len());

        for (id, name) in run_best(&openings, &endings, slice, &wanted, false) {
            results.add(&pool_label(wanted[&id]), id, name);
        }

        // The aggregate first, and this ordering matters more than it looks.
        //
        // A checkpointed run folder carries `.incomplete` until the pass seals it, and both
        // walks skip such a folder on purpose -- `run_folders` will not send a partial batch,
        // `every_run_folder` will not let one account for its own names. So mid-run the folder
        // is readable by no route at all, and the aggregate is the *only* copy `recover_stranded`
        // can find. Writing the folder first and the aggregate second leaves a window where a
        // kill loses the slice entirely: not sendable, not accounted, not strandable.
        //
        // Neither write gates the other, which was the real fault in the first version -- a
        // locked file or a full disk skipped the other write for the whole 8,000-second run.
        if let Err(error) = results.write(paths::findings()) {
            eprintln!("  the aggregate files could not be written: {error}");
        }

        match results.write_run_as(paths::findings(), "images", &when) {
            // `results.added()`, not `results.len()`: `Results::load` has already put every name
            // on disk into this, so `len()` prints a near-constant six-figure number that says
            // nothing about whether the slice saved anything.
            Ok(Some(_)) => println!("  checkpoint: {} name(s) from this run are safe", results.added()),
            Ok(None) => println!("  nothing found yet, so there is no run folder to write"),
            Err(error) => eprintln!("  the run folder could not be checkpointed: {error}"),
        }
    }

    println!("this run added {}", results.added());

    // Recorded whatever the outcome, including nothing: a run that finds nothing is a
    // real result, and three of them in a row is a loop. See `futility`.
    futility::record(results.added(),
        Some(candidate_space(openings.len(), endings.len(), stems.len(), false)));

    // Not `expect`. The loop above tolerates this write failing, and then the identical call
    // here panicked on it -- skipping `write_run_as`, `note_run` and `seal_run`, so the folder
    // kept its `.incomplete` marker for ever and the names came back later as an anonymous
    // recovered batch with no run note, if at all.
    if let Err(error) = results.write(paths::findings()) {
        eprintln!("the aggregate files could not be written: {error}");
    }

    match results.write_run_as(paths::findings(), "images", &when) {
        Ok(Some(folder)) => {
            println!("this run's own names: {}", folder.display());
            let _ = Results::note_run(
                &folder,
                &RunNote::new(
                    "images derived from materials (images_from_materials)",
                    "each confirmed material name stripped of mtl_ and retried as an image name \
                     with every semantic suffix, both prefixed and bare",
                    began.elapsed(),
                )
                .measured("game", config::game())
                .measured("openings", openings.len())
                .measured("endings", endings.len())
                .measured("stems", stems.len())
                .measured("ids hunted", wanted.len())
                // The whole product across every slice, which is what the run covered however
                // it was cut up. Same label as `confirm_list`, so the two can be ranked.
                .measured(
                    "candidates tested",
                    candidate_space(openings.len(), endings.len(), stems.len(), false),
                )
                .measured("new", results.added())
                // See `confirm_plan`: lets `scripts/overlap.py` say how much ground this run
                // shares with somebody else's, which a fingerprint cannot.
                .measured("sketch beginnings", Sketch::of(&openings))
                .measured("sketch stems", Sketch::of(&stems))
                .measured("sketch endings", Sketch::of(&endings))
                .fingerprint(&fingerprint),
            );

            // Written and noted, so it stops being a live run. Until this the folder carries
            // `.incomplete` and `submit` leaves it alone -- and if this pass is killed, it stays
            // marked and `recover_stranded` picks the names up instead.
            if let Err(error) = Results::seal_run(&folder) {
                eprintln!("the run folder could not be marked finished: {error}");
            }
        }
        Ok(None) => println!("this run found nothing new"),
        Err(error) => eprintln!("the run folder could not be written: {error}"),
    }
}
