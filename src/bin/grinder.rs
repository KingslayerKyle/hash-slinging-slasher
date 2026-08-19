//! The one-click grinder: open it and it grinds.
//!
//! Everything else in this repository assumes somebody at a terminal. This is the opposite: a
//! standalone app for the contributor who wants to donate CPU time and nothing else. Ship it
//! in a folder beside `snapshots/`, `data/` and the other binaries, and:
//!
//!   1. On launch it fetches or refreshes the community tables from cod-name-db -- with git if
//!      the machine has it, and by plain HTTPS download if not. No GitHub account is needed,
//!      because this app never submits anything.
//!   2. It then runs the searches in a self-feeding rotation -- the general search, images
//!      derived from materials, numbered families -- printing every find as it lands. Each
//!      confirmed name seeds the next pass, so leaving it open all night compounds.
//!   3. Everything found is exported continuously as `.csv` in exactly the `hash,name` shape
//!      the cod-name-db tables use, named for the table each belongs in. Closing the app --
//!      Enter, Ctrl+C, or closing the window -- loses at most a minute of work, and the csv
//!      files in `exports/` are always current. Send them to cod-name-db however suits.

use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

use slasher::{paths, tables};

/// The searches, in the order they feed each other: the general search finds materials, the
/// derivative passes turn those into images and family members, and everything they confirm
/// seeds the next general pass.
const ROTATION: [&str; 3] = ["confirm_cw", "images_from_materials", "confirm_variants"];

/// Which cod-name-db table each findings file belongs to, for naming the exports.
fn export_name(kind: &str) -> String {
    match kind {
        "xmodel" => "fnv1a_xmodels.additions.csv".to_owned(),
        "xanim" => "fnv1a_xanims.additions.csv".to_owned(),
        "image" => "fnv1a_ximages.additions.csv".to_owned(),
        "material" => "fnv1a_xmaterials.additions.csv".to_owned(),
        "sound_asset" | "sound" => "fnv1a_xsounds.additions.csv".to_owned(),
        other => format!("{other}.additions.csv"),
    }
}

fn main() {
    println!("hash-slinging-slasher -- the one-click grinder");
    println!("==============================================\n");

    // Everything below uses paths relative to the repository, so stand in it wherever the app
    // was double-clicked from. root() walks up from the executable when the working directory
    // is somewhere unhelpful, which is exactly what a double-click gives you.
    let root = paths::root();
    if let Err(error) = std::env::set_current_dir(&root) {
        finish(&format!("could not enter {}: {error}", root.display()));
        return;
    }

    // 1. The tables. Nothing can be judged without them: a search that cannot read them would
    //    report every published name in the game as a new find.
    println!("fetching the community tables from cod-name-db (a few hundred MB the first time)\n");
    match tables::ensure(&paths::tables(), false) {
        Ok(count) => println!("\n{count} tables to exclude against\n"),
        Err(why) => {
            println!("git could not fetch the tables ({why})");
            println!("trying a plain download instead\n");
            if let Err(why) = download_tables() {
                finish(&format!(
                    "the tables could not be fetched at all: {why}\n\
                     Check the internet connection and open the app again."
                ));
                return;
            }
        }
    }

    // 2. Stop politely whenever the person says so. Enter is the off switch; the thread never
    //    fires on EOF, so a headless launch just grinds until killed.
    let stop = Arc::new(AtomicBool::new(false));
    {
        let stop = Arc::clone(&stop);
        std::thread::spawn(move || {
            let stdin = std::io::stdin();
            let mut line = String::new();
            while let Ok(read) = stdin.lock().read_line(&mut line) {
                if read == 0 {
                    return; // EOF: no console attached, never stop from here.
                }
                stop.store(true, Ordering::Relaxed);
                return;
            }
        });
    }
    println!("grinding starts now. Press Enter at any time to stop and export.\n");

    // 3. The rotation. Each pass prints as it goes, findings checkpoint to disk every minute,
    //    and every checkpoint refreshes the csv exports -- so closing the window at any moment
    //    still leaves current csv files behind.
    'grind: loop {
        for search in ROTATION {
            if stop.load(Ordering::Relaxed) {
                break 'grind;
            }

            let Some(program) = sibling(search) else {
                println!("({search} is not beside this app; skipping it)");
                continue;
            };

            println!("--- {search} ---");
            match run_and_relay(&program, &stop) {
                Ok(stopped) => {
                    export_csvs();
                    if stopped {
                        break 'grind;
                    }
                }
                Err(error) => {
                    println!("{search} could not run: {error}");
                }
            }
        }
    }

    // 4. The handover.
    export_csvs();
    let where_to = root.join("exports");
    finish(&format!(
        "everything found is in {}\n\
         Each file is `hash,name` lines for the cod-name-db table it is named after.\n\
         Send them to https://github.com/echo000/cod-name-db to publish them.",
        where_to.display()
    ));
}

/// A search binary that ships beside this one, or in the repository's usual build spots.
fn sibling(name: &str) -> Option<PathBuf> {
    let file = format!("{name}{}", std::env::consts::EXE_SUFFIX);

    let mut candidates = Vec::new();
    if let Ok(me) = std::env::current_exe() {
        if let Some(dir) = me.parent() {
            candidates.push(dir.join(&file));
        }
    }
    candidates.push(PathBuf::from("bin").join("windows").join(&file));
    candidates.push(PathBuf::from("target").join("release").join(&file));

    candidates.into_iter().find(|path| path.is_file())
}

/// Runs one search, relaying its output, refreshing the exports at every checkpoint. Returns
/// whether the person asked to stop -- in which case the child is ended, which costs at most
/// the minute since its last checkpoint.
fn run_and_relay(program: &Path, stop: &AtomicBool) -> Result<bool, String> {
    let mut child: Child = Command::new(program)
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .spawn()
        .map_err(|error| format!("{error}"))?;

    let stdout = child.stdout.take().ok_or("no output pipe")?;
    for line in BufReader::new(stdout).lines() {
        let Ok(line) = line else { break };
        println!("{line}");

        if line.contains("checkpoint:") {
            export_csvs();
        }

        if stop.load(Ordering::Relaxed) {
            let _ = child.kill();
            let _ = child.wait();
            return Ok(true);
        }
    }

    let _ = child.wait();
    Ok(false)
}

/// Copies every findings file into `exports/` under the name of the cod-name-db table it
/// belongs to. The findings are already `hash,name` lines, which is exactly the csv shape the
/// tables use, so this is a copy rather than a conversion.
fn export_csvs() {
    let findings = paths::findings();
    let exports = Path::new("exports");
    let _ = std::fs::create_dir_all(exports);

    let Ok(entries) = std::fs::read_dir(&findings) else {
        return;
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) != Some("txt") {
            continue;
        }
        let Some(kind) = path.file_stem().and_then(|s| s.to_str()) else {
            continue;
        };
        // localize names are worthless to recover -- the build ships them in plain text.
        if kind == "localizeentry" {
            continue;
        }

        let _ = std::fs::copy(&path, exports.join(export_name(kind)));
    }
}

/// Fetches the tables without git: the zip GitHub serves for the default branch, unpacked with
/// the tar that ships with Windows 10+ and every unix. Slower to refresh than git, but it asks
/// nothing of the machine.
fn download_tables() -> Result<(), String> {
    let zip = "cod-name-db.zip";
    let fetched = Command::new("curl")
        .args([
            "-L",
            "--fail",
            "-o",
            zip,
            "https://github.com/echo000/cod-name-db/archive/refs/heads/main.zip",
        ])
        .status()
        .map_err(|error| format!("curl could not run: {error}"))?;

    if !fetched.success() {
        return Err("the download failed".to_owned());
    }

    let unpacked = Command::new("tar")
        .args(["-xf", zip])
        .status()
        .map_err(|error| format!("tar could not run: {error}"))?;
    let _ = std::fs::remove_file(zip);

    if !unpacked.success() {
        return Err("the archive would not unpack".to_owned());
    }

    // The zip's root folder is named for the branch; the searches expect `cod-name-db`.
    let _ = std::fs::remove_dir_all("cod-name-db");
    std::fs::rename("cod-name-db-main", "cod-name-db")
        .map_err(|error| format!("could not put the tables in place: {error}"))?;

    Ok(())
}

/// The app is double-clicked, so its window vanishes the instant main returns. Hold it open
/// until the person has read the last message.
fn finish(message: &str) {
    println!("\n{message}");
    print!("\npress Enter to close.");
    let _ = std::io::stdout().flush();
    let mut line = String::new();
    let _ = std::io::stdin().lock().read_line(&mut line);
}
