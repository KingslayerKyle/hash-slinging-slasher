//! Known-pair cracker for techset naming conventions.
//!
//! Black Ops 4 carries assets left over from Black Ops III, so the same material exported from
//! both games gives a known pair: BO3 shows the techset's plain name (`mc/lit_weapon#e6142445`)
//! and BO4 shows only the hash of whatever BO4 calls the same thing
//! (`techset_7164a9a402077437`). Whatever transformation connects them must connect every such
//! pair consistently, so three pairs make a found answer a proof rather than a guess.
//!
//! Reads lines of `target_hex,bo3_name` and tries `<base><separator><hex tag>` for every
//! separator in a small set, every tag width up to eight, and the base both with and without
//! its directory. The whole tag space is swept at each width, so the original BO3 tag is
//! covered as one candidate among all of them.

use std::path::Path;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Instant;

use slasher::{feed, read_list, ID_MASK};

const HEX: [u8; 16] = *b"0123456789abcdef";
const SEPARATORS: [&str; 5] = ["#", "", "_", ".", "@"];

#[inline(always)]
fn step(hash: u64, byte: u8) -> u64 {
    feed(hash, &[byte])
}

/// Every tag of every width up to eight, depth first so states are reused.
fn sweep(seed: u64, target: u64, label: &str) {
    let mut stack = [(seed, 0u8); 9];
    let mut tag = [0u8; 8];

    if seed & ID_MASK == target {
        println!("  MATCH {label} with no tag at all");
    }

    let mut depth = 0usize;
    loop {
        let (state, digit) = stack[depth];
        if digit as usize >= HEX.len() {
            if depth == 0 {
                break;
            }
            depth -= 1;
            continue;
        }
        stack[depth].1 += 1;

        let next = step(state, HEX[digit as usize]);
        tag[depth] = HEX[digit as usize];

        if next & ID_MASK == target {
            let text: String = tag[..=depth].iter().map(|&b| b as char).collect();
            println!("  MATCH {label} tag '{text}' (width {})", depth + 1);
        }

        if depth + 1 < 8 {
            depth += 1;
            stack[depth] = (next, 0);
        }
    }
}

fn main() {
    let began = Instant::now();
    assert_eq!(feed(slasher::games::hash(&slasher::config::game(), "techset", "mc/a", true), b"bc#0"), slasher::games::hash(&slasher::config::game(), "techset", "mc/abc#0", true));

    let list = std::env::args().nth(1).expect("a file of target_hex,bo3_name lines");
    let pairs: Vec<(u64, String, String)> = read_list(Path::new(&list))
        .into_iter()
        .filter_map(|line| {
            let (hex, name) = line.split_once(',')?;
            let target = u64::from_str_radix(hex.trim(), 16).ok()? & ID_MASK;
            // The name with its original tag stripped: everything before the '#'.
            let base = name.split('#').next().unwrap_or(name).trim().to_owned();
            Some((target, base, name.trim().to_owned()))
        })
        .collect();

    println!("{} known pairs", pairs.len());

    // First the literal BO3 names, tag and all -- if BO4 kept them verbatim, done already.
    for (target, _, original) in &pairs {
        if slasher::games::hash(&slasher::config::game(), "techset", original, true) & ID_MASK == *target {
            println!("  MATCH: BO4 kept the BO3 name verbatim: {original}");
        }
    }

    // Then every shape: each pair, base with and without its directory, every separator,
    // every tag width. One work item per (pair, base form, separator).
    let mut jobs: Vec<(u64, String, String)> = Vec::new();
    for (target, base, _) in &pairs {
        let mut forms = vec![base.clone()];
        if let Some((_, stem)) = base.split_once('/') {
            forms.push(stem.to_owned());
        }

        for form in forms {
            for separator in SEPARATORS {
                jobs.push((*target, format!("{form}{separator}"), format!("{form}<{separator}>")));
            }
        }
    }

    println!("{} shapes to sweep, all tag widths 0..=8 each", jobs.len());

    let next = AtomicUsize::new(0);
    std::thread::scope(|scope| {
        for _ in 0..std::thread::available_parallelism().map(|n| n.get()).unwrap_or(8) {
            scope.spawn(|| loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some((target, prefix, label)) = jobs.get(index) else { break };
                sweep(slasher::games::hash(&slasher::config::game(), "techset", prefix, true), *target, label);
            });
        }
    });

    println!("done in {}", slasher::human_duration(began.elapsed()));
}
