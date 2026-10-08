//! Hash policies and capture-local pool maps. Synthetic pools use the same map as native pools.
use std::{collections::HashMap, fs, io::{self, Read}, path::{Path, PathBuf}, sync::{Mutex, OnceLock}};

pub const IW_BASIS: u64 = 0x47F5_817A_5EF9_61BA;
pub const MODERN_TABLES: &[&str] = &[
    "fnv1a_ximages_v2", "fnv1a_xmaterials_v2", "fnv1a_xanims_v2",
    "fnv1a_xsounds_v2", "fnv1a_soundbanks_aliases_v2", "fnv1a_soundbanks_v2",
    "fnv1a_animpkgs_v2",
];

pub fn modern(game: &str) -> bool {
    matches!(game, "MODWAR22" | "YAMYAMOK" | "BLACKOP6" | "BLACKOP7" | "MODWAR7")
}

/// Modern models normally carry embedded names. Keep their hashes as history/vocabulary,
/// but require a deliberate opt-in to hunt or submit a hash-only model exception.
pub fn searchable(game: &str, kind: &str, search_modern_models: bool) -> bool {
    !modern(game) || kind != "xmodel" || search_modern_models
}

pub fn basis(game: &str, kind: &str) -> u64 {
    if modern(game) && !matches!(kind, "sound_alias" | "bone" | "bones") {
        IW_BASIS
    } else { crate::BASIS }
}

pub fn hash(game: &str, kind: &str, name: &str, fold: bool) -> u64 {
    if fold { crate::feed(basis(game, kind), name.as_bytes()) }
    else { crate::feed_raw(basis(game, kind), name.as_bytes()) }
}

/// Database aliases retain bit 63; captured ids always have it cleared.
pub fn output_key(game: &str, kind: &str, name: &str, fold: bool) -> u64 {
    let hash = hash(game, kind, name, fold);
    if modern(game) && kind == "sound_alias" { hash } else { hash & crate::ID_MASK }
}

pub fn canonical(kind: &str) -> &str {
    match kind { "sndasset" => "sound_asset", other => other }
}

/// Saluki CSV paths can replace original periods/backslashes with directory separators.
/// A spelling is accepted only when it reproduces the supplied database key.
pub fn sound_spelling(game: &str, key: u64, display: &str) -> Option<String> {
    let fold = game != "BLKOPS04";
    let table = if modern(game) { "fnv1a_xsounds_v2" } else { "fnv1a_xsounds" };
    let (_, name) = crate::database::verified_row(table, key, display)?;
    (hash(game,"sound_asset",&name,fold) & crate::ID_MASK == key & crate::ID_MASK).then_some(name)
}

pub fn header(path: &Path) -> io::Result<(String, u64)> {
    let mut file = fs::File::open(path)?;
    let mut head = [0; 10];
    file.read_exact(&mut head)?;
    let bad = || io::Error::new(io::ErrorKind::InvalidData, "invalid CODIDS header");
    if &head[..6] != b"CODIDS" || u16::from_le_bytes([head[6],head[7]]) != 1 { return Err(bad()); }
    let n = u16::from_le_bytes([head[8],head[9]]) as usize;
    if n == 0 || n > 64 { return Err(bad()); }
    let mut tag = vec![0; n];
    file.read_exact(&mut tag)?;
    let game = String::from_utf8(tag).map_err(|_| bad())?;
    let mut count = [0; 8];
    file.read_exact(&mut count)?;
    let count = u64::from_le_bytes(count);
    if file.metadata()?.len() != 18 + n as u64 + count.checked_mul(10).ok_or_else(bad)? { return Err(bad()); }
    Ok((game, count))
}

/// Flat runtime directory deliberately contains one combined capture per game.
pub fn capture(game: &str) -> Result<PathBuf, String> {
    let mut found = Vec::new();
    for entry in fs::read_dir(crate::paths::snapshots()).map_err(|e| e.to_string())?.flatten() {
        let path = entry.path();
        if path.extension().and_then(|x| x.to_str()) == Some("ids") {
            let (tag, _) = header(&path).map_err(|e| format!("{}: {e}", path.display()))?;
            if tag == game { found.push(path); }
        }
    }
    match found.len() {
        1 => Ok(found.remove(0)),
        0 => Err(format!("no {game} capture in {}", crate::paths::snapshots().display())),
        _ => Err(format!("multiple {game} captures: combine modes by asset type before searching")),
    }
}

pub fn read_pools(path: &Path) -> Result<Vec<String>, String> {
    let text = fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let mut rows = HashMap::new();
    let mut names = std::collections::HashSet::new();
    for line in text.lines() {
        let fields: Vec<_> = line.split(|c: char| c.is_whitespace() || c == ',').filter(|x| !x.is_empty()).collect();
        if fields.len() != 3 { continue; }
        if let (Ok(index), Ok(_count)) = (fields[0].parse::<usize>(), fields[2].parse::<u64>()) {
            if index > u16::MAX as usize || rows.insert(index, fields[1].to_owned()).is_some() || !names.insert(fields[1].to_owned()) {
                return Err(format!("{}: duplicate or invalid pool mapping", path.display()));
            }
        }
    }
    let max = *rows.keys().max().ok_or_else(|| format!("{}: no pool mappings", path.display()))?;
    let mut pools = (0..=max).map(|i| format!("pool_{i}")).collect::<Vec<_>>();
    for (i, name) in rows { pools[i] = name; }
    Ok(pools)
}

pub fn pools_for(game: &str) -> &'static [&'static str] {
    static CACHE: OnceLock<Mutex<HashMap<PathBuf, &'static [&'static str]>>> = OnceLock::new();
    let path = capture(game).unwrap_or_else(|e| panic!("{e}")).with_extension("pools.txt");
    let mut cache = CACHE.get_or_init(Default::default).lock().unwrap();
    if let Some(pools) = cache.get(&path) { return pools; }
    let names = read_pools(&path).unwrap_or_else(|e| panic!("{e}"));
    let pools: &'static [&'static str] = Box::leak(names.into_iter().map(|s| &*Box::leak(s.into_boxed_str())).collect::<Vec<_>>().into_boxed_slice());
    cache.insert(path, pools);
    pools
}

pub fn groups(wanted: &HashMap<u64, usize>) -> Vec<(u64, HashMap<u64, usize>)> {
    let game = crate::config::game();
    if !modern(&game) { return vec![(crate::BASIS, wanted.clone())]; }
    let pools = crate::pools_for(&game);
    let mut groups = std::collections::BTreeMap::<u64, HashMap<u64, usize>>::new();
    for (&id, &pool) in wanted {
        let kind = pools.get(pool).expect("captured pool must have a mapping");
        groups.entry(basis(&game, kind)).or_default().insert(id, pool);
    }
    groups.into_iter().collect()
}

/// Advance by one slot, independent of historical per-game pass counts.
pub fn next_game<'a>(available: &'a [&str], previous: Option<&str>) -> Option<&'a str> {
    if available.is_empty() { return None; }
    let index = previous.and_then(|p| available.iter().position(|g| *g == p)).map(|i| (i+1)%available.len()).unwrap_or(0);
    Some(available[index])
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn rotation_visits_every_game() {
        let order = ["BLKOPS04", "BLKOPSCW", "MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"];
        assert_eq!(next_game(&[], None), None);
        assert_eq!(next_game(&order, None), Some(order[0]));
        for i in 0..order.len() { assert_eq!(next_game(&order, Some(order[i])), Some(order[(i+1)%order.len()])); }
        assert_eq!(next_game(&order, Some("removed")), Some(order[0]));
    }
    #[test] fn modern_policies_and_alias_width() {
        assert_eq!(hash("BLACKOP6", "image", "TEST\\name", true), crate::feed(IW_BASIS, b"test/name"));
        assert_eq!(hash("BLACKOP6", "sound_alias", "test", true), crate::hash64("test"));
        assert_ne!(hash("BLACKOP6", "image", "test", true), crate::hash64("test"));
        assert_eq!(output_key("BLACKOP6", "sound_alias", "test", true), crate::hash64("test"));
        assert_eq!(output_key("BLKOPSCW", "sound_alias", "test", true), crate::id_of("test"));
    }
    #[test] fn sound_display_paths_require_verified_original_spellings() {
        let display = "iw9/dst/iw9_dst_street_barricade_03.ln.75.48000.all";
        let original = sound_spelling("MODWAR22", 0x10004dd150a8b9e6, display).unwrap();
        assert_eq!(original, "iw9.dst.iw9_dst_street_barricade_03.ln.75.48000.all");
        assert_eq!(output_key("MODWAR22", "sound_asset", &original, true), 0x10004dd150a8b9e6);
        let display = "amb/environment/water/waves/crash/wave_crash_01.ln100.pc.snd";
        let original = sound_spelling("BLKOPS04", 0x100116a5a23b8100, display).unwrap();
        assert!(original.contains('\\'));
        assert_eq!(output_key("BLKOPS04", "sound_asset", &original, false), 0x100116a5a23b8100);
        assert!(sound_spelling("MODWAR22", 123, display).is_none());
    }
}
