//! Rewrites `snapshots/*.pools.txt` with each game's own asset type names.
//!
//! The originals were written by `snapshot`, which labelled every pool with Cold War's enum
//! because that was the only one the crate had. Against Black Ops 4 data that is simply wrong:
//! index 5 is `xanim` in Cold War and `xmodelmesh` in Black Ops 4, index 6 is `xmodel` there and
//! `material` here. Every Black Ops 4 count was therefore filed under another type's name, which
//! is how "a model and animation goldmine" got written down about a pool that may be the one kind
//! of asset no rule can ever name.
//!
//! The counts were always right. Only the labels were wrong, and both live in the `.ids` file, so
//! this needs no game and no Cordycep -- it recomputes from what is already committed.

use std::collections::BTreeMap;
use std::fs;

use slasher::snapshot::Snapshot;

fn main() {
    let folder = slasher::paths::snapshots();

    let Ok(entries) = fs::read_dir(&folder) else {
        eprintln!("{} could not be read", folder.display());
        std::process::exit(1);
    };

    let mut any = false;

    for entry in entries.flatten() {
        let path = entry.path();
        if path.extension().and_then(|end| end.to_str()) != Some("ids") {
            continue;
        }

        let snapshot = match Snapshot::read(&path) {
            Ok(snapshot) => snapshot,
            Err(why) => {
                eprintln!("{} could not be read: {why}", path.display());
                continue;
            }
        };

        // The names belong to the game the file says it holds, never to whatever this machine is
        // configured to grind. Getting that wrong is the whole bug being fixed here.
        let names = slasher::pools_for(snapshot.game());

        let mut counts: BTreeMap<usize, usize> = BTreeMap::new();
        for (_, pool) in snapshot.records() {
            *counts.entry(pool as usize).or_default() += 1;
        }

        let mut text = format!(
            "{} -- {} assets in {} filled pools\n\n{:<6} {:<34} {:>10}\n",
            snapshot.game(),
            snapshot.len(),
            counts.len(),
            "index",
            "asset type",
            "assets"
        );

        for (index, count) in &counts {
            let name = names
                .get(*index)
                .map(|name| (*name).to_owned())
                .unwrap_or_else(|| format!("pool_{index}"));

            text.push_str(&format!("{index:<6} {name:<34} {count:>10}\n"));
        }

        let out = path.with_extension("pools.txt");
        match fs::write(&out, text) {
            Ok(()) => {
                println!("{} -- {} pools written to {}", snapshot.game(), counts.len(), out.display());
                any = true;
            }
            Err(error) => eprintln!("{} could not be written: {error}", out.display()),
        }
    }

    if !any {
        eprintln!("no snapshots found in {}", folder.display());
        std::process::exit(1);
    }
}
