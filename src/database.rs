//! Read database spellings without treating Saluki export paths as original asset names.
use crate::{BASIS, ID_MASK, games::IW_BASIS};

fn policy(table: &str) -> Option<(u64, u64, bool)> {
    let table=table.strip_suffix(".csv").unwrap_or(table);
    if !table.starts_with("fnv1a_") { return None; }
    let mask = match table {
        "fnv1a_bones" => u32::MAX as u64,
        "fnv1a_strings" => 0x0fff_ffff_ffff_ffff,
        "fnv1a_bones_v2" | "fnv1a_soundbanks_aliases_v2" => u64::MAX,
        _ => ID_MASK,
    };
    let basis = if table.ends_with("_v2") && !matches!(table,"fnv1a_bones_v2" | "fnv1a_soundbanks_aliases_v2") { IW_BASIS } else { BASIS };
    Some((basis,mask,table.contains("xsounds") && !table.ends_with("_v2")))
}

/// Hash a restored spelling according to its source table, independent of the search's game.
pub fn source_hash(table: &str, name: &str) -> Option<u64> {
    let table=table.strip_suffix(".csv").unwrap_or(table);
    let (basis,_,_) = policy(table)?;
    if table == "fnv1a_bones" {
        let mut value = 0x811c9dc5u32;
        for byte in name.bytes() { value = (value ^ u32::from(byte)).wrapping_mul(0x01000193); }
        Some(u64::from(value))
    } else {
        let mut value=basis;
        for byte in name.bytes() { value=(value^u64::from(byte)).wrapping_mul(0x100000001b3); }
        Some(value)
    }
}

/// Keep the original only if it hashes correctly; otherwise undo supported separator rewrites.
/// Unrestorable FNV rows are excluded as seeds, but their stored keys still exclude discoveries.
pub fn verified_row(table: &str, key: u64, display: &str) -> Option<(u64,String)> {
    let table=table.strip_suffix(".csv").unwrap_or(table);
    let (_,mask,raw_sound) = policy(table)?;
    let display = display.trim();
    // Legacy files also carry older 60-bit, case-sensitive names. Preserve that source spelling.
    let older_mask = !table.ends_with("_v2") && mask == ID_MASK;
    for spelling in [display.to_owned(),display.to_ascii_lowercase()] {
        let candidates = [spelling.replace('\\',"/"), spelling.replace(['/', '\\'],"."), spelling.replace('/',"\\")];
        for (index,name) in candidates.into_iter().enumerate() {
            if index == 2 && !raw_sound { continue; }
            let full = source_hash(table,&name)?;
            if full & mask == key || (older_mask && full & 0x0fff_ffff_ffff_ffff == key) { return Some((full,name)); }
        }
    }
    None
}

pub fn names(table: &str, text: &str) -> Vec<String> {
    text.lines().filter_map(|line| {
        let (key,display) = line.trim().split_once(',')?;
        let key = u64::from_str_radix(key.trim(),16).ok()?;
        if policy(table).is_some() { verified_row(table,key,display).map(|(_,name)|name) }
        else { Some(display.trim().to_owned()) }
    }).filter(|name| !name.is_empty()).collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn modern_dots_and_legacy_backslashes_are_restored_from_the_table_not_the_selected_game() {
        let original="iw9.dst.iw9_dst_street_barricade_03.ln.75.48000.all";
        let row=verified_row("fnv1a_xsounds_v2",0x10004dd150a8b9e6,"iw9/dst/iw9_dst_street_barricade_03.ln.75.48000.all").unwrap();
        assert_eq!(row.1,original);
        assert_eq!(row.0&ID_MASK,0x10004dd150a8b9e6);
        let row=verified_row("fnv1a_xsounds",0x100116a5a23b8100,"amb/environment/water/waves/crash/wave_crash_01.ln100.pc.snd").unwrap();
        assert_eq!(row.1,"amb\\environment\\water\\waves\\crash\\wave_crash_01.ln100.pc.snd");
        assert_eq!(row.0&ID_MASK,0x100116a5a23b8100);
    }
    #[test]
    fn correct_separators_remain_intact_and_bad_names_are_never_seeded() {
        let original="cin/scene/file.sn75.pc.en.snd";
        let key=source_hash("fnv1a_english_xsounds",original).unwrap()&ID_MASK;
        assert_eq!(verified_row("fnv1a_english_xsounds",key,original).unwrap().1,original);
        assert!(verified_row("fnv1a_english_xsounds",123,original).is_none());
        assert!(names("fnv1a_xsounds_v2","123,wrong/display/name\n").is_empty());
    }
    #[test]
    fn table_masks_and_full_width_aliases_are_obeyed() {
        for table in ["fnv1a_bones","fnv1a_strings","fnv1a_bones_v2","fnv1a_soundbanks_aliases_v2","fnv1a_ximages_v2"] {
            let name="test_name";
            let (_,mask,_)=policy(table).unwrap();
            let full=source_hash(table,name).unwrap();
            assert_eq!(verified_row(table,full&mask,name).unwrap(),(full,name.to_owned()));
            assert_eq!(verified_row(&format!("{table}.csv"),full&mask,name).unwrap(),(full,name.to_owned()));
        }
        let name="fly_npc_ar_able18_ubgl_reload_07";
        let full=source_hash("fnv1a_soundbanks_aliases_v2",name).unwrap();
        assert!(full>ID_MASK);
        assert!(verified_row("fnv1a_soundbanks_aliases_v2",full&ID_MASK,name).is_none());
    }
    #[test]
    fn stored_keys_exclude_unrestorable_rows_without_excluding_the_export_paths_hash() {
        let root=std::env::temp_dir().join(format!("hss_db_key_authority_{}",std::process::id()));
        std::fs::create_dir_all(&root).unwrap();
        let display="unrestorable/display/path.ln.75.all";
        std::fs::write(root.join("fnv1a_xsounds_v2.csv"),format!("123,{display}\n10004dd150a8b9e6,iw9/dst/iw9_dst_street_barricade_03.ln.75.48000.all\n")).unwrap();
        let known=crate::database_keys(&root,"BLACKOP6");
        assert!(known.contains(&0x123));
        assert!(known.contains(&0x10004dd150a8b9e6));
        assert!(!known.contains(&(source_hash("fnv1a_xsounds_v2",display).unwrap()&ID_MASK)));
        assert_eq!(crate::read_names(&root.join("fnv1a_xsounds_v2.csv")),vec!["iw9.dst.iw9_dst_street_barricade_03.ln.75.48000.all"]);
        std::fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn older_source_case_and_sixty_bit_keys_are_preserved_without_relaxing_modern_alias_width() {
        assert_eq!(verified_row("fnv1a_ximages",0x1cbe11a68bb09e77,"ui_icon_stickers_BPS1_058").unwrap().1,"ui_icon_stickers_BPS1_058");
        assert_eq!(verified_row("fnv1a_xanims",0x1fd88e8f753ff0d,"a_chicken_death").unwrap().1,"a_chicken_death");
        assert_eq!(verified_row("fnv1a_english_xsounds",0xb007f5ada1917b7,"cin/cp_amerikatown_load/amerikatown_lr.sn75.pc.en.snd").unwrap().1,"cin/cp_amerikatown_load/amerikatown_lr.sn75.pc.en.snd");
    }

    #[test]
    fn mixed_export_separators_restore_across_modern_tables_and_unknown_spellings_still_exclude() {
        let root=std::env::temp_dir().join(format!("hss_all_modern_separators_{}",std::process::id()));
        std::fs::create_dir_all(&root).unwrap();
        let mut expected=Vec::new();
        for table in crate::games::MODERN_TABLES {
            let original=format!("{table}.weapon.sound.variant");
            let (_,mask,_)=policy(table).unwrap();
            let full=source_hash(table,&original).unwrap();
            let key=full&mask;
            let display=original.replacen('.',"/",1).replacen('.',"\\",1);
            assert_eq!(verified_row(table,key,&display),Some((full,original.clone())));
            let missing=0x123;
            std::fs::write(root.join(format!("{table}.csv")),format!("{key:x},{display}\n{missing:x},unrestorable/display/path\n")).unwrap();
            expected.push((key&ID_MASK,original,table.to_owned()));
        }
        for game in crate::config::GAMES.iter().filter(|g|crate::games::modern(g)) {
            let known=crate::database_keys(&root,game);
            assert!(known.contains(&0x123));
            for (key,original,table) in &expected {
                assert!(known.contains(key),"{game}/{table}: exported spelling hid a known key");
                assert_eq!(crate::read_names(&root.join(format!("{table}.csv"))),vec![original.clone()]);
            }
        }
        std::fs::remove_dir_all(root).unwrap();
    }
}
