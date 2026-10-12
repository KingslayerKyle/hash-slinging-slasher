// CPU baseline for the two halves of the meet engine, same math as src/lib.rs.
// rustc -O bench/cpu_peel.rs -o bench/cpu_peel.exe
//   cpu_peel.exe peel   <ids> <threads>     -- multiply-chain rate over (id, ending) pairs
//   cpu_peel.exe probe  <table_mb> <threads> -- random binary search into a sorted peeled set
//
// No dependencies, and none in Cargo.toml: this is a measurement, not part of the build.

use std::env;
use std::hint::black_box;
use std::sync::Arc;
use std::thread;
use std::time::Instant;

const PRIME: u64 = 0x1000_0000_1B3;
const PRIME_INVERSE: u64 = 0xCE96_5057_AFF6_957B; // pow(PRIME, -1, 2^64), checked below
const ID_MASK: u64 = 0x7FFF_FFFF_FFFF_FFFF;

fn peel(mut hash: u64, text: &[u8]) -> u64 {
    for &byte in text.iter().rev() {
        let byte = match byte {
            b'A'..=b'Z' => byte + 32,
            b'\\' => b'/',
            other => other,
        };
        hash = hash.wrapping_mul(PRIME_INVERSE) ^ byte as u64;
    }
    hash
}

fn endings_from_file() -> Vec<Vec<u8>> {
    let text = std::fs::read_to_string("data/suffixes.txt").expect("data/suffixes.txt");
    let mut out = Vec::new();
    for line in text.lines() {
        let line = line.trim();
        if !line.is_empty() {
            out.push(line.as_bytes().to_vec());
        }
    }
    out
}

fn ids(count: usize) -> Vec<u64> {
    let mut state = 0x2545F4914F6CDD1Du64;
    (0..count)
        .map(|_| {
            state ^= state << 13;
            state ^= state >> 7;
            state ^= state << 17;
            state & ID_MASK
        })
        .collect()
}

fn main() {
    assert_eq!(
        PRIME.wrapping_mul(PRIME_INVERSE),
        1,
        "PRIME_INVERSE must be the real inverse of PRIME"
    );

    let args: Vec<String> = env::args().collect();
    let mode = args.get(1).map(String::as_str).unwrap_or("peel");
    let threads: usize = args
        .get(3)
        .and_then(|value| value.parse().ok())
        .unwrap_or(1);
    if threads == 0 || !matches!(mode, "peel" | "probe") {
        eprintln!("mode must be peel or probe, with at least one thread");
        std::process::exit(2);
    }

    if mode == "peel" {
        let count: usize = args
            .get(2)
            .and_then(|value| value.parse().ok())
            .unwrap_or(1_000_000);
        let endings = endings_from_file();
        let wanted = ids(count);
        let endings = Arc::new(endings);
        let wanted = Arc::new(wanted);
        let total = (count * endings.len()) as u64;

        let started = Instant::now();
        let mut workers = Vec::new();
        for worker in 0..threads {
            let endings = Arc::clone(&endings);
            let wanted = Arc::clone(&wanted);
            workers.push(thread::spawn(move || {
                let mut acc: u64 = 0;
                let slice = endings.len() / threads * worker;
                let end = if worker + 1 == threads {
                    endings.len()
                } else {
                    slice + endings.len() / threads
                };
                for index in slice..end {
                    let ending = &endings[index];
                    for id in wanted.iter() {
                        acc = acc.wrapping_add(peel(black_box(*id), ending));
                    }
                }
                black_box(acc)
            }));
        }
        for worker in workers {
            worker.join().unwrap();
        }
        let seconds = started.elapsed().as_secs_f64();
        println!(
            "peel  ids={count} endings={} threads={threads}  {:.*} peels in {:.1}s  {:.2}G peels/s",
            endings.len(),
            1,
            total as f64 / 1e9,
            seconds,
            total as f64 / 1e9 / seconds
        );
        return;
    }

    if mode == "probe" {
        let table_mb: usize = args
            .get(2)
            .and_then(|value| value.parse().ok())
            .unwrap_or(480);
        let entries = table_mb * 1024 * 1024 / 8;
        let mut table = ids(entries);
        table.sort_unstable();
        let table = Arc::new(table);
        let probes: u64 = 20_000_000;
        let per_thread = probes / threads as u64;

        let started = Instant::now();
        let mut workers = Vec::new();
        for worker in 0..threads {
            let table = Arc::clone(&table);
            workers.push(thread::spawn(move || {
                let mut acc = 0usize;
                let mut state = 0x9E3779B97F4A7C15u64 ^ worker as u64;
                for _ in 0..per_thread {
                    state ^= state << 13;
                    state ^= state >> 7;
                    state ^= state << 17;
                    acc += table.binary_search(&black_box(state & ID_MASK)).is_ok() as usize;
                }
                black_box(acc)
            }));
        }
        for worker in workers {
            worker.join().unwrap();
        }
        let seconds = started.elapsed().as_secs_f64();
        println!(
            "probe table={table_mb}MB ({entries} sorted u64) threads={threads}  \
             {:.1}M random binary searches in {:.1}s  {:.2}M probes/s",
            probes as f64 / 1e6,
            seconds,
            probes as f64 / 1e6 / seconds
        );
    }
}
