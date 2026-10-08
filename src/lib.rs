//! The pieces every search here shares: the hash, the lookup, the tables and the result files.
//!
//! Recovering a Call of Duty asset name is two halves. Harvesting produces candidate strings,
//! from a build's own files or from the names that are already published. Confirming hashes
//! those candidates and looks for the result among the assets the loader is holding, which turns
//! a guess into a fact: a match means the game itself refers to that name.
//!
//! What every search then has in common is this module. The hash has to be the game's, computed
//! the game's way. The lookup has to answer hundreds of billions of times, so it is a filter
//! before it is a map. And a result is only worth keeping if it is written somewhere a previous
//! run cannot be undone by.

use std::collections::{HashMap, HashSet};
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};

pub mod loader;
pub mod config;
pub mod disk;
pub mod github;
pub mod tables;
pub mod database;
pub mod paths;
pub mod snapshot;
pub mod search;

// Everything that has to happen before a search, and the gate that makes it happen. Kept
// together because they are one idea: a night is wasted by a stale clone far more often than by
// a bad method, so freshness is enforced by a program rather than asked for in prose.
pub mod update;
pub mod recon;
pub mod futility;
pub mod readiness;
pub mod startup;
pub mod fingerprint;

// Reading the loader's memory to capture a snapshot. Only whoever owns the game needs this, and
// it is the only Windows-only part of the crate, so it is behind a feature that is off by
// default. Grinding against a captured snapshot needs none of it.
#[cfg(feature = "cordycep")]
pub mod cordycep;
#[cfg(feature = "cordycep")]
pub mod memory;

/// The hash the tools use: FNV-1a, 64 bit.
pub mod games;

pub const BASIS: u64 = 0xCBF2_9CE4_8422_2325;
pub const PRIME: u64 = 0x0000_0100_0000_01B3;

/// Every id the loader hands out has bit 63 clear, so a name matches under one spelling only.
/// Narrowing further loses real matches and invents collisions.
pub const ID_MASK: u64 = 0x7FFF_FFFF_FFFF_FFFF;

/// The only game these pool indexes and tables describe.
pub const GAME: &str = "BLKOPSCW";

/// Pools that are large, easy to hit, and worth nothing -- with the reason, so that the next
/// person to be tempted by one can see what it cost the last person.
///
/// These are not merely "not the priority". Each has been searched, and each produced a large
/// number of genuine hashes that nobody has any use for. The point of naming them here rather
/// than only in the documentation is that a program can refuse, and prose cannot.
///
/// They are also, not coincidentally, the biggest pools in both games -- `streamkey` alone is
/// 420,229 ids in Cold War and 292,133 in Black Ops 4, more than any nameable type. Anything
/// that opens up "every pool" lands here first and hardest.
pub const LOW_VALUE_POOLS: &[(&str, &str)] = &[
    (
        "streamkey",
        "the largest pool in both games and the emptiest. One pass produced ~290,000 genuine \
         hashes, overwhelmingly sequential terrain entries like \
         `maps/mp/mp_apocalypse.d3dbsp_s1__terrain_l01_n000079` -- real names describing nothing \
         anybody needs. They also bury the useful findings in the same results folder.",
    ),
    (
        "localizeentry",
        "a localize entry is a 16-byte struct holding a pointer to its own *unhashed* string, so \
         the plain text is already in the build. No published table holds one of these names \
         because recovering them proves nothing. 8,667 were confirmed in a single twenty-minute \
         pass, all worthless.",
    ),
    (
        "localize_entry",
        "the Black Ops 4 spelling of `localizeentry`, and worthless for the same reason.",
    ),
    (
        "xmodelmesh",
        "structurally unreachable: a mesh name is `<model>_s1_geo_rigid_bs_` plus twenty-six \
         characters of base32 that are a hash of the mesh itself. No rule can produce it, and \
         leaving these ids in the wanted set roughly doubles what a candidate can land on by \
         coincidence.",
    ),
];

/// Why a name does not look like its pool's convention -- **without claiming it is wrong**.
///
/// A match proves a string hashes to an id the game holds. It does **not** prove the string is
/// that asset's name -- with ~136,000 wanted ids and a hundred trillion candidates a pass, one or
/// two coincidences are expected, and every binary prints the figure it expects. Until now
/// nothing acted on that: a coincidence was written to disk and submitted like any other find.
///
/// One turned up on the first widened pass:
/// `survival/operators/beck/vox_beck_se_kill_mult_nightingale_01.rn75.pc.ea_item`, filed as an
/// `xmodel` in both games. Everything about it said coincidence -- the sound-encoding path, the
/// tail that is not a valid sound tail, an id that is a genuine model with the usual `xcollision`
/// and `xskeleton` beside it.
///
/// **It was checked in Saluki and it is the model's real name.** Somebody at Treyarch pasted a
/// sound path onto a model. So the rule this function encodes is *not* "reject": rejecting would
/// have thrown away a verified name, which is the one thing this project must never do. What an
/// odd shape is actually good for is deciding what to *learn* from -- a sound path taken as an
/// xmodel convention would teach every later candidate a shape the game does not use.
///
/// The rule is deliberately narrow, and it is measured rather than assumed. Across the published
/// tables: **1,414,269 xmodel, image, material and xanim names carry no `.rn75.`/`.ln75.` tail
/// between them -- not one -- while 1,485,904 sound names do.** So the tail is a sound name's
/// signature, and one on anything else is worth flagging -- never rejecting. Reproduce with:
///
/// ```text
/// cd cod-name-db/csv
/// cut -d, -f2- fnv1a_xmodels.csv | grep -cE '\.(rn|ln)75\.'      # 0
/// cat fnv1a_*xsounds.csv | cut -d, -f2- | grep -cE '\.(rn|ln)75\.'  # 1485904
/// ```
///
/// Nothing else is guessed at here, and nothing is ever rejected on it.
pub fn odd_for_pool(pool: &str, name: &str) -> Option<String> {
    let sound = matches!(pool, "sound" | "sound_asset" | "sound_bank" | "sound_duck");

    if !sound && (name.contains(".rn75.") || name.contains(".ln75.")) {
        return Some(format!(
            "carries a sound name's `.rn75.`/`.ln75.` tail but is filed as `{pool}`, which no \
             published xmodel, image, material or xanim does. Kept and submitted -- one such name \
             is verified real, a sound path pasted onto a model by mistake -- but held back from \
             the seed corpus, because learning a convention from somebody's slip would aim every \
             later candidate wrongly."
        ));
    }

    None
}

/// Why this pool is not worth searching, if it is one of the ones that is not.
pub fn low_value_reason(pool: &str) -> Option<&'static str> {
    LOW_VALUE_POOLS
        .iter()
        .find(|(name, _)| *name == pool)
        .map(|(_, reason)| *reason)
}

/// Cold War's asset types, by pool index -- the whole `BO5XAssetType` enum, since Cold War is
/// "Black Ops 5" internally. Index 18 being the sound bank pool is what first confirmed the
/// ordering; index 184 being `streamkey` is what identified the largest unnamed pool in the game.
pub const POOLS: &[&str] = &[
    "zone", "assetlist", "physpreset", "physconstraints", "destructibledef", "xanim", "xmodel",
    "xcollision", "xskeleton", "xmodelmesh", "material", "csdef", "computeshaderset", "rtsdef",
    "raytraceshaderset", "techset", "image", "sound", "sound_bank", "sound_asset", "sound_duck",
    "sound_alias_modifier", "sound_acoustics", "col_map", "clip_map", "com_map", "game_map",
    "gfx_map", "fonticon", "localizeentry", "gesture", "gesturetable", "cinematicmotion", "weapon",
    "weaponfull", "weaponfrontend", "weaponblueprint", "weaponstylesettings",
    "weaponsecondarymovement", "weapontunables", "cgmediatable", "playersoundstable",
    "playerfxtable", "sharedweaponsounds", "attachment", "attachmentunique", "weaponcamo",
    "weaponcamobinding", "customizationtable", "customizationtablefrontend", "snddriverglobals",
    "fx", "tagfx", "klf", "impactsfxtable", "impactsoundstable", "aitype", "character",
    "xmodelalias", "rawfile", "rawfilepreproc", "rawtextfile", "animtree", "stringtable",
    "structuredtable", "leaderboarddef", "ddl", "glasses", "scriptparsetree", "scriptparsetreedbg",
    "script_using", "script_using_cp", "script_using_mp", "script_using_wz", "script_using_zm",
    "keyvaluepairs", "vehicle", "tracer", "surfacefxtable", "surfacesounddef", "footsteptable",
    "entityfximpacts", "entitysoundimpacts", "zbarrier", "vehiclefxdef", "vehiclesounddef",
    "typeinfo", "scriptbundle", "scriptbundlelist", "rumble", "bulletpenetration", "locdmgtable",
    "aimtable", "shoottable", "playerglobaltunables", "overheadcameratunables", "animselectortable",
    "animmappingtable", "animstatemachine", "behaviortree", "behaviorstatemachine", "ttf", "sanim",
    "shellshock", "statuseffect", "cinematic_camera", "cinematic_sequence", "spectate_camera",
    "xcam", "bgcache", "flametable", "bitfield", "maptable", "maptableentry", "maptablelist",
    "objective", "objectivelist", "navmesh", "navvolume", "laser", "beam", "streamerhint",
    "flowgraph", "postfxbundle", "luafile", "luafiledebug", "renderoverridebundle",
    "staticlevelfxlist", "triggerlist", "playerroletemplate", "playerroletemplatefrontend",
    "playerrolecategorytable", "playerrolecategory", "characterbodytype",
    "characterbodytypefrontend", "playeroutfit", "gametypetable", "gametypetableentry", "feature",
    "featuretable", "unlockableitem", "unlockableitemtable", "entitylist", "playlists",
    "playlistglobalsettings", "playlistschedule", "motionmatchinginput", "blackboard",
    "tacticalquery", "playermovementtunables", "hierarchicaltasknetwork", "ragdoll", "storagefile",
    "storagefilelist", "charmixer", "storeproduct", "storecategory", "storecategorylist", "rank",
    "ranktable", "prestige", "prestigetable", "firstpartyentitlement", "firstpartyentitlementlist",
    "entitlement", "entitlementlist", "sku", "labelstore", "labelstorelist", "cpu_occlusion_data",
    "lighting", "districts", "streamerworld", "talent", "playertalenttemplate", "playeranimation",
    "unused", "terraingfx", "highlightreelinfodefines", "highlightreelprofileweighting",
    "highlightreelstarlevels", "dlogevent", "rawstring", "ballisticdesc", "streamkey",
    "rendertargets", "drawnodes", "grouplodmodel", "fxlibraryvolume", "arenaseasons",
    "sprayorgestureitem", "sprayorgesturelist", "hwplatform", "attachmenttable", "navinput",
    "uimodeldatastruct", "crafticon", "crafticonlist", "craftweaponsticker",
    "craftweaponstickerlist", "craftbackground", "craftbackgroundlist", "craftmaterial",
    "craftmateriallist", "craftcategory", "craftcategorylist", "craftweaponicontransform",
    "craftweaponicontransformlist", "xanimcurve", "dynmodel", "vectorfield", "winddef",
    "vehicleassembly", "milestone", "milestonetable", "triggereffectdesc", "triggeractions",
    "playersettings", "compasstunables", "execution", "scenario",
    // Appended past the real enum, like `sound_asset`, and for the same reason: sound *aliases*
    // are not loader assets. They live inside the bank assets, as arrays of records whose names
    // these games store only as hashes -- so no pool of the game's own holds them, and nothing in
    // a capture could.
    //
    // Worth having: `fnv1a_soundbanks_aliases.csv` upstream already names 33,289, and the two
    // games hold 93,663 between them. The ids were read out of the live loader with Amadeus,
    // which is the reader that knows those record layouts.
    "sound_alias",
];

/// Black Ops 4's asset types, by pool index. A different enum entirely -- xmodel is 6 in Cold
/// War and 4 here -- which is why a find has to be labelled against the game it was found in
/// rather than against whichever list happens to be compiled in.
pub const BO4_POOLS: &[&str] = &[
    "physpreset", "physconstraints", "destructibledef", "xanim", "xmodel", "xmodelmesh", "material",
    "compute_shader_set", "technique_set", "image", "sound", "clipmap", "comworld", "gameworld",
    "gfxworld", "fonticon", "localize_entry", "localize_list", "gesture", "gesture_table", "weapon",
    "weapon_full", "weapon_tunables", "cgmedia", "playersounds", "playerfx", "sharedweaponsounds",
    "attachment", "attachment_unique", "weapon_camo", "customization_table",
    "customization_table_fe_images", "snddriver_globals", "fx", "tagfx", "klf", "impact_fx",
    "impact_sound", "aitype", "character", "xmodelalias", "rawfile", "xanim_tree", "stringtable",
    "structured_table", "leaderboard", "ddl", "glasses", "scriptparsetree", "scriptparsetreedbg",
    "scriptparsetreeforced", "keyvaluepairs", "vehicledef", "tracer", "surfacefx_table",
    "surfacesounddef", "footstep_table", "entityfximpacts", "entitysoundimpacts", "zbarrier",
    "vehiclefxdef", "vehiclesounddef", "typeinfo", "scriptbundle", "scriptbundlelist", "rumble",
    "bulletpenetration", "locdmgtable", "aimtable", "shoottable", "playerglobaltunables",
    "animselectortableset", "animmappingtable", "animstatemachine", "behaviortree",
    "behaviorstatemachine", "ttf", "sanim", "light_description", "shellshock", "status_effect",
    "cinematic_camera", "cinematic_sequence", "spectate_camera", "xcam", "bg_cache",
    "texture_combo", "flametable", "bitfield", "maptable", "maptable_list",
    "maptable_loading_images", "maptable_preview_images", "maptableentry_level_assets", "objective",
    "objective_list", "navmesh", "navvolume", "laser", "beam", "streamer_hint", "flowgraph",
    "postfxbundle", "luafile", "luafile_dbg", "renderoverridebundle", "static_level_fx_list",
    "trigger_list", "player_role_template", "player_role_category_table", "player_role_category",
    "character_body_type", "player_outfit", "gametypetable", "feature", "featuretable",
    "unlockable_item", "unlockable_item_table", "entity_list", "playlists",
    "playlist_global_settings", "playlist_schedule", "motion_matching_input", "blackboard",
    "tacticalquery", "player_movement_tunables", "hierarchical_task_network", "ragdoll",
    "storagefile", "storagefilelist", "charmixer", "storeproduct", "storecategory",
    "storecategorylist", "rank", "ranktable", "prestige", "prestigetable", "firstpartyentitlement",
    "firstpartyentitlementlist", "entitlement", "entitlementlist", "sku", "labelstore",
    "labelstorelist", "cpu_occlusion_data", "lighting", "streamerworld", "talent",
    "playertalenttemplate", "playeranimation", "err_unused", "terraingfx",
    "highlightreelinfodefines", "highlightreelprofileweighting", "highlightreelstarlevels",
    "dlogevent", "rawstring", "ballisticdesc", "streamkey", "rendertargets", "drawnodes",
    "grouplodmodel", "fxlibraryvolume", "arenaseasons", "sprayorgestureitem", "sprayorgesturelist",
    "hwplatform", "assetlist", "report",
    // Index 170, past the end of the real enum, and deliberately so.
    //
    // Black Ops 4's own `sound` pool at index 10 holds sound **banks** -- the one entry of its
    // hundred that resolves is `mp_embassy.all`, out of `fnv1a_soundbanks_v2.csv`. The individual
    // sounds are not loader assets at all: they live inside SAB files that Cordycep never opens,
    // which is why that pool has a hundred entries and not eighty thousand.
    //
    // Those SAB entries can be added to a snapshot, and when they are they need a type of their
    // own. Filing them under `sound` would mix bank names and file names in one results file, and
    // the two go to *different* tables upstream -- banks to `fnv1a_soundbanks`, files to
    // `fnv1a_xsounds`. Whoever copies a submission into cod-name-db could not tell them apart.
    //
    // The name is Cold War's, because Cold War already draws exactly this distinction:
    // `sound_bank` at 18 for the banks, `sound_asset` at 19 for the files. Same split, same words.
    "sound_asset",
    // Index 171. **Order matters here and cannot be changed.** The snapshot already carries
    // 79,263 ids filed as pool 170, so anything inserted ahead of `sound_asset` silently relabels
    // every one of them as something else.
    // Appended past the real enum, like `sound_asset`, and for the same reason: sound *aliases*
    // are not loader assets. They live inside the bank assets, as arrays of records whose names
    // these games store only as hashes -- so no pool of the game's own holds them, and nothing in
    // a capture could.
    //
    // Worth having: `fnv1a_soundbanks_aliases.csv` upstream already names 33,289, and the two
    // games hold 93,663 between them. The ids were read out of the live loader with Amadeus,
    // which is the reader that knows those record layouts.
    "sound_alias",
];

/// The pool names for the game being ground.
pub fn pools() -> &'static [&'static str] {
    pools_for(&config::game())
}

/// The pool names for a named game.
///
/// Wanted wherever the game is known from something better than the configuration -- a snapshot's
/// own tag, or whatever the loader has open. Labelling one game's pool index out of the other's
/// enum has now produced three separate wrong answers in this codebase, each stated with complete
/// confidence, because index 5 is `xanim` in Cold War and `xmodelmesh` in Black Ops 4 and both
/// look perfectly reasonable in a log.
pub fn pools_for(game: &str) -> &'static [&'static str] {
    match game {
        "BLKOPS04" => BO4_POOLS,
        "BLKOPSCW" => POOLS,
        game if games::modern(game) => games::pools_for(game),
        other => panic!("unsupported game {other}"),
    }
}

/// What to file a find in this pool under.
///
/// The asset type when the pool numbering is known to apply to the game being ground, and
/// `pool_NNN` when it is not. A name filed under the wrong type is wrong to publish even though
/// the name itself is right, and `validate` rejects it -- so an unknown numbering says so rather
/// than guessing.
pub fn pool_label(index: usize) -> String {
    match pools().get(index) {
        Some(name) => games::canonical(name).to_owned(),
        None => format!("pool_{index}"),
    }
}

/// Which pool index an asset type name is, if it is one of them.
/// The same asset type under the name the other game gives it.
///
/// The two games name several types differently, and a search asks for a type by *string*: the
/// config says `sound_asset`, and `wanted_for_search` drops anything `pool_index` cannot resolve.
/// Without this, switching to Black Ops 4 silently hunts nothing for those types -- the pool looks
/// empty because it was never asked for, which is the worst way for this to fail.
///
/// Differences that are only underscores are handled by comparison rather than listed here. These
/// are the ones where the games genuinely chose different words. Black Ops 4 has no separate
/// `sound_asset` at all, so it falls back to its one `sound` pool.
const ALIASES: &[&[&str]] = &[
    &["sound_asset", "sound", "sndasset"],
    &["com_map", "comworld"],
    &["game_map", "gameworld"],
    &["gfx_map", "gfxworld"],
    &["techset", "technique_set"],
    &["animtree", "xanim_tree"],
];

/// Which pool index an asset type name is, in the game being ground.
///
/// Tried three ways, most exact first: the name as given, the name ignoring underscores, and then
/// the name the other game uses for the same thing.
pub fn pool_index(kind: &str) -> Option<usize> {
    pool_index_in(pools(), kind)
}

/// The same lookup against a named table rather than the game being ground.
///
/// Split out so it can be tested. `pool_index` reads which game is configured, and a test that
/// goes through it is a test whose answer depends on this machine's settings -- which is exactly
/// how one here started failing the moment the game stopped always being Cold War.
pub fn pool_index_in(table: &'static [&'static str], kind: &str) -> Option<usize> {

    if let Some(found) = table.iter().position(|pool| *pool == kind) {
        return Some(found);
    }

    let flattened = |name: &str| name.replace('_', "");
    if let Some(found) = table.iter().position(|pool| flattened(pool) == flattened(kind)) {
        return Some(found);
    }

    for group in ALIASES {
        if !group.contains(&kind) {
            continue;
        }

        for other in *group {
            if let Some(found) = table.iter().position(|pool| pool == other) {
                return Some(found);
            }
        }
    }

    None
}

/// The hash, taken as a fold rather than over a whole string.
///
/// A candidate is a beginning, a stem and an ending. Folding lets the beginning be hashed once
/// for a whole run and the stem once per beginning, so an ending costs only the few bytes it is
/// long. That is the difference between five million candidates a second and a billion.
///
/// The name is normalised as it goes: lower cased, and backslash folded to forward slash.
/// Missing that normalisation makes everything fail to match.
#[inline(always)]
pub fn feed(hash: u64, text: &[u8]) -> u64 {
    feed_with::<true>(hash, text)
}

/// The same fold, leaving backslashes alone.
///
/// **One table needs this, and getting it wrong costs the entire search.** Black Ops 4's sound
/// entries live in SAB files and are named with literal backslashes, and their ids are the hash
/// of exactly that. Measured against the 8,385 of them cod-name-db already names: **8,385
/// reproduce without folding, 0 with it.** Every other table folds harmlessly, because its names
/// already use forward slashes and the fold is a no-op there.
///
/// A search that hashes those candidates the ordinary way matches nothing at all, for ever, while
/// looking exactly like ordinary unnamed work — which is the most expensive way for this project
/// to be wrong.
#[inline(always)]
pub fn feed_raw(hash: u64, text: &[u8]) -> u64 {
    feed_with::<false>(hash, text)
}

/// The fold, with the normalisation chosen at compile time.
///
/// A const parameter rather than a runtime flag: this runs hundreds of billions of times a pass,
/// and a branch per byte would be paid on every candidate in the project for the sake of the one
/// table that wants the other behaviour.
#[inline(always)]
pub fn feed_with<const FOLD: bool>(mut hash: u64, text: &[u8]) -> u64 {
    for &byte in text {
        let byte = match byte {
            b'A'..=b'Z' => byte + 32,
            b'\\' if FOLD => b'/',
            other => other,
        };

        hash ^= byte as u64;
        hash = hash.wrapping_mul(PRIME);
    }

    hash
}

/// The inverse of the prime, modulo 2^64. The prime is odd, so it has one.
///
/// This is what makes the hash reversible: a byte fed in can be taken back out again, exactly.
pub const PRIME_INVERSE: u64 = {
    // Newton's method doubles the number of correct bits each time, so six rounds from a
    // three-bit seed is more than the sixty four needed.
    let mut inverse: u64 = 1;
    let mut round = 0;
    while round < 6 {
        inverse = inverse.wrapping_mul(2u64.wrapping_sub(PRIME.wrapping_mul(inverse)));
        round += 1;
    }
    inverse
};

/// Takes a known ending back off a hash, giving the hash the name had before it.
///
/// The forward step is `h = (h ^ byte) * prime`, so the backward one is
/// `h = (h * prime_inverse) ^ byte`, walking the bytes in reverse. It is exact, not a guess.
///
/// This is what lets a search cost the sum of its lists rather than the product. Instead of
/// hashing every stem with every ending, each ending is peeled off each wanted id once, and what
/// is left is the hash the stem alone would have to reach. A thousand endings then cost one pass
/// over the wanted ids rather than a thousand passes over the stems.
#[inline(always)]
pub fn peel(hash: u64, text: &[u8]) -> u64 {
    peel_with::<true>(hash, text)
}

/// Peeling that matches [`feed_raw`], for the one table whose names keep their backslashes.
#[inline(always)]
pub fn peel_raw(hash: u64, text: &[u8]) -> u64 {
    peel_with::<false>(hash, text)
}

#[inline(always)]
pub fn peel_with<const FOLD: bool>(mut hash: u64, text: &[u8]) -> u64 {
    for &byte in text.iter().rev() {
        let byte = match byte {
            b'A'..=b'Z' => byte + 32,
            b'\\' if FOLD => b'/',
            other => other,
        };

        hash = hash.wrapping_mul(PRIME_INVERSE) ^ byte as u64;
    }

    hash
}

/// The hash of a whole name.
pub fn hash64(text: &str) -> u64 {
    feed(BASIS, text.as_bytes())
}

/// The hash of a whole name, keeping its backslashes. See [`feed_raw`].
pub fn hash64_raw(text: &str) -> u64 {
    feed_raw(BASIS, text.as_bytes())
}

/// The hash of a name as the loader would hold it.
pub fn id_of(text: &str) -> u64 {
    hash64(text) & ID_MASK
}

/// How the two stages are sized, in bits of the id each is indexed by.
const COARSE_BITS: u32 = 24;
const FINE_BITS: u32 = 26;

/// A membership test over the ids still unnamed, in two stages.
///
/// Nearly every candidate is a miss, so the first question asked of one has to be cheap. Both
/// stages are bitmaps read at disjoint parts of the id, which makes them independent: a miss
/// usually stops at the small one, which stays in cache, and only a few candidates in ten
/// thousand ever reach the map behind it.
pub struct Filter {
    coarse: Vec<u64>,
    fine: Vec<u64>,
    coarse_bits: u32,
    fine_bits: u32,
}

impl Filter {
    pub fn new<'a>(ids: impl Iterator<Item = &'a u64>) -> Self {
        Self::with_bits(ids, COARSE_BITS, FINE_BITS)
    }

    /// A filter sized for how much is going into it.
    ///
    /// A bitmap holding far more entries than it has bits says yes to everything, which costs
    /// the whole point of having one. Half a dozen bits per entry keeps the first stage a real
    /// question, and the second stage is given the same again.
    pub fn sized<'a>(ids: impl Iterator<Item = &'a u64> + Clone, count: usize) -> Self {
        let wanted = (count.max(1) * 8).next_power_of_two().trailing_zeros();
        let bits = wanted.clamp(COARSE_BITS, 32);

        Self::with_bits(ids, bits, bits.min(30))
    }

    fn with_bits<'a>(ids: impl Iterator<Item = &'a u64>, coarse_bits: u32, fine_bits: u32) -> Self {
        let mut filter = Self {
            coarse: vec![0; 1 << (coarse_bits - 6)],
            fine: vec![0; 1 << (fine_bits - 6)],
            coarse_bits,
            fine_bits,
        };

        for id in ids {
            let (coarse, fine) = filter.slots(*id);
            filter.coarse[coarse >> 6] |= 1 << (coarse & 63);
            filter.fine[fine >> 6] |= 1 << (fine & 63);
        }

        filter
    }

    #[inline(always)]
    fn slots(&self, id: u64) -> (usize, usize) {
        let coarse = id & ((1 << self.coarse_bits) - 1);
        let fine = (id >> self.coarse_bits) & ((1 << self.fine_bits) - 1);

        (coarse as usize, fine as usize)
    }

    #[inline(always)]
    pub fn may_hold(&self, id: u64) -> bool {
        let (coarse, fine) = self.slots(id);

        if self.coarse[coarse >> 6] & (1 << (coarse & 63)) == 0 {
            return false;
        }

        self.fine[fine >> 6] & (1 << (fine & 63)) != 0
    }
}

/// One 'hash,name' file, as pairs.
pub fn read_rows(path: &Path) -> Vec<(u64, String)> {
    fs::read_to_string(path)
        .unwrap_or_default()
        .lines()
        .filter_map(|line| {
            let (key, name) = line.trim().split_once(',')?;
            Some((
                u64::from_str_radix(key.trim(), 16).ok()? & ID_MASK,
                name.to_owned(),
            ))
        })
        .collect()
}

/// The names out of a 'hash,name' file, or the plain lines of one that is not.
pub fn read_names(path: &Path) -> Vec<String> {
    if path.extension().and_then(|s|s.to_str()) == Some("csv") {
        let table=path.file_stem().and_then(|s|s.to_str()).unwrap_or("");
        if table.starts_with("fnv1a_") {
            return database::names(table,&fs::read_to_string(path).unwrap_or_default());
        }
    }
    fs::read_to_string(path)
        .unwrap_or_default()
        .lines()
        .map(|line| {
            let line = line.trim();
            match line.split_once(',') {
                Some((key, name)) if u64::from_str_radix(key, 16).is_ok() => name.to_owned(),
                _ => line.to_owned(),
            }
        })
        .filter(|line| !line.is_empty())
        .collect()
}

/// Every line of every text file in a folder.
pub fn folder_names(directory: impl AsRef<Path>) -> Vec<String> {
    let directory = directory.as_ref();
    let mut names = Vec::new();

    let Ok(entries) = fs::read_dir(directory) else {
        return names;
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) == Some("txt") {
            names.extend(read_names(&path));
        }
    }

    names
}

/// One line per item, which is how the generated lists are stored.
pub fn read_list(path: &Path) -> Vec<String> {
    fs::read_to_string(path)
        .unwrap_or_else(|error| panic!("{} could not be read: {error}", path.display()))
        .lines()
        .map(str::trim)
        .filter(|line| !line.is_empty())
        .map(str::to_owned)
        .collect()
}

/// The names one table holds.
pub fn table_names(table: &str) -> Vec<String> {
    let path = tables::csv_folder(&paths::tables()).join(format!("{table}.csv"));
    database::names(table, &fs::read_to_string(path).unwrap_or_default())
}

/// Every name every table holds.
///
/// A newer game's table teaches the wrong conventions and must never be measured for the lists,
/// but that is a different question from whether its names are worth cutting into pieces. Cold
/// War carries a great deal of the games either side of it, reading a table costs one pass over
/// a file, and missing a name costs the name -- so all of them are read here.
pub fn all_table_names() -> Vec<String> {
    let mut names = Vec::new();

    let Ok(entries) = fs::read_dir(tables::csv_folder(&paths::tables())) else {
        return names;
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) == Some("csv") {
            names.extend(table_names(path.file_stem().and_then(|s| s.to_str()).unwrap_or("")));
        }
    }

    names
}

/// Every hash any table already resolves.
///
/// Every table is read, including the newer games', because a name any of them resolves is not a
/// new find whoever it belongs to. Both the stored key and the hash of the stored name are taken,
/// since a table can hold one at a different width from the other.
pub fn table_keys() -> HashSet<u64> {
    database_keys(&tables::csv_folder(&paths::tables()), &config::game())
}

/// Stored keys always exclude known assets. Rehashed names must first reproduce their source key.
pub fn database_keys(folder: &Path, game: &str) -> HashSet<u64> {
    let mut known = HashSet::new();
    let Ok(entries) = fs::read_dir(folder) else { return known; };
    for entry in entries.flatten() {
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) != Some("csv") { continue; }
        let table = path.file_stem().and_then(|s| s.to_str()).unwrap_or("");
        if games::modern(game) && !games::MODERN_TABLES.contains(&table) { continue; }
        let Ok(text) = fs::read_to_string(&path) else { continue; };
        for row in text.lines() {
            let Some((key,display)) = row.split_once(',') else { continue; };
            let Ok(key) = u64::from_str_radix(key.trim(),16) else { continue; };
            known.extend([key,key & ID_MASK]);
            if let Some((full,_)) = database::verified_row(table,key,display) {
                known.extend([full,full & ID_MASK]);
            }
        }
    }
    known
}

/// Whether a set of table hashes is big enough to be the real thing.
///
/// Without the tables every loaded asset looks unnamed, and a search would report a few million
/// already published names as though they were finds. A short read means the tables moved, not
/// that the game got bigger.
pub fn tables_look_complete(known: &HashSet<u64>) -> bool {
    known.len() >= 1_000_000
}

/// Every ending a table's names carry: one, two and three trailing segments, all of them.
///
/// No threshold, deliberately. Where a search is narrow enough to afford the whole set, a
/// threshold would drop exactly the unusual endings that a published table cannot already name.
pub fn endings_of(tables: &[&str]) -> Vec<String> {
    let mut endings: HashSet<String> = HashSet::new();

    for table in tables {
        for name in table_names(table) {
            let name = name.to_lowercase();
            let marks: Vec<usize> = name
                .bytes()
                .enumerate()
                .filter(|(_, byte)| *byte == b'_')
                .map(|(index, _)| index)
                .collect();

            for depth in 1..=3 {
                if marks.len() >= depth {
                    let at = marks[marks.len() - depth];
                    if at + 1 < name.len() {
                        endings.insert(name[at..].to_owned());
                    }
                }
            }
        }
    }

    endings.into_iter().collect()
}

/// Results held as a file per asset type, each a list of 'hash,name'.
///
/// Loaded, added to, and written back. A run can only ever add: what a previous run wrote is
/// already in the map that gets written out, so a rule change that no longer reaches an old name
/// does not take it away. Getting this wrong once silently replaced a whole result set, which is
/// why it is one type with one way in.
/// A duration the way people write them: `2h 14m 09s`, `14m 09s`, `42s`.
pub fn human_duration(duration: std::time::Duration) -> String {
    let seconds = duration.as_secs();
    let (hours, minutes, seconds) = (seconds / 3600, (seconds % 3600) / 60, seconds % 60);

    if hours > 0 {
        format!("{hours}h {minutes:02}m {seconds:02}s")
    } else if minutes > 0 {
        format!("{minutes}m {seconds:02}s")
    } else {
        format!("{seconds}s")
    }
}

/// What a run has to say for itself, beyond the names it found.
///
/// A submission that says only "430 names" teaches the next contributor nothing, and this
/// project's whole advantage is supposed to be that each night starts further along than the
/// last. So a run records what it *was*: the method, the inputs, what those inputs measured, how
/// much ground it covered, and the fingerprint that lets the next person recognise the same
/// search and go and do a different one instead.
///
/// Everything here ends up in the pull request. Keep it to things a later reader can act on.
pub struct RunNote {
    method: String,
    what: String,
    took: std::time::Duration,

    /// Which operating system and architecture the run happened on.
    ///
    /// Recorded because the project now ships binaries for three platforms but has only ever been
    /// *run* on one. Tests passing on Linux and macOS in CI is not the same as somebody grinding
    /// there -- a path assumption or a `gh` invocation could be wrong on either and no test would
    /// notice. This is how that stops being a guess: count the submissions per platform.
    platform: String,

    /// Which engine actually did the confirming: `CPU`, or a GPU backend once one exists.
    ///
    /// Recorded per run and carried into the submission, so that if a GPU backend is ever found to
    /// have a fault, the batches it produced can be identified and re-checked without guessing.
    /// Provenance is cheap to write now and impossible to reconstruct later.
    compute: String,
    fingerprint: Option<String>,
    measurements: Vec<(String, String)>,
    next: Option<String>,
}

impl RunNote {
    pub fn new(method: impl Into<String>, what: impl Into<String>, took: std::time::Duration) -> Self {
        Self {
            method: method.into(),
            what: what.into(),
            took,
            platform: format!("{} {}", std::env::consts::OS, std::env::consts::ARCH),
            compute: "CPU".to_owned(),
            fingerprint: None,
            measurements: Vec::new(),
            next: None,
        }
    }

    /// Which engine confirmed these names. Defaults to `CPU`; a GPU backend sets it explicitly.
    pub fn computed_on(mut self, backend: impl Into<String>) -> Self {
        self.compute = backend.into();
        self
    }

    /// The digest of everything that decided what this pass would find. See `fingerprint`.
    pub fn fingerprint(mut self, value: impl Into<String>) -> Self {
        self.fingerprint = Some(value.into());
        self
    }

    /// A number worth carrying: candidates, seeds, throughput, how much was already known.
    pub fn measured(mut self, label: impl Into<String>, value: impl std::fmt::Display) -> Self {
        self.measurements.push((label.into(), value.to_string()));
        self
    }

    /// What the person who reads this should try next, in one sentence.
    pub fn next_step(mut self, value: impl Into<String>) -> Self {
        self.next = Some(value.into());
        self
    }

    fn render(&self) -> String {
        let mut text = format!(
            "- method: {}\n- what it does: {}\n- ran for: {}\n- platform: {}\n\
             - confirmed on: {}\n",
            self.method,
            self.what,
            human_duration(self.took),
            self.platform,
            self.compute
        );

        for (label, value) in &self.measurements {
            text.push_str(&format!("- {label}: {value}\n"));
        }

        // Last, and in exactly this spelling: `recon` reads it back out of a pull request diff to
        // warn the next contributor off a search that has already been run to exhaustion.
        if let Some(fingerprint) = &self.fingerprint {
            text.push_str(&format!("- fingerprint: {fingerprint}\n"));
        }

        if let Some(next) = &self.next {
            text.push_str(&format!("\n**Next:** {next}\n"));
        }

        text
    }
}

#[derive(Default)]
pub struct Results {
    by_kind: HashMap<String, HashMap<u64, String>>,
    before: HashMap<String, usize>,
    added: HashMap<String, HashMap<u64, String>>,

    /// Whether to leave a name spelled exactly as the search hashed it.
    ///
    /// Almost always true, and for those pools the two spellings reach the same asset, so a name
    /// is written in the spelling the published tables use. **Black Ops 4's SAB sound names are
    /// the exception, and it is not cosmetic:** their ids are the hash of the string *with* its
    /// backslashes, so rewriting them as forward slashes leaves a row whose name no longer
    /// produces its own id. Three submissions went out that way -- 37 rows nothing downstream can
    /// verify or use, because a table keyed on the name resolves it to a different hash entirely.
    ///
    /// Phrased as "keep" rather than "fold" so that `Default` -- which is `false`, and which the
    /// tests and any future caller get for free -- means *fold*, the behaviour every pool but one
    /// wants. Named the other way round, forgetting to set it would quietly disable folding
    /// everywhere, and a wrong default that fails silently is how this bug happened once already.
    keep_spelling: bool,
}

/// The file a run folder carries while it is still being written to. See `write_run_as`.
pub const INCOMPLETE: &str = ".incomplete";

impl Results {
    /// Reads whatever is already in a folder, and in the per-run folders under it.
    ///
    /// A run writes what it found on its own into `run_<when>`, so that what is new is a folder
    /// rather than a diff. Every one of them is read back here, because the question a run asks
    /// is whether a name is new to *all* of them.
    pub fn load(directory: impl AsRef<Path>) -> Self {
        let directory = directory.as_ref();
        let mut by_kind: HashMap<String, HashMap<u64, String>> = HashMap::new();

        let mut folders = vec![PathBuf::from(directory)];

        if let Ok(entries) = fs::read_dir(directory) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.is_dir() {
                    folders.push(path);
                }
            }
        }

        for folder in folders {
            let Ok(entries) = fs::read_dir(&folder) else {
                continue;
            };

            for entry in entries.flatten() {
                let path = entry.path();
                if path.extension().and_then(|e| e.to_str()) != Some("txt") {
                    continue;
                }

                let Some(kind) = path.file_stem().and_then(|s| s.to_str()) else {
                    continue;
                };

                by_kind
                    .entry(kind.to_owned())
                    .or_default()
                    .extend(read_rows(&path));
            }
        }

        let before = by_kind
            .iter()
            .map(|(kind, rows)| (kind.clone(), rows.len()))
            .collect();

        Self {
            by_kind,
            before,
            added: HashMap::new(),
            keep_spelling: false,
        }
    }

    /// Keeps names exactly as the search spelled them, for a run whose hash did not fold.
    ///
    /// Call this on any `--no-fold` run. The default is to fold, because every pool but Black Ops
    /// 4's SAB sounds wants it and a wrong default there would be silent -- a folded name still
    /// hashes to the right id when the hash itself folds, so nothing would ever complain.
    pub fn keeping_spelling(mut self) -> Self {
        self.keep_spelling = true;
        self
    }

    /// Every id already held, whatever type it is filed under.
    pub fn ids(&self) -> HashSet<u64> {
        self.by_kind
            .values()
            .flat_map(|rows| rows.keys().map(|id| id & ID_MASK))
            .collect()
    }

    /// Every name held, whatever type it is filed under.
    ///
    /// These are proven patterns, so they go back in as seeds: each one suggests siblings the
    /// same rules can now reach.
    pub fn all_names(&self) -> Vec<String> {
        self.by_kind
            .values()
            .flat_map(|rows| rows.values().cloned())
            .collect()
    }

    /// The same, minus anything whose shape would teach a later pass the wrong convention.
    ///
    /// A confirmed name is kept forever and submitted; that is not in question. But it is also
    /// fed back in as raw material, and a real-but-unrepresentative name is actively harmful
    /// there -- one xmodel genuinely called `.../vox_....rn75.pc.ea_item` would put a whole sound
    /// path into the xmodel vocabulary and spend the next pass building candidates from it.
    /// Keep the name, decline the lesson.
    pub fn seed_names(&self) -> Vec<String> {
        self.by_kind
            .iter()
            .flat_map(|(kind, rows)| {
                rows.values().filter(move |name| odd_for_pool(kind, name).is_none()).cloned()
            })
            .collect()
    }

    /// The names held under one type.
    pub fn names(&self, kind: &str) -> Vec<String> {
        self.by_kind
            .get(kind)
            .map(|rows| rows.values().cloned().collect())
            .unwrap_or_default()
    }

    pub fn len(&self) -> usize {
        self.by_kind.values().map(HashMap::len).sum()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn kinds(&self) -> usize {
        self.by_kind.len()
    }

    /// Adds a name, keeping the first spelling that reached an id.
    ///
    /// A name already held is not an addition, however it was arrived at, so a run's own folder
    /// stays a list of what that run was the first to reach.
    pub fn add(&mut self, kind: &str, id: u64, name: String) {
        // A scraped line may separate its directories with backslashes. Where the hash folded
        // them, both spellings reach the same asset and only one is the spelling the published
        // tables use, so that is the one written down.
        //
        // Where the hash did *not* fold -- `--no-fold`, which is the only way Black Ops 4's SAB
        // sound names are reachable at all -- the backslashes are load-bearing: the id is the hash
        // of exactly that string. Rewriting them here produced rows whose name does not hash to
        // the id beside it, which is worse than finding nothing, because it looks like a find.
        // See `Results::keeping_spelling`.
        let name = if !self.keep_spelling && name.contains('\\') {
            name.replace('\\', "/")
        } else {
            name
        };

        // Kept, and flagged. An earlier version discarded these as coincidences, and the very
        // first one it caught turned out -- checked in Saluki -- to be the model's real name: a
        // sound path somebody at Treyarch pasted onto a model. Results only ever grow, and that
        // rule outranks any heuristic about what a name ought to look like. The flag exists so a
        // human glances at it, and so `seed_names` declines to learn from it.
        if let Some(why) = odd_for_pool(kind, &name) {
            println!("  unusual, kept: {id:x},{name}\n    {why}");
        }

        let game = config::game();
        let id = if games::modern(&game) && kind == "sound_alias" {
            let expected = games::output_key(&game, kind, &name, !self.keep_spelling);
            assert_eq!(expected & ID_MASK, id & ID_MASK, "alias name does not reproduce captured id");
            expected
        } else { id };
        let rows = self.by_kind.entry(kind.to_owned()).or_default();

        if rows.contains_key(&id) {
            return;
        }

        rows.insert(id, name.clone());
        self.added
            .entry(kind.to_owned())
            .or_default()
            .insert(id, name);
    }

    /// What this run added, and nothing else.
    pub fn added(&self) -> usize {
        self.added.values().map(HashMap::len).sum()
    }

    /// Writes only what this run found, into a folder of its own named for when it ran.
    ///
    /// The merged set says what is known; this says what is new, which is what gets submitted.
    /// Nothing is written at all when a run found nothing, because an empty folder per barren
    /// pass buries the ones that were not.
    pub fn write_run(&self, directory: impl AsRef<Path>, label: &str) -> std::io::Result<Option<PathBuf>> {
        let written = self.write_run_as(directory, label, &stamp())?;

        // A one-shot write is finished the moment it returns, so it seals itself. Only a
        // checkpointing caller has to say when it is done.
        if let Some(folder) = &written {
            Self::seal_run(folder)?;
        }

        Ok(written)
    }

    /// The same, into a folder named for a stamp the caller keeps, so it can be written *during*
    /// a run rather than only at the end.
    ///
    /// This is what makes an interrupted run recoverable, and the gap it closes was silent and
    /// expensive. A pass checkpoints its names to the aggregate files every sixty seconds, but the
    /// run folder was written once, at the end -- and `submit` only ever sends run folders. So an
    /// agent killed mid-pass (a usage limit, a closed laptop) left its findings on disk in a shape
    /// nothing would ever send. Worse, silently: the next session's `submit` reports "nothing new
    /// to submit" and looks like success.
    ///
    /// Called repeatedly with the same stamp it rewrites the same folder, and since `added` only
    /// grows, the folder only grows with it.
    pub fn write_run_as(
        &self,
        directory: impl AsRef<Path>,
        label: &str,
        when: &str,
    ) -> std::io::Result<Option<PathBuf>> {
        let directory = directory.as_ref();
        if self.added.is_empty() {
            return Ok(None);
        }

        let folder = PathBuf::from(directory).join(format!("run_{when}_{label}"));
        fs::create_dir_all(&folder)?;

        // Marked unfinished until the caller seals it. `submit` decides what to send by looking
        // for `run_*` folders, so before this the folder's *existence* was the only signal a run
        // had ended -- and a checkpoint made that signal appear sixty seconds in. A `submit`
        // running meanwhile sent the partial batch and wrote the folder's name into its ledger,
        // after which `already_sent` skipped it for ever and every name the pass went on to find
        // was unreachable: `recover_stranded` will not strand a name that sits in a run folder.
        // The names stayed on disk, valid and unsubmittable, which is the same silent loss the
        // checkpointing was added to prevent.
        //
        // Written every time rather than only on the first checkpoint, so a folder cannot be left
        // sealed by an earlier run of the same stamp.
        fs::write(
            folder.join(INCOMPLETE),
            "This run had not finished when this folder was last written.\n\
             `submit` skips a folder holding this file, and picks the names up as stranded\n\
             instead, so an abandoned run is still recovered. Removed when the run ends.\n",
        )?;

        let mut kinds: Vec<&String> = self.added.keys().collect();
        kinds.sort();

        for kind in kinds {
            let rows = &self.added[kind];

            let mut ordered: Vec<(&u64, &String)> = rows.iter().collect();
            ordered.sort_by(|a, b| a.1.to_lowercase().cmp(&b.1.to_lowercase()));

            let mut file = fs::File::create(folder.join(format!("{kind}.txt")))?;
            for (id, name) in &ordered {
                writeln!(file, "{id:x},{name}")?;
            }
        }

        Ok(Some(folder))
    }

    /// Marks a run folder finished, so `submit` will send it.
    ///
    /// Idempotent, and not an error when the marker is already gone -- a caller that seals twice,
    /// or seals a folder written before this existed, is not doing anything wrong.
    pub fn seal_run(folder: &Path) -> std::io::Result<()> {
        match fs::remove_file(folder.join(INCOMPLETE)) {
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(()),
            other => other,
        }
    }

    /// Whether a run folder is still being written to.
    pub fn run_unfinished(folder: &Path) -> bool {
        folder.join(INCOMPLETE).exists()
    }

    /// Writes a run's account of itself into its folder, and the submission carries it upstream.
    ///
    /// A `.md` rather than a `.txt`, because a submission gathers every `.txt` line in a run
    /// folder as a name, and the account of a run is not a name.
    pub fn note_run(folder: &Path, note: &RunNote) -> std::io::Result<()> {
        fs::write(folder.join("notes.md"), note.render())
    }

    /// Writes a file per type, sorted by name, and reports what each gained.
    pub fn write(&self, directory: impl AsRef<Path>) -> std::io::Result<()> {
        let directory = directory.as_ref();
        fs::create_dir_all(directory)?;

        println!("\n{:<24} {:>10} {:>10}", "type", "rows", "added");

        let mut kinds: Vec<&String> = self.by_kind.keys().collect();
        kinds.sort();

        let mut total = 0;
        let mut added_all = 0;

        for kind in kinds {
            let rows = &self.by_kind[kind];
            let added = rows.len() - self.before.get(kind).copied().unwrap_or(0);

            let mut ordered: Vec<(&u64, &String)> = rows.iter().collect();
            ordered.sort_by(|a, b| a.1.to_lowercase().cmp(&b.1.to_lowercase()));

            let path = PathBuf::from(directory).join(format!("{kind}.txt"));
            let mut file = fs::File::create(&path)?;
            for (id, name) in &ordered {
                writeln!(file, "{id:x},{name}")?;
            }

            total += rows.len();
            added_all += added;
            println!("{kind:<24} {:>10} {:>10}", rows.len(), added);
        }

        println!("\ntotal: {total} (this run added {added_all})");

        Ok(())
    }
}

/// A name with any trailing `stamp()` taken off: `xmodel_20260819-174052` to `xmodel`.
///
/// Lives here, beside the function that writes the stamp, because it has been got wrong before
/// and the two have to agree. `validate` used to strip only trailing runs of *pure digits*, which
/// matches nothing on a real filename -- the stamp has a dash in it -- so it read the asset type
/// of every submitted file as `xmodel_20260819-174052`, resolved that to no pool, and quietly
/// passed every name as untypeable. A second copy of the rule is how that happens twice.
///
/// Written as a trailing trim rather than a split on the first underscore, because plenty of pool
/// names carry one: `sound_asset` would otherwise come back as `sound`.
pub fn strip_stamp(stem: &str) -> &str {
    let mut cut = stem;

    while let Some((before, last)) = cut.rsplit_once('_') {
        let stamp_like = !last.is_empty()
            && last.bytes().all(|byte| byte.is_ascii_digit() || byte == b'-')
            && last.bytes().any(|byte| byte.is_ascii_digit());

        if !stamp_like {
            break;
        }

        cut = before;
    }

    cut
}

/// The moment a run started, as `yyyymmdd-hhmmss` in UTC, for naming the folder it writes.
///
/// Written out by hand rather than by pulling in a calendar crate, since the whole of what is
/// wanted is a name that sorts in the order the runs happened.
pub fn stamp() -> String {
    let seconds = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|since| since.as_secs())
        .unwrap_or(0);

    let (days, rest) = (seconds / 86_400, seconds % 86_400);
    let (hour, minute, second) = (rest / 3600, (rest % 3600) / 60, rest % 60);

    // Days since 1970 to a civil date, counting from March so a leap day lands at the end of a
    // four hundred year era rather than in the middle of one.
    let era_days = days as i64 + 719_468;
    let era = era_days.div_euclid(146_097);
    let day_of_era = era_days.rem_euclid(146_097);
    let year_of_era =
        (day_of_era - day_of_era / 1460 + day_of_era / 36_524 - day_of_era / 146_096) / 365;
    let day_of_year = day_of_era - (365 * year_of_era + year_of_era / 4 - year_of_era / 100);
    let month_of = (5 * day_of_year + 2) / 153;

    let day = day_of_year - (153 * month_of + 2) / 5 + 1;
    let month = if month_of < 10 { month_of + 3 } else { month_of - 9 };
    let year = year_of_era + era * 400 + i64::from(month <= 2);

    format!("{year:04}{month:02}{day:02}-{hour:02}{minute:02}{second:02}")
}

/// What a run of this size is expected to match by coincidence rather than because the game has
/// the name. Worth printing: it is the one cost of widening the rules that does not show up as
/// time.
pub fn expected_by_chance(candidates: u64, wanted: usize) -> f64 {
    candidates as f64 * wanted as f64 / 9.223e18
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A checkpoint marks its folder unfinished; the end of the run clears it.
    ///
    /// This is the whole of the guard. `submit` decides what to send by looking for `run_*`
    /// folders, so once checkpointing made that folder appear sixty seconds into a pass, a
    /// `submit` running meanwhile sent the partial batch and ledgered the folder -- after which
    /// `already_sent` skipped it for ever and `recover_stranded` would not strand names sitting
    /// inside a run folder. Every name the pass went on to find was unreachable by both routes.
    #[test]
    fn a_checkpointed_run_is_marked_unfinished_until_it_ends() {
        let dir = std::env::temp_dir().join(format!("seal_{}", std::process::id()));
        let _ = fs::remove_dir_all(&dir);
        let _ = fs::create_dir_all(&dir);

        let mut results = Results::default();
        results.add("xmodel", 1, "one".to_owned());

        // A checkpoint, written mid-pass under a stamp fixed at the start.
        let folder = results
            .write_run_as(&dir, "all", "20260820-210000")
            .unwrap()
            .expect("a run folder");

        assert!(
            Results::run_unfinished(&folder),
            "a checkpointed run folder must say it is unfinished, or submit will send it              part-written and orphan everything the pass finds afterwards"
        );

        // A second checkpoint keeps it unfinished rather than accidentally sealing it.
        results.add("xmodel", 2, "two".to_owned());
        results.write_run_as(&dir, "all", "20260820-210000").unwrap();
        assert!(Results::run_unfinished(&folder), "a later checkpoint must not seal the folder");

        Results::seal_run(&folder).unwrap();
        assert!(!Results::run_unfinished(&folder), "sealing must clear the marker");

        // Sealing twice is not an error: a caller that seals a folder written before this
        // existed is not doing anything wrong.
        Results::seal_run(&folder).unwrap();

        let _ = fs::remove_dir_all(&dir);
    }

    /// A one-shot `write_run` seals itself, because it is finished the moment it returns.
    ///
    /// The binaries that do not checkpoint -- `confirm_sounds`, `confirm_variants`,
    /// `images_from_materials` and the rest -- go through this. If it did not seal, every one of
    /// their runs would look unfinished and `submit` would stop sending them entirely.
    #[test]
    fn a_one_shot_run_is_finished_when_it_is_written() {
        let dir = std::env::temp_dir().join(format!("seal_once_{}", std::process::id()));
        let _ = fs::remove_dir_all(&dir);
        let _ = fs::create_dir_all(&dir);

        let mut results = Results::default();
        results.add("image", 3, "three".to_owned());

        let folder = results.write_run(&dir, "sounds").unwrap().expect("a run folder");

        assert!(
            !Results::run_unfinished(&folder),
            "a one-shot run must be sendable immediately, or submit would never send one again"
        );

        let _ = fs::remove_dir_all(&dir);
    }

    /// A run note actually *writes* which engine confirmed it.
    ///
    /// The field existed, the builder existed, `submit` read it back -- and the format string in
    /// `render` was never updated, so the line was written nowhere and every submission reported
    /// "not recorded". It compiled, the tests passed, and the feature was dead. Nothing catches a
    /// missing line in a format string except asserting on the rendered text.
    #[test]
    fn a_run_note_records_which_engine_confirmed_it() {
        let note = RunNote::new("a method", "what it does", std::time::Duration::from_secs(1));
        assert!(note.render().contains("- confirmed on: CPU
"), "default backend not written");

        // The platform is recorded too, and it is the only way we will ever know whether anybody
        // actually grinds on Linux or macOS rather than merely compiling there.
        let rendered = note.render();
        assert!(
            rendered.contains(&format!("- platform: {} {}
", std::env::consts::OS, std::env::consts::ARCH)),
            "the platform was not written: {rendered}"
        );

        let gpu = RunNote::new("a method", "what it does", std::time::Duration::from_secs(1))
            .computed_on("GPU (OpenCL, gfx1100)");
        assert!(
            gpu.render().contains("- confirmed on: GPU (OpenCL, gfx1100)
"),
            "an explicit backend is not written"
        );
    }

    /// A stored name must reproduce the id stored beside it. That is the only thing a row means.
    ///
    /// Black Ops 4's SAB sound names are hashed *unfolded*, so their backslashes are part of the
    /// input. `add` used to rewrite them to forward slashes unconditionally, which left rows whose
    /// name hashes to something else entirely -- 37 of them reached three merged submissions
    /// before anything noticed, because every other pool folds and folding a folded name is a
    /// no-op. Nothing complained until `validate` re-derived them.
    #[test]
    fn an_unfolded_name_keeps_the_spelling_its_id_was_hashed_from() {
        let name = "fly\\emotes\\teddybear_in.ln100.pc.snd";
        let id = feed_raw(BASIS, name.as_bytes()) & ID_MASK;

        let folder = std::env::temp_dir().join(format!("keepspell_{}", std::process::id()));
        let _ = fs::remove_dir_all(&folder);
        fs::create_dir_all(&folder).unwrap();

        let mut kept = Results::load(&folder).keeping_spelling();
        kept.add("sound_asset", id, name.to_owned());

        let stored = kept.names("sound_asset");
        assert_eq!(stored, vec![name.to_owned()], "the spelling was rewritten");
        assert_eq!(
            feed_raw(BASIS, stored[0].as_bytes()) & ID_MASK,
            id,
            "a stored name must hash to the id stored beside it"
        );

        // And the default still tidies a scraped backslash away, which every folded pool wants.
        let mut folded = Results::load(&folder);
        folded.add("xmodel", 1, "a\\b".to_owned());
        assert_eq!(folded.names("xmodel"), vec!["a/b".to_owned()]);

        let _ = fs::remove_dir_all(&folder);
    }

    /// The five default types must resolve in **both** games, since both are ground now.
    ///
    /// Against the tables directly rather than through `pool_index`, which reads the configured
    /// game -- a test that goes through it passes or fails depending on this machine's settings,
    /// and one here duly started failing the day the game stopped always being Cold War.
    #[test]
    fn the_default_types_resolve_in_both_games() {
        for table in [POOLS, BO4_POOLS] {
            for kind in config::DEFAULT_POOLS {
                assert!(pool_index_in(table, kind).is_some(), "{kind} did not resolve");
            }
        }
    }

    /// Cold War must never be answered with an alias when it has the exact name itself.
    #[test]
    fn an_exact_name_wins_over_an_alias() {
        assert_eq!(pool_index_in(POOLS, "sound_asset"), Some(19), "sound_asset is 19, not 17");
        assert_eq!(pool_index_in(POOLS, "sound"), Some(17));
        assert_eq!(pool_index_in(POOLS, "xmodel"), Some(6));
        assert_eq!(pool_index_in(POOLS, "streamkey"), Some(184));
    }

    /// And the same five in Black Ops 4, where the numbering is different and `sound_asset` has
    /// to fall through to its one `sound` pool.
    #[test]
    fn the_black_ops_4_numbering_is_its_own() {
        assert_eq!(pool_index_in(BO4_POOLS, "xanim"), Some(3));
        assert_eq!(pool_index_in(BO4_POOLS, "xmodel"), Some(4));
        assert_eq!(pool_index_in(BO4_POOLS, "material"), Some(6));
        assert_eq!(pool_index_in(BO4_POOLS, "image"), Some(9));
        // 170, the SAB sound pool, not 10. Index 10 is Black Ops 4's *bank* pool -- its hundred
        // entries are names like `mp_embassy.all` -- and the individual sounds live in SAB files
        // that never reach the loader. This mirrors Cold War, where `sound_asset` is the files
        // (19) and `sound_bank` the banks (18).
        assert_eq!(pool_index_in(BO4_POOLS, "sound_asset"), Some(170), "the SAB sound pool");
        assert_eq!(pool_index_in(BO4_POOLS, "sound"), Some(10), "the bank pool");
    }

    /// The lookup used against Black Ops 4's table, which is where the mismatches bite. Written
    /// against BO4_POOLS directly so it does not depend on this machine's config.toml.
    #[test]
    fn every_default_type_reaches_something_in_black_ops_4() {
        let find = |kind: &str| -> Option<usize> {
            let flattened = |name: &str| name.replace('_', "");

            BO4_POOLS
                .iter()
                .position(|pool| *pool == kind)
                .or_else(|| BO4_POOLS.iter().position(|pool| flattened(pool) == flattened(kind)))
                .or_else(|| {
                    ALIASES
                        .iter()
                        .filter(|group| group.contains(&kind))
                        .find_map(|group| {
                            group.iter().find_map(|other| {
                                BO4_POOLS.iter().position(|pool| pool == other)
                            })
                        })
                })
        };

        // Named the same in both, and the reason Black Ops 4 is worth grinding at all.
        assert_eq!(find("xmodel"), Some(4), "xmodel is 4 in Black Ops 4, not 6");
        assert_eq!(find("xanim"), Some(3));
        assert_eq!(find("image"), Some(9));
        assert_eq!(find("material"), Some(6));

        // Named differently. These are the ones that silently resolved to nothing before.
        // 170, the SAB sound pool appended past the real enum, not 10. Index 10 is the *bank*
        // pool -- its hundred entries are names like `mp_embassy.all` -- and the individual sounds
        // live in SAB files the loader never opens. Same split Cold War already makes.
        assert_eq!(find("sound_asset"), Some(170), "the SAB sound pool, not the bank pool");
        assert_eq!(find("sound"), Some(10), "the bank pool");
        assert_eq!(find("localizeentry"), Some(16), "spelled localize_entry there");
        assert_eq!(find("gesturetable"), Some(19), "spelled gesture_table there");
        assert_eq!(find("clip_map"), Some(11), "spelled clipmap there");
        assert_eq!(find("gfx_map"), Some(14), "called gfxworld there");
        assert_eq!(find("techset"), Some(8), "called technique_set there");
        assert_eq!(find("xmodelmesh"), Some(5), "unreachable in both, and must still be found");
    }

    /// The hash has to be the game's, and the normalisation is half of it: these reproduce
    /// published table keys exactly, and dropping the lower casing or the slash folding makes
    /// every one of them miss.
    #[test]
    fn the_hash_reproduces_published_table_keys() {
        assert_eq!(
            id_of("mc/mtl_c_t9_gloves_02_nylon_green_darkstripe"),
            0x1630_1bbd_eda1_638c
        );
        assert_eq!(
            id_of("p9_mal_clothes_tshirt_crew_mens_hanging_electriccow_full"),
            0x4e09_38e3_6d88_3dcd
        );
    }

    /// A material name is a path and the directory is part of what is hashed. Dropping it was
    /// what kept materials unreachable, so it is worth a test rather than a comment.
    #[test]
    fn the_directory_is_part_of_a_material_name() {
        assert_ne!(
            id_of("mc/mtl_c_t9_gloves_02_nylon_green_darkstripe"),
            id_of("mtl_c_t9_gloves_02_nylon_green_darkstripe")
        );
    }

    #[test]
    fn a_name_hashes_the_same_however_it_is_written() {
        assert_eq!(id_of("MC\\Mtl_Test"), id_of("mc/mtl_test"));
    }

    /// Folding has to give the same answer as hashing the whole string, or every search built on
    /// it is quietly wrong.
    #[test]
    fn folding_a_name_in_pieces_matches_hashing_it_whole() {
        let whole = hash64("i_mtl_wpn_t9_ak47_barrel_c");
        let folded = feed(feed(hash64("i_mtl_"), b"wpn_t9_ak47_barrel"), b"_c");

        assert_eq!(whole, folded);
    }

    /// The filter may say yes wrongly, which the map behind it catches. It may never say no
    /// wrongly, because nothing looks at a candidate it rejects.
    #[test]
    fn the_filter_never_rejects_an_id_it_holds() {
        let ids: Vec<u64> = (0..5_000).map(|n| id_of(&format!("test_{n}"))).collect();
        let filter = Filter::new(ids.iter());

        for id in &ids {
            assert!(filter.may_hold(*id));
        }
    }

    /// A rule change that no longer reaches an old name must not delete it.
    /// The two spellings of a path reach the same asset, and the one written down should be the
    /// one the published tables use.
    #[test]
    fn a_backslash_path_is_written_with_forward_slashes() {
        let mut results = Results::default();
        results.add("sound_asset", 1, r"amb\animals\crow_00.rn75.pc.all.snd".to_owned());

        assert_eq!(results.names("sound_asset")[0], "amb/animals/crow_00.rn75.pc.all.snd");
    }

    #[test]
    fn results_only_ever_grow() {
        let mut results = Results::default();
        results.add("image", 1, "first".to_owned());
        results.add("image", 1, "second".to_owned());
        results.add("image", 2, "third".to_owned());

        assert_eq!(results.len(), 2);
        assert_eq!(results.names("image").len(), 2);
        assert!(results.names("image").contains(&"first".to_owned()));
    }
}
