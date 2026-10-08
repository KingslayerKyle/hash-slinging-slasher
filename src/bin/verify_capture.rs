//! Offline replay of published names against actual captures. Writes only to --out.
//! This deliberately withholds the sampled names from a local exclusion set; production gates stay enabled.
use std::{collections::{HashMap, HashSet}, fs, path::PathBuf};
use slasher::{config, games, loader, pool_index, search::{Meet, Search, run_best}, tables, paths, ID_MASK};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().collect();
    let out = args.windows(2).find(|p| p[0] == "--out").map(|p| PathBuf::from(&p[1])).ok_or("--out required; replay never uses production findings")?;
    if out.exists() { return Err("existing replay output preserved; use a fresh directory".into()); }
    let game = config::game();
    let (assets, _) = loader::loaded_assets()?;
    let known = slasher::table_keys();
    assert!(slasher::tables_look_complete(&known), "published tables read short");
    let modern = games::modern(&game);
    let ordinary = if modern { "_v2" } else { "" };
    let mut summary = Vec::new();
    let mut all_wanted = HashMap::new();
    let mut all_names = Vec::new();
    let mut results = slasher::Results::default();
    if game == "BLKOPS04" { results = results.keeping_spelling(); }
    for (kind, stem) in [("xmodel", "fnv1a_xmodels"), ("image", "fnv1a_ximages"), ("material", "fnv1a_xmaterials"), ("xanim", "fnv1a_xanims"), ("sound_asset", "fnv1a_xsounds"), ("sound_alias", "fnv1a_soundbanks_aliases")] {
        let Some(pool) = pool_index(kind) else { continue };
        let held: HashSet<_> = assets.iter().filter(|(_, p)| *p == pool).map(|(id, _)| *id).collect();
        let mut table = format!("{stem}{ordinary}.csv");
        let fold = !(game == "BLKOPS04" && kind == "sound_asset");
        if game == "BLKOPSCW" && kind == "sound_asset" { table = "fnv1a_english_xsounds.csv".to_owned(); }
        // Modern models have no dedicated source CSV. Names shared with ordinary assets
        // are valid fixtures only when their verified hash is in this game's model pool.
        let sources: Vec<String> = if modern && kind == "xmodel" {
            games::MODERN_TABLES.iter().filter(|s| **s != "fnv1a_soundbanks_aliases_v2")
                .map(|s| format!("{s}.csv")).collect()
        } else { vec![table] };
        let mut sample = HashMap::new();
        let mut high = None;
        for table in sources {
        let text = fs::read_to_string(tables::csv_folder(&paths::tables()).join(&table))?;
        for row in text.lines() {
            let Some((key, name)) = row.split_once(',') else { continue };
            let Ok(published) = u64::from_str_radix(key.trim(), 16) else { continue };
            let Some((_,restored)) = slasher::database::verified_row(&table,published,name.trim()) else { continue };
            let name=restored.as_str();
            let full = games::hash(&game, kind, name, fold);
            let id = full & ID_MASK;
            // Some DB sound rows contain display names. Only reproducible keys are replay fixtures.
            if published & ID_MASK != id || !held.contains(&id) { continue; }
            if modern && kind == "sound_alias" && full > ID_MASK && high.is_none() { high = Some((id, name.to_owned())); }
            if sample.len() < 100 { sample.insert(id, name.to_owned()); }
            if sample.len() >= 100 && (!(modern && kind == "sound_alias") || high.is_some()) { break; }
        }
        if sample.len() >= 100 { break; }
        }
        if let Some((id, name)) = high { sample.insert(id, name); }
        assert!(!sample.is_empty(), "{game}/{kind}: no reproducible published names in capture");
        let sampled: HashSet<_> = sample.keys().copied().collect();
        assert!(sampled.is_subset(&known), "normal exclusions must already know every fixture");
        let withheld: HashSet<_> = known.iter().copied().filter(|id| !sampled.contains(&(id & ID_MASK))).collect();
        let limited: Vec<_> = sample.keys().map(|id| (*id, pool)).collect();
        let wanted = loader::unnamed_in(&limited, &withheld, pool);
        assert_eq!(wanted.len(), sample.len());
        assert!(loader::unnamed_in(&limited, &known, pool).is_empty(), "normal DB exclusion must hide all fixtures");
        let names: Vec<_> = sample.values().cloned().collect();
        let basis = games::basis(&game, kind);
        let hits = Meet::with_basis(&[], &[], basis, fold).run(&names, &wanted);
        assert_eq!(hits.iter().map(|(id, _)| *id).collect::<HashSet<_>>(), sampled);
        if fold {
            let forward = Search::with_basis(&[], &[], basis).run(&names, &wanted);
            assert_eq!(forward.iter().map(|(id, _)| *id).collect::<HashSet<_>>(), sampled);
            all_wanted.extend(wanted);
            all_names.extend(names.clone());
            // Exercise real partial-name recovery, not just whole-name hashing.
            let (id, name) = sample.iter().find(|(_, n)| n.len() > 3 && n.is_ascii()).ok_or("no fragment fixture")?;
            let openings = vec![name[..1].to_owned()];
            let endings = vec![name[name.len()-1..].to_owned()];
            let middles = vec![name[1..name.len()-1].to_owned()];
            let one = HashMap::from([(*id, pool)]);
            let fragment = Meet::with_basis(&openings, &endings, basis, true).dressed_only().run(&middles, &one);
            assert!(fragment.contains(&(*id, name.clone())), "fragment recovery failed");
        }
        if modern && kind != "sound_alias" {
            assert!(Meet::with_basis(&[], &[], slasher::BASIS, true).run(&names, &HashMap::from_iter(sample.keys().map(|id| (*id,pool)))).is_empty(), "wrong offset matched fixture");
        }
        let high_bit = sample.values().filter(|name| games::output_key(&game, kind, name, fold) > ID_MASK).count();
        for name in sample.values() {
            results.add(kind, games::hash(&game, kind, name, fold) & ID_MASK, name.clone());
        }
        summary.push(format!("{game},{kind},{},{high_bit}\n", sample.len()));
    }
    // Default engines must partition mixed ordinary/alias pools by hash basis automatically.
    for hits in [Search::new(&[], &[]).run(&all_names, &all_wanted), Meet::new(&[], &[]).run(&all_names, &all_wanted), run_best(&[], &[], &all_names, &all_wanted, true)] {
        assert_eq!(hits.iter().map(|(id, _)| *id).collect::<HashSet<_>>(), all_wanted.keys().copied().collect());
    }
    assert!(Search::new(&[], &[]).run(&["__codex_nonexistent_capture_fixture__"], &all_wanted).is_empty());
    fs::create_dir_all(&out)?;
    results.write(&out)?;
    assert!(all_wanted.keys().all(|id| results.ids().contains(id)));
    fs::write(out.join("replay.csv"), format!("game,type,recovered,full_width_keys\n{}", summary.concat()))?;
    println!("REPLAY_OK\n{}", summary.concat());
    Ok(())
}
