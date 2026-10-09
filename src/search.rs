//! The scan every search here runs: beginnings and endings against a set of stems, hashed and
//! held up against the ids the loader has that nobody can name.
//!
//! Each search differs only in where its stems, beginnings and endings come from. The scan
//! itself is the same question asked hundreds of billions of times, and it is the same three
//! things that make it affordable: the hash is folded so a beginning costs nothing per stem and
//! an ending costs only the bytes it is long, a candidate meets two bitmaps before it reaches a
//! map, and a name is built into a string only once it has already matched.

use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};
use std::time::{Duration, Instant};

use crate::{expected_by_chance, feed, feed_raw, peel, peel_raw, Filter, BASIS, ID_MASK};

/// How many entries a batch of peeled endings is allowed to reach.
///
/// The peeled set is held as a sorted list of hashes, eight bytes each, and the filter over it
/// wants another byte or so per entry. Sixty million is about half a gigabyte all told, which
/// leaves room on a machine that is also running the loader.
const PEELED_BATCH: usize = 60_000_000;

/// The beginning index that means there was no beginning at all.
const BARE: usize = 0xFFFF_FFFF;

/// A search that peels its endings off the answers instead of appending them to the questions.
///
/// The forward search costs `stems x beginnings x endings`, and the endings are the longest list
/// by a distance -- two thousand of them against a hundred and seventy beginnings. Since the
/// hash can be run backwards, an ending does not have to be appended to anything: it can be
/// taken off each wanted id once, leaving the hash that whatever comes before it must produce.
/// Then the scan only has to try `stems x beginnings`, and look each result up in the peeled set.
///
/// The cost stops being a product and becomes a sum, so the ending list is very nearly free. A
/// pass that took two hours takes minutes, and the lists can be widened by an order of magnitude
/// for what the narrow ones used to cost.
///
/// The peeled set is built in batches because it is `wanted x endings x 2` entries and that does
/// not fit in memory whole. Two, because a loader id has had bit 63 cleared and the name's real
/// hash may have had it set.
pub struct Meet<'a> {
    openings: Vec<(String, u64)>,
    endings: &'a [String],
    bare: bool,
    /// Whether backslashes are folded to forward slashes, as every asset type but one wants.
    ///
    /// Carried on the search rather than chosen at each call site, because the peel and the feed
    /// **must** agree: peeling with one normalisation and hashing with the other produces a
    /// search that matches nothing at all and looks entirely healthy doing it. One flag, six
    /// places derived from it, no way for them to drift apart.
    fold: bool,
    basis: u64,
    explicit_basis: bool,
}

/// One batch of endings, peeled off every wanted id.
struct Peeled {
    /// Every hash a stem-and-beginning would have to reach, sorted so it can be searched.
    hashes: Vec<u64>,
    filter: Filter,
}

impl Peeled {
    /// Peels a batch of endings off every wanted id.
    ///
    /// `no_ending` asks for the id itself as well, un-peeled, which is the candidate that has no
    /// ending on it. That is a separate question from whether a stem may stand with no beginning:
    /// one is about the end of a name and the other about its start, and a search that treats
    /// them as one loses every name that carries a beginning and no ending.
    fn build(
        wanted: &HashMap<u64, usize>,
        endings: &[&String],
        no_ending: bool,
        fold: bool,
    ) -> Self {
        let mut hashes: Vec<u64> =
            Vec::with_capacity(wanted.len() * (endings.len() + usize::from(no_ending)) * 2);

        for id in wanted.keys() {
            // The id has had bit 63 cleared, so the name hashed to one of two values.
            for spelling in [*id, id | !ID_MASK] {
                if no_ending {
                    hashes.push(spelling);
                }

                for ending in endings {
                    hashes.push(if fold {
                        peel(spelling, ending.as_bytes())
                    } else {
                        peel_raw(spelling, ending.as_bytes())
                    });
                }
            }
        }

        hashes.sort_unstable();
        hashes.dedup();

        let filter = Filter::sized(hashes.iter(), hashes.len());

        Self { hashes, filter }
    }

    #[inline(always)]
    fn holds(&self, hash: u64) -> bool {
        self.filter.may_hold(hash) && self.hashes.binary_search(&hash).is_ok()
    }
}

impl<'a> Meet<'a> {
    pub fn new(openings: &[String], endings: &'a [String]) -> Self {
        Self::with_fold(openings, endings, true)
    }

    /// A search over names whose backslashes are **not** folded to forward slashes.
    ///
    /// Black Ops 4's SAB sound names are the only ones like this, and their ids are the hash of
    /// the unfolded string. See `slasher::feed_raw` for the measurement.
    pub fn unfolded(openings: &[String], endings: &'a [String]) -> Self {
        Self::with_fold(openings, endings, false)
    }

    fn with_fold(openings: &[String], endings: &'a [String], fold: bool) -> Self {
        let mut result = Self::with_basis(openings, endings, BASIS, fold);
        result.explicit_basis = false;
        result
    }

    pub fn with_basis(openings: &[String], endings: &'a [String], basis: u64, fold: bool) -> Self {
        Self {
            openings: openings
                .iter()
                .map(|opening| {
                    let hash = if fold {
                        feed(basis, opening.as_bytes())
                    } else {
                        feed_raw(basis, opening.as_bytes())
                    };
                    (opening.clone(), hash)
                })
                .collect(),
            endings,
            bare: true,
            fold,
            basis,
            explicit_basis: true,
        }
    }

    /// Drops the bare stem, with no beginning and no ending, from the candidates.
    pub fn dressed_only(mut self) -> Self {
        self.bare = false;
        self
    }

    /// How many candidates this is equivalent to trying, which is what the cost by coincidence
    /// is reckoned on. The work done is far less; the question asked is the same.
    pub fn candidates(&self, stems: usize) -> u64 {
        let openings = self.openings.len() as u64 + u64::from(self.bare);

        stems as u64 * openings * (self.endings.len() as u64 + 1)
    }

    /// Runs the search and returns every name that matched.
    pub fn run<S: AsRef<str> + Sync>(
        &self,
        stems: &[S],
        wanted: &HashMap<u64, usize>,
    ) -> Vec<(u64, String)> {
        self.run_checkpointed(stems, wanted, &mut |_| {})
    }

    /// The same, handing over each batch's names as soon as they are known.
    ///
    /// A pass takes an hour, and the thing running it is often an assistant on a usage limit that
    /// can end mid-run. Returning everything only at the end means a run cut off at fifty five
    /// minutes is worth nothing at all, which is the difference between a night of grinding and
    /// a night of nothing.
    ///
    /// A batch boundary is the earliest a name can be handed over, because within a batch the
    /// workers collect bare hashes and it is the join afterwards that turns them into names.
    /// That is fine: a batch is seconds to under a minute, so this is a finer checkpoint than
    /// a timer would give and needs no clock of its own.
    pub fn run_checkpointed<S: AsRef<str> + Sync>(
        &self,
        stems: &[S],
        wanted: &HashMap<u64, usize>,
        checkpoint: &mut dyn FnMut(&[(u64, String)]),
    ) -> Vec<(u64, String)> {
        if !self.explicit_basis && crate::games::modern(&crate::config::game()) {
            let openings: Vec<_> = self.openings.iter().map(|(s, _)| s.clone()).collect();
            let mut all = Vec::new();
            for (basis, targets) in crate::games::groups(wanted) {
                let mut search = Self::with_basis(&openings, self.endings, basis, self.fold);
                search.bare = self.bare;
                all.extend(search.run_checkpointed(stems, &targets, checkpoint));
            }
            return all;
        }
        let threads = std::thread::available_parallelism()
            .map(|count| count.get())
            .unwrap_or(8);

        let equivalent = self.candidates(stems.len());
        println!(
            "candidates: {equivalent} ({:.2}T equivalent) across {threads} threads",
            equivalent as f64 / 1e12
        );
        println!(
            "names expected to match by chance at this size: {:.3}",
            expected_by_chance(equivalent, wanted.len())
        );

        // How many endings fit in one peeled batch.
        let per_id = wanted.len().max(1) * 2;
        let batch = (PEELED_BATCH / per_id).max(1);
        let batches = self.endings.len().div_ceil(batch).max(1);

        println!(
            "peeling {} endings off {} ids in {batches} batch(es) of {batch}",
            self.endings.len(),
            wanted.len()
        );

        let mut collected: Vec<(u64, String)> = Vec::new();
        let started = Instant::now();
        let forward = AtomicU64::new(0);

        // An empty ending list still has one thing to ask -- the stem and beginning on their
        // own -- and `chunks` on an empty slice yields nothing at all, which would sweep nothing.
        let rounds: Vec<&[String]> = if self.endings.is_empty() {
            vec![&[]]
        } else {
            self.endings.chunks(batch).collect()
        };

        for (number, chunk) in rounds.into_iter().enumerate() {
            let slice: Vec<&String> = chunk.iter().collect();

            // The bare stem is a candidate in its own right, and only needs asking once.
            // The ending-less candidate is asked once, on the first batch.
            let peeled = Peeled::build(wanted, &slice, number == 0, self.fold);

            let done = AtomicUsize::new(0);
            let finished = AtomicBool::new(false);
            let total = stems.len();
            let mut reached: Vec<u64> = Vec::new();

            std::thread::scope(|scope| {
                let reporter = scope.spawn(|| {
                    let mut last = Instant::now();

                    while !finished.load(Ordering::Relaxed) {
                        std::thread::sleep(Duration::from_millis(250));

                        if last.elapsed() < REPORT_EVERY {
                            continue;
                        }
                        last = Instant::now();

                        let seen = done.load(Ordering::Relaxed);
                        let elapsed = started.elapsed().as_secs_f64();
                        let share = (number as f64 + seen as f64 / total as f64)
                            / batches as f64;

                        println!(
                            "  batch {}/{batches}  {:>5.1}%  {seen}/{total} stems  {:.1}B forward  {:.0}s left",
                            number + 1,
                            share * 100.0,
                            forward.load(Ordering::Relaxed) as f64 / 1e9,
                            if share > 0.0 { elapsed / share - elapsed } else { 0.0 },
                        );
                    }
                });

                let size = total.div_ceil(threads).max(1);
                let mut workers = Vec::new();

                for (index, piece) in stems.chunks(size).enumerate() {
                    let this = &*self;
                    let peeled = &peeled;
                    let done = &done;
                    let forward = &forward;
                    let base = index * size;

                    workers
                        .push(scope.spawn(move || this.sweep(piece, base, peeled, done, forward)));
                }

                for worker in workers {
                    reached.extend(worker.join().expect("a worker"));
                }

                finished.store(true, Ordering::Relaxed);
                let _ = reporter.join();
            });

            // A stem-and-beginning that reached the peeled set has an ending in this batch that
            // completes it. Which one is worth finding out by hand: it happens rarely enough
            // that trying every ending forward costs nothing.
            let before = collected.len();
            collected.extend(self.name_them(&reached, stems, &slice, wanted, number == 0));
            if forward.load(Ordering::Relaxed) != 0 {
                crate::gpu::record_cpu();
            }

            // Handed over now rather than at the end, so a run that is cut off keeps what it had
            // already found.
            if collected.len() > before {
                checkpoint(&collected[before..]);
            }

            drop(peeled);
        }

        println!(
            "swept {:.1}B forward hashes in {:.0}s, {} matched",
            forward.load(Ordering::Relaxed) as f64 / 1e9,
            started.elapsed().as_secs_f64(),
            collected.len()
        );

        collected
    }

    /// The fold this search was built with, applied. Every hash in the engine goes through here.
    #[inline(always)]
    fn feed(&self, hash: u64, text: &[u8]) -> u64 {
        if self.fold {
            feed(hash, text)
        } else {
            feed_raw(hash, text)
        }
    }

    /// One worker's share of the stems, reporting the index of every stem-and-beginning that
    /// landed in the peeled set. The index carries both which stem and which beginning.
    fn sweep<S: AsRef<str>>(
        &self,
        chunk: &[S],
        base: usize,
        peeled: &Peeled,
        done: &AtomicUsize,
        forward: &AtomicU64,
    ) -> Vec<u64> {
        let mut reached: Vec<u64> = Vec::new();
        let mut counted = 0_u64;
        let mut since = 0_usize;

        for (offset, stem) in chunk.iter().enumerate() {
            let piece = stem.as_ref().as_bytes();

            if self.bare {
                counted += 1;
                if peeled.holds(self.feed(self.basis, piece)) {
                    reached.push(Self::mark(base + offset, BARE));
                }
            }

            for (index, (_, opening)) in self.openings.iter().enumerate() {
                counted += 1;
                if peeled.holds(self.feed(*opening, piece)) {
                    reached.push(Self::mark(base + offset, index));
                }
            }

            since += 1;
            if since == BATCH {
                done.fetch_add(since, Ordering::Relaxed);
                forward.fetch_add(counted, Ordering::Relaxed);
                since = 0;
                counted = 0;
            }
        }

        done.fetch_add(since, Ordering::Relaxed);
        forward.fetch_add(counted, Ordering::Relaxed);

        reached
    }

    /// A stem offset and a beginning index, packed so a worker can report both as one number.
    /// Half the word each, which is more of both than any list here will ever hold.
    #[inline(always)]
    fn mark(offset: usize, opening: usize) -> u64 {
        ((offset as u64) << 32) | (opening as u64 & 0xFFFF_FFFF)
    }

    /// Turns what the sweep reached into names, by trying the batch's endings forward.
    ///
    /// The sweep only proves that something in this batch completes the stem; which ending it is
    /// costs a few dozen hashes to find out, and it happens rarely enough not to matter.
    fn name_them<S: AsRef<str>>(
        &self,
        reached: &[u64],
        stems: &[S],
        endings: &[&String],
        wanted: &HashMap<u64, usize>,
        bare_batch: bool,
    ) -> Vec<(u64, String)> {
        let mut named = Vec::new();

        for mark in reached {
            let offset = (mark >> 32) as usize;
            let opening = (mark & 0xFFFF_FFFF) as usize;

            let Some(stem) = stems.get(offset) else {
                continue;
            };
            let stem = stem.as_ref();

            let (prefix, base) = if opening == BARE {
                ("", self.basis)
            } else {
                let (text, hash) = &self.openings[opening];
                (text.as_str(), *hash)
            };

            let start = self.feed(base, stem.as_bytes());

            if bare_batch {
                let id = start & ID_MASK;
                if wanted.contains_key(&id) {
                    named.push((id, format!("{prefix}{stem}")));
                }
            }

            for ending in endings {
                let id = self.feed(start, ending.as_bytes()) & ID_MASK;
                if wanted.contains_key(&id) {
                    named.push((id, format!("{prefix}{stem}{ending}")));
                }
            }
        }

        named
    }
}

/// A run takes long enough that silence is indistinguishable from a hang.
const REPORT_EVERY: Duration = Duration::from_secs(30);

/// How many stems a worker finishes before touching the shared counters. Sixteen threads
/// contending over one counter per stem costs more than the counting is worth.
const BATCH: usize = 1024;

/// A search, as the three lists it multiplies together.
pub struct Search {
    /// Every beginning, with its hash already taken, since a beginning is hashed once for a
    /// whole run rather than once per candidate.
    openings: Vec<(String, u64)>,

    endings: Vec<String>,

    /// Whether the bare stem, with neither a beginning nor an ending, is a candidate in itself.
    /// It is for a scraped string, which may already be the whole name; it is not where the stem
    /// is a fragment that is known to need dressing.
    bare: bool,
    basis: u64,
    explicit_basis: bool,
}

impl Search {
    pub fn new(openings: &[String], endings: &[String]) -> Self {
        let mut result = Self::with_basis(openings, endings, BASIS);
        result.explicit_basis = false;
        result
    }

    pub fn with_basis(openings: &[String], endings: &[String], basis: u64) -> Self {
        Self {
            openings: openings
                .iter()
                .map(|opening| (opening.clone(), feed(basis, opening.as_bytes())))
                .collect(),
            endings: endings.to_vec(),
            bare: true,
            basis,
            explicit_basis: true,
        }
    }

    /// Drops the bare stem from the candidates.
    pub fn dressed_only(mut self) -> Self {
        self.bare = false;
        self
    }

    /// How many candidates a set of stems will produce.
    pub fn candidates(&self, stems: usize) -> u64 {
        let per_opening = self.endings.len() as u64 + 1;
        let openings = self.openings.len() as u64 + u64::from(self.bare);

        stems as u64 * openings * per_opening
    }

    /// Runs the scan across every thread available, and returns what matched.
    ///
    /// `wanted` is the ids still unnamed; anything else the filter lets through is dropped by the
    /// map behind it. Progress is printed because a run of this size is measured in hours.
    pub fn run<S: AsRef<str> + Sync>(
        &self,
        stems: &[S],
        wanted: &HashMap<u64, usize>,
    ) -> Vec<(u64, String)> {
        if !self.explicit_basis && crate::games::modern(&crate::config::game()) {
            let openings: Vec<_> = self.openings.iter().map(|(s, _)| s.clone()).collect();
            let mut all = Vec::new();
            for (basis, targets) in crate::games::groups(wanted) {
                let mut search = Self::with_basis(&openings, &self.endings, basis);
                search.bare = self.bare;
                all.extend(search.run(stems, &targets));
            }
            return all;
        }
        let filter = Filter::new(wanted.keys());

        let threads = std::thread::available_parallelism()
            .map(|count| count.get())
            .unwrap_or(8);

        let expected = self.candidates(stems.len());
        println!(
            "candidates: {expected} ({:.2}T) across {threads} threads",
            expected as f64 / 1e12
        );
        println!(
            "names expected to match by chance at this size: {:.3}",
            expected_by_chance(expected, wanted.len())
        );

        let done = AtomicUsize::new(0);
        let tried = AtomicU64::new(0);
        let finished = AtomicBool::new(false);
        let total = stems.len();

        let mut collected: Vec<(u64, String)> = Vec::new();
        let started = Instant::now();

        std::thread::scope(|scope| {
            let reporter = scope.spawn(|| {
                let mut last = Instant::now();

                while !finished.load(Ordering::Relaxed) {
                    std::thread::sleep(Duration::from_millis(250));

                    if last.elapsed() < REPORT_EVERY {
                        continue;
                    }
                    last = Instant::now();

                    let seen = done.load(Ordering::Relaxed);
                    let candidates = tried.load(Ordering::Relaxed);
                    let elapsed = started.elapsed().as_secs_f64();
                    let share = seen as f64 / total as f64;

                    println!(
                        "  {:>5.1}%  {seen}/{total} stems  {:.1}B  {:.0}M/s  {:.0}s left",
                        share * 100.0,
                        candidates as f64 / 1e9,
                        candidates as f64 / elapsed / 1e6,
                        if share > 0.0 {
                            elapsed / share - elapsed
                        } else {
                            0.0
                        },
                    );
                }
            });

            let size = total.div_ceil(threads).max(1);
            let mut workers = Vec::new();

            for chunk in stems.chunks(size) {
                let this = &*self;
                let filter = &filter;
                let done = &done;
                let tried = &tried;

                workers.push(scope.spawn(move || this.sweep(chunk, filter, wanted, done, tried)));
            }

            for worker in workers {
                collected.extend(worker.join().expect("a worker"));
            }

            finished.store(true, Ordering::Relaxed);
            let _ = reporter.join();
        });

        println!(
            "scanned {} candidates in {:.0}s, {} matched",
            tried.load(Ordering::Relaxed),
            started.elapsed().as_secs_f64(),
            collected.len()
        );

        if tried.load(Ordering::Relaxed) != 0 {
            crate::gpu::record_cpu();
        }

        collected
    }

    /// One worker's share of the stems.
    fn sweep<S: AsRef<str>>(
        &self,
        chunk: &[S],
        filter: &Filter,
        wanted: &HashMap<u64, usize>,
        done: &AtomicUsize,
        tried: &AtomicU64,
    ) -> Vec<(u64, String)> {
        let mut hits: Vec<(u64, String)> = Vec::new();
        let mut counted = 0_u64;
        let mut since = 0_usize;

        macro_rules! test {
            ($hash:expr, $name:expr) => {{
                counted += 1;
                let id = $hash & ID_MASK;
                if filter.may_hold(id) && wanted.contains_key(&id) {
                    hits.push((id, $name));
                }
            }};
        }

        for stem in chunk {
            let stem = stem.as_ref();
            let piece = stem.as_bytes();

            if self.bare {
                let plain = feed(self.basis, piece);
                test!(plain, stem.to_string());

                for ending in &self.endings {
                    test!(feed(plain, ending.as_bytes()), format!("{stem}{ending}"));
                }
            }

            for (opening, base) in &self.openings {
                let prefixed = feed(*base, piece);
                test!(prefixed, format!("{opening}{stem}"));

                for ending in &self.endings {
                    test!(
                        feed(prefixed, ending.as_bytes()),
                        format!("{opening}{stem}{ending}")
                    );
                }
            }

            since += 1;
            if since == BATCH {
                done.fetch_add(since, Ordering::Relaxed);
                tried.fetch_add(counted, Ordering::Relaxed);
                since = 0;
                counted = 0;
            }
        }

        done.fetch_add(since, Ordering::Relaxed);
        tried.fetch_add(counted, Ordering::Relaxed);

        hits
    }
}

/// Roughly what one peeled entry costs relative to one forward hash, counting the sort that
/// makes the batch searchable. Sorting dominates a peeled batch, and getting this wrong picks
/// the slower search.
const PEEL_COST: u64 = 80;

/// How many distinct candidate names a search is asking about.
///
/// This is a property of the three lists, not of how the search runs: peeling and hashing
/// forwards ask exactly the same question, so both cover this many candidates and only differ in
/// what they cost. `+ 1` on the endings is the stem wearing no ending at all, and `bare` adds the
/// stem wearing no beginning either.
///
/// It exists because a method that does not record this cannot be compared with one that does.
/// `methods_report.py --efficiency` ranks by candidates per name, which is the figure that
/// predicts what a pass will return; a search that reports only how many names it found is
/// ranked by how long it ran, and that is how a blind sweep of 1.35 billion candidates for 402
/// names came to outrank a derivation that found 1,514 in 596,049.
/// **Zero when there are no beginnings and the bare stem is excluded**, because that is what the
/// search does: `Meet` and `Search` both take their opening count as `openings.len() + bare`, so
/// with neither there is no column to iterate and nothing is tested. This used to floor the width
/// at one, which made a plan with no `begin:` lines and `bare: no` report 31,747,647,770
/// candidates, scan none of them, and exit reporting success. `confirm_plan` refuses such a plan
/// outright now, and this agrees with the engine rather than flattering it.
pub fn candidate_space(openings: usize, endings: usize, stems: usize, bare: bool) -> u64 {
    let width = openings as u64 + u64::from(bare);
    (stems as u64)
        .saturating_mul(width)
        .saturating_mul(endings as u64 + 1)
}

/// Runs a search whichever way round is cheaper, and says which it chose.
///
/// Peeling the endings off the wanted ids turns a product into a sum, but it is not free: each
/// batch has to be sorted before it can be searched, and a batch is `wanted x endings x 2`
/// entries. Where there are few stems and a great many endings, that sort costs more than the
/// multiplication it saves, and hashing forwards is faster.
///
/// The two give identical answers, so this is only ever a question of time.
pub fn run_best<S: AsRef<str> + Sync>(
    openings: &[String],
    endings: &[String],
    stems: &[S],
    wanted: &HashMap<u64, usize>,
    bare: bool,
) -> Vec<(u64, String)> {
    let width = (openings.len() as u64 + u64::from(bare)).max(1);
    let breadth = stems.len() as u64 * width;
    let peeled = wanted.len() as u64 * 2;

    let batches = (endings.len() as u64 * peeled)
        .div_ceil(PEELED_BATCH as u64)
        .max(1);
    let meet = batches * breadth + endings.len() as u64 * peeled * PEEL_COST;
    let plain = candidate_space(openings.len(), endings.len(), stems.len(), bare);

    if meet < plain {
        println!(
            "peeling the endings off the wanted ids: about {:.1}B of work against {:.1}B forwards",
            meet as f64 / 1e9,
            plain as f64 / 1e9
        );
        let search = Meet::new(openings, endings);
        let search = if bare { search } else { search.dressed_only() };
        search.run(stems, wanted)
    } else {
        println!(
            "hashing forwards: about {:.1}B of work against {:.1}B peeling",
            plain as f64 / 1e9,
            meet as f64 / 1e9
        );
        let search = Search::new(openings, endings);
        let search = if bare { search } else { search.dressed_only() };
        search.run(stems, wanted)
    }
}

/// Optional backend routing without changing the historical CPU entry point.
/// Returned keys are lookup IDs; Results applies the game's output-width policy.
pub fn run_best_with_backend<S: AsRef<str> + Sync>(
    openings: &[String],
    endings: &[String],
    stems: &[S],
    wanted: &HashMap<u64, usize>,
    bare: bool,
    fold: bool,
    options: &crate::gpu::BackendOptions,
) -> Result<Vec<(u64, String)>, String> {
    run_best_with_backend_checkpointed(
        openings,
        endings,
        stems,
        wanted,
        bare,
        fold,
        options,
        &mut |_| {},
    )
}

/// Checkpoint only completely validated batches. A failed GPU batch never reaches
/// the callback; Auto recomputes it on CPU, while explicit CUDA returns an error.
pub fn run_best_with_backend_checkpointed<S: AsRef<str> + Sync>(
    openings: &[String],
    endings: &[String],
    stems: &[S],
    wanted: &HashMap<u64, usize>,
    bare: bool,
    fold: bool,
    options: &crate::gpu::BackendOptions,
    checkpoint: &mut dyn FnMut(&[(u64, String)]),
) -> Result<Vec<(u64, String)>, String> {
    let mut driver = crate::gpu::NativeCuda;
    let groups = crate::games::groups(wanted);
    // Explicit CUDA remains an explicit request even for an empty target set.
    if groups.is_empty() && options.backend == crate::gpu::Backend::Cuda {
        crate::gpu::CudaDriver::probe(&mut driver, options.device)?;
    }
    let mut all = Vec::new();
    for (basis, targets) in groups {
        all.extend(run_group_with_backend(
            openings,
            endings,
            stems,
            &targets,
            bare,
            fold,
            basis,
            options,
            &mut driver,
            checkpoint,
        )?);
    }
    Ok(all)
}

fn prefers_meet(openings: usize, endings: usize, stems: usize, targets: usize, bare: bool) -> bool {
    let width = (openings as u128 + u128::from(bare)).max(1);
    let breadth = stems as u128 * width;
    let peeled = targets as u128 * 2;
    let batches = (endings as u128 * peeled)
        .div_ceil(PEELED_BATCH as u128)
        .max(1);
    let meet = batches
        .saturating_mul(breadth)
        .saturating_add(endings as u128 * peeled * PEEL_COST as u128);
    let plain = stems as u128 * (openings as u128 + u128::from(bare)) * (endings as u128 + 1);
    meet < plain
}

const CHECKPOINT_CANDIDATES: u64 = 1_000_000_000;

fn stems_for_budget(openings: usize, endings: usize, bare: bool, budget: u64) -> usize {
    let per_stem = (openings as u128 + u128::from(bare)) * (endings as u128 + 1);
    if per_stem == 0 {
        return usize::MAX;
    }
    ((budget as u128 / per_stem).max(1).min(usize::MAX as u128)) as usize
}

fn cpu_group<S: AsRef<str> + Sync>(
    openings: &[String],
    endings: &[String],
    stems: &[S],
    wanted: &HashMap<u64, usize>,
    bare: bool,
    fold: bool,
    basis: u64,
    meet: bool,
    checkpoint: &mut dyn FnMut(&[(u64, String)]),
) -> Vec<(u64, String)> {
    if stems.is_empty() || wanted.is_empty() || (!bare && openings.is_empty()) {
        return Vec::new();
    }
    if meet || !fold {
        let search = Meet::with_basis(openings, endings, basis, fold);
        let search = if bare { search } else { search.dressed_only() };
        search.run_checkpointed(stems, wanted, checkpoint)
    } else {
        let search = Search::with_basis(openings, endings, basis);
        let search = if bare { search } else { search.dressed_only() };
        // Preserve the caller's historical CPU batching. Every Search::run has
        // a progress reporter; slicing further imposes a fixed startup cost.
        let found = search.run(stems, wanted);
        checkpoint(&found);
        found
    }
}

fn run_group_with_backend<S: AsRef<str> + Sync>(
    openings: &[String],
    endings: &[String],
    stems: &[S],
    wanted: &HashMap<u64, usize>,
    bare: bool,
    fold: bool,
    basis: u64,
    options: &crate::gpu::BackendOptions,
    driver: &mut dyn crate::gpu::CudaDriver,
    checkpoint: &mut dyn FnMut(&[(u64, String)]),
) -> Result<Vec<(u64, String)>, String> {
    use crate::gpu::{Backend, PackedRequest};
    let width = (openings.len() as u64)
        .checked_add(u64::from(bare))
        .ok_or("candidate beginning count overflow")?;
    let height = (endings.len() as u64)
        .checked_add(1)
        .ok_or("candidate ending count overflow")?;
    let total = crate::gpu::checked_space(width, stems.len() as u64, height)?;
    let meet = !fold
        || prefers_meet(
            openings.len(),
            endings.len(),
            stems.len(),
            wanted.len(),
            bare,
        );
    if options.backend == Backend::Cpu
        || (options.backend == Backend::Auto
            && (meet || total < options.min_candidates || total == 0 || wanted.is_empty()))
    {
        return Ok(cpu_group(
            openings, endings, stems, wanted, bare, fold, basis, meet, checkpoint,
        ));
    }
    let prepared = (|| {
        let info = driver.probe(options.device)?;
        let request = PackedRequest::new(
            openings,
            endings,
            stems,
            wanted,
            bare,
            fold,
            basis,
            options.device,
        )?;
        let budget = if options.backend == Backend::Cuda {
            Some(CHECKPOINT_CANDIDATES)
        } else {
            driver.prefer_gpu(&request, &info)?
        };
        Ok::<_, String>(budget)
    })();
    let mut budget = match prepared {
        Ok(Some(budget)) => budget,
        Ok(None) => {
            println!("CPU selected: CUDA did not establish a clear workload-specific advantage");
            return Ok(cpu_group(
                openings, endings, stems, wanted, bare, fold, basis, meet, checkpoint,
            ));
        }
        Err(error) if options.backend == Backend::Auto => {
            eprintln!("CUDA unavailable for this workload; continuing on CPU: {error}");
            return Ok(cpu_group(
                openings, endings, stems, wanted, bare, fold, basis, meet, checkpoint,
            ));
        }
        Err(error) => return Err(error),
    };
    let mut all = Vec::new();
    let mut from = 0;
    while from < stems.len() {
        let count = stems_for_budget(openings.len(), endings.len(), bare, budget);
        let to = from.saturating_add(count).min(stems.len());
        let chunk = &stems[from..to];
        let result = (|| {
            let request = PackedRequest::new(
                openings,
                endings,
                chunk,
                wanted,
                bare,
                fold,
                basis,
                options.device,
            )?;
            let validated = request.validate(driver.execute(&request)?)?;
            if request.total != 0 && !request.targets.is_empty() {
                crate::gpu::record_cuda();
            }
            if let Some(next) = crate::gpu::checkpoint_budget(request.total, &validated) {
                budget = next;
            }
            Ok::<_, String>(request.names(validated))
        })();
        match result {
            Ok(found) => {
                checkpoint(&found);
                all.extend(found);
            }
            Err(error) if options.backend == Backend::Auto => {
                eprintln!("CUDA batch discarded; continuing this group on CPU: {error}");
                all.extend(cpu_group(
                    openings,
                    endings,
                    &stems[from..],
                    wanted,
                    bare,
                    fold,
                    basis,
                    meet,
                    checkpoint,
                ));
                break;
            }
            Err(error) => return Err(error),
        }
        from = to;
    }
    Ok(all)
}

#[cfg(test)]
mod backend_tests {
    use super::*;
    use crate::gpu::{
        fixture_execution, Backend, BackendOptions, CudaDriver, DeviceInfo, Execution,
        PackedRequest,
    };

    #[derive(Default)]
    struct MockCuda {
        probes: usize,
        calibrations: usize,
        calls: usize,
        probe_fails: bool,
        fail_at: Option<usize>,
        corrupt_at: Option<usize>,
        budget: Option<u64>,
    }

    impl CudaDriver for MockCuda {
        fn probe(&mut self, _: usize) -> Result<DeviceInfo, String> {
            self.probes += 1;
            if self.probe_fails {
                return Err("injected unavailable device".into());
            }
            Ok(DeviceInfo {
                ordinal: 0,
                name: "fixture".into(),
                major: 8,
                minor: 0,
                total_memory: 16 << 30,
                free_memory: 16 << 30,
                driver_version: 0,
                runtime_version: 0,
            })
        }
        fn execute(&mut self, request: &PackedRequest) -> Result<Execution, String> {
            self.calls += 1;
            if self.fail_at == Some(self.calls) {
                return Err("injected allocation/kernel error".into());
            }
            let mut result = fixture_execution(request);
            if self.corrupt_at == Some(self.calls) {
                result.candidates = u64::MAX;
            }
            Ok(result)
        }
        fn prefer_gpu(&mut self, _: &PackedRequest, _: &DeviceInfo) -> Result<Option<u64>, String> {
            self.calibrations += 1;
            Ok(self.budget)
        }
    }

    fn fixture_run(
        backend: Backend,
        min_candidates: u64,
        fold: bool,
        basis: u64,
        mock: &mut MockCuda,
        checkpoint: &mut dyn FnMut(&[(u64, String)]),
    ) -> Result<Vec<(u64, String)>, String> {
        let openings = vec!["AMB\\".into()];
        let endings = vec![".WAV".into()];
        let stems = ["one", "two", "three"];
        let wanted = stems
            .iter()
            .map(|stem| {
                let name = format!("AMB\\{stem}.WAV");
                let full = if fold {
                    feed(basis, name.as_bytes())
                } else {
                    feed_raw(basis, name.as_bytes())
                };
                (full & ID_MASK, 0)
            })
            .collect();
        run_group_with_backend(
            &openings,
            &endings,
            &stems,
            &wanted,
            false,
            fold,
            basis,
            &BackendOptions {
                backend,
                device: 0,
                min_candidates,
            },
            mock,
            checkpoint,
        )
    }

    #[test]
    fn cpu_and_ineligible_auto_never_touch_cuda() {
        for (backend, threshold) in [(Backend::Cpu, 1), (Backend::Auto, 100)] {
            let mut mock = MockCuda {
                probe_fails: true,
                ..MockCuda::default()
            };
            let found =
                fixture_run(backend, threshold, true, BASIS, &mut mock, &mut |_| {}).unwrap();
            assert_eq!(found.len(), 3);
            assert_eq!((mock.probes, mock.calibrations, mock.calls), (0, 0, 0));
        }
        let mut mock = MockCuda {
            probe_fails: true,
            ..MockCuda::default()
        };
        let ends: Vec<_> = (0..100).map(|n| format!("_{n}")).collect();
        let stems: Vec<_> = (0..500).map(|n| format!("stem_{n}")).collect();
        let wanted = HashMap::from([(crate::id_of("stem_1_5"), 0)]);
        assert!(prefers_meet(0, ends.len(), stems.len(), wanted.len(), true));
        let found = run_group_with_backend(
            &[],
            &ends,
            &stems,
            &wanted,
            true,
            true,
            BASIS,
            &BackendOptions {
                backend: Backend::Auto,
                min_candidates: 1,
                ..BackendOptions::default()
            },
            &mut mock,
            &mut |_| {},
        )
        .unwrap();
        assert_eq!(found.len(), 1);
        assert_eq!(mock.probes, 0);
    }

    #[test]
    fn explicit_cuda_forces_small_and_unfolded_products_without_calibration() {
        for basis in [BASIS, crate::games::IW_BASIS] {
            for fold in [false, true] {
                let mut mock = MockCuda::default();
                let mut actual = fixture_run(
                    Backend::Cuda,
                    100_000_000,
                    fold,
                    basis,
                    &mut mock,
                    &mut |_| {},
                )
                .unwrap();
                let mut expected = fixture_run(
                    Backend::Cpu,
                    1,
                    fold,
                    basis,
                    &mut MockCuda::default(),
                    &mut |_| {},
                )
                .unwrap();
                actual.sort();
                expected.sort();
                assert_eq!(actual, expected);
                assert_eq!(actual.len(), 3);
                assert!(actual.iter().all(|(_, name)| name.contains('\\')));
                assert_eq!((mock.probes, mock.calibrations, mock.calls), (1, 0, 1));
            }
        }
    }

    #[test]
    fn auto_calibrates_once_and_checkpoints_each_validated_batch() {
        let mut mock = MockCuda {
            budget: Some(2),
            ..MockCuda::default()
        };
        let mut saved = Vec::new();
        let mut callbacks = 0;
        let actual = fixture_run(Backend::Auto, 1, true, BASIS, &mut mock, &mut |batch| {
            callbacks += 1;
            saved.extend_from_slice(batch);
        })
        .unwrap();
        assert_eq!(actual, saved);
        assert_eq!(actual.len(), 3);
        assert_eq!(callbacks, 3);
        assert_eq!((mock.probes, mock.calibrations, mock.calls), (1, 1, 3));
    }

    #[test]
    fn auto_discards_failed_gpu_batches_and_cpu_completes_remaining_work() {
        for corrupt in [false, true] {
            let mut mock = MockCuda {
                budget: Some(2),
                fail_at: (!corrupt).then_some(2),
                corrupt_at: corrupt.then_some(2),
                ..MockCuda::default()
            };
            let mut saved = Vec::new();
            let mut actual = fixture_run(Backend::Auto, 1, true, BASIS, &mut mock, &mut |batch| {
                saved.extend_from_slice(batch)
            })
            .unwrap();
            let mut expected = fixture_run(
                Backend::Cpu,
                1,
                true,
                BASIS,
                &mut MockCuda::default(),
                &mut |_| {},
            )
            .unwrap();
            actual.sort();
            expected.sort();
            saved.sort();
            assert_eq!(actual, expected);
            assert_eq!(actual, saved);
            assert_eq!(
                mock.calls, 2,
                "a failed backend must not be retried within the group"
            );
            assert_eq!(mock.calibrations, 1);
        }
        for probe_fails in [false, true] {
            let mut mock = MockCuda {
                probe_fails,
                ..MockCuda::default()
            };
            assert_eq!(
                fixture_run(Backend::Auto, 1, true, BASIS, &mut mock, &mut |_| {})
                    .unwrap()
                    .len(),
                3
            );
            assert_eq!(mock.calls, 0);
        }
    }

    #[test]
    fn explicit_cuda_errors_without_checkpoints_for_unverified_results() {
        for (probe_fails, fail_at, corrupt_at) in [
            (true, None, None),
            (false, Some(1), None),
            (false, None, Some(1)),
        ] {
            let mut mock = MockCuda {
                probe_fails,
                fail_at,
                corrupt_at,
                ..MockCuda::default()
            };
            let mut callbacks = 0;
            assert!(
                fixture_run(Backend::Cuda, 1, true, BASIS, &mut mock, &mut |_| {
                    callbacks += 1
                })
                .is_err()
            );
            assert_eq!(callbacks, 0);
        }
    }

    #[test]
    fn unfolded_auto_retains_cpu_meet_and_literal_backslashes() {
        let mut mock = MockCuda {
            probe_fails: true,
            ..MockCuda::default()
        };
        let found = fixture_run(Backend::Auto, 1, false, BASIS, &mut mock, &mut |_| {}).unwrap();
        assert_eq!(found.len(), 3);
        assert_eq!(mock.probes, 0);
        for (id, name) in found {
            assert_eq!(id, feed_raw(BASIS, name.as_bytes()) & ID_MASK);
            assert_ne!(id, feed(BASIS, name.as_bytes()) & ID_MASK);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{hash64, hash64_raw, id_of};

    /// The whole of the fast search rests on the hash running backwards exactly, so this is the
    /// test that matters most: peeling a string off a hash has to give back what was there
    /// before it, byte for byte, including the normalisation.
    #[test]
    fn peeling_undoes_feeding() {
        // The unfolded pair must round-trip too, or a Black Ops 4 SAB search peels with one
        // normalisation and hashes with the other and matches nothing while looking healthy.
        let back = hash64_raw(r"amb\environment\water");
        assert_eq!(peel_raw(feed_raw(back, br"\wave_01"), br"\wave_01"), back);

        // And the two normalisations must genuinely differ on a backslash, or the flag is a lie.
        assert_ne!(hash64(r"a\b"), hash64_raw(r"a\b"));
        assert_eq!(
            hash64("a/b"),
            hash64_raw("a/b"),
            "no backslash, no difference"
        );

        let before = hash64("mc/mtl_wpn_t9_ak47");
        assert_eq!(peel(feed(before, b"_barrel_c"), b"_barrel_c"), before);
        assert_eq!(peel(feed(before, b"_BARREL_C"), b"_barrel_c"), before);
        assert_eq!(peel(BASIS, b""), BASIS);
    }

    /// And that a whole name comes apart into the three pieces it was built from.
    #[test]
    fn a_name_comes_apart_into_beginning_stem_and_ending() {
        let whole = hash64("i_mtl_wpn_t9_ak47_barrel_c");

        assert_eq!(peel(whole, b"_c"), hash64("i_mtl_wpn_t9_ak47_barrel"));
        assert_eq!(peel(whole, b"wpn_t9_ak47_barrel_c"), hash64("i_mtl_"));
    }

    /// The candidate count is a number that goes into a submission and gets ranked against every
    /// other method, so it has to be the count the search actually covers rather than an estimate
    /// near it. Counted here against the shape of the product: every stem, wearing every opening
    /// or none, wearing every ending or none.
    #[test]
    fn the_candidate_space_is_the_whole_product() {
        // Three stems, two openings, four endings. Dressed: 3 x 2 x 5 = 30. The `+ 1` on endings
        // is the stem wearing its opening and no ending at all, which is a candidate the search
        // does ask about.
        assert_eq!(candidate_space(2, 4, 3, false), 30);

        // Bare adds the opening-less column: 3 x 3 x 5.
        assert_eq!(candidate_space(2, 4, 3, true), 45);

        // No openings and not bare is a search that asks nothing, and this has to say so. The
        // engine takes its opening count as `openings.len() + bare`; with neither there is no
        // column and nothing is tested. Reporting a stem count here instead is what let a plan
        // claim 31.7 billion candidates, scan none, and exit successfully.
        assert_eq!(candidate_space(0, 0, 7, false), 0);
        assert_eq!(candidate_space(0, 4, 7, false), 0);
        assert_eq!(candidate_space(0, 0, 0, true), 0);

        // With no openings but the bare column kept, the stem wears each ending and nothing else.
        assert_eq!(candidate_space(0, 4, 7, true), 35);

        // A real pass: 30.6M pieces, 700 beginnings, 4,800 endings. This must not wrap.
        assert_eq!(
            candidate_space(700, 4800, 30_660_024, true),
            103_186_341_432_024
        );
    }

    /// The two searches ask the same question and must give the same answer. The faster one is
    /// only worth having if it finds every name the plain one does and invents none, so it is
    /// checked against the plain one rather than against an expected result.
    #[test]
    fn the_fast_search_finds_exactly_what_the_plain_one_does() {
        let openings: Vec<String> = ["mc/", "i_", "mc/mtl_", ""]
            .iter()
            .map(|text| (*text).to_owned())
            .collect();
        let endings: Vec<String> = (0..40).map(|number| format!("_{number:02}")).collect();
        let stems: Vec<String> = (0..500).map(|number| format!("thing_{number}")).collect();

        // A set of ids that the lists really do reach, plus noise that nothing reaches.
        let mut wanted: HashMap<u64, usize> = HashMap::new();
        for (index, stem) in stems.iter().enumerate() {
            let opening = &openings[index % openings.len()];
            let ending = &endings[index % endings.len()];
            wanted.insert(id_of(&format!("{opening}{stem}{ending}")), 0);
            wanted.insert(id_of(&format!("{opening}{stem}")), 0);
            wanted.insert(id_of(stem), 0);
        }
        for number in 0..2_000 {
            wanted.insert(id_of(&format!("nothing reaches this {number}")), 0);
        }

        // These fixture ids use the legacy basis, independent of this machine's selected game.
        let mut plain = Search::with_basis(&openings, &endings, BASIS).run(&stems, &wanted);
        let mut fast = Meet::with_basis(&openings, &endings, BASIS, true).run(&stems, &wanted);

        plain.sort();
        fast.sort();
        plain.dedup();
        fast.dedup();

        assert!(!plain.is_empty());
        assert_eq!(plain, fast);
    }

    /// The same, for a search whose stems are fragments that always need dressing.
    #[test]
    fn the_two_searches_agree_when_the_bare_stem_is_not_a_candidate() {
        let openings: Vec<String> = ["arena/", "menu/", "weapon/"]
            .iter()
            .map(|text| (*text).to_owned())
            .collect();
        let endings: Vec<String> = (0..70).map(|number| format!("_name_{number}")).collect();
        let stems: Vec<String> = (0..300).map(|number| format!("key_{number}")).collect();

        let mut wanted: HashMap<u64, usize> = HashMap::new();
        for (index, stem) in stems.iter().enumerate() {
            let opening = &openings[index % openings.len()];
            wanted.insert(id_of(&format!("{opening}{stem}")), 29);
            wanted.insert(
                id_of(&format!(
                    "{opening}{stem}{}",
                    endings[index % endings.len()]
                )),
                29,
            );
        }

        let mut plain = Search::with_basis(&openings, &endings, BASIS)
            .dressed_only()
            .run(&stems, &wanted);
        let mut fast = Meet::with_basis(&openings, &endings, BASIS, true)
            .dressed_only()
            .run(&stems, &wanted);

        plain.sort();
        fast.sort();
        plain.dedup();
        fast.dedup();

        assert!(!plain.is_empty());
        assert_eq!(plain, fast);
    }

    /// A batch boundary is where a fast search would lose names if the bare stem, or the last
    /// few endings, were handled only on the first time round.
    #[test]
    fn the_fast_search_agrees_across_many_batches() {
        let openings: Vec<String> = vec!["mc/".to_owned(), "wc/".to_owned()];
        let endings: Vec<String> = (0..500).map(|number| format!("_{number}")).collect();
        let stems: Vec<String> = (0..200).map(|number| format!("piece_{number}")).collect();

        let mut wanted: HashMap<u64, usize> = HashMap::new();
        for (index, stem) in stems.iter().enumerate() {
            // Deliberately spread across the whole ending list, so a batch that was skipped
            // shows up as a missing name.
            let ending = &endings[(index * 7) % endings.len()];
            wanted.insert(id_of(&format!("mc/{stem}{ending}")), 0);
            wanted.insert(id_of(&format!("wc/{stem}")), 0);
            wanted.insert(id_of(stem), 0);
        }

        let mut plain = Search::with_basis(&openings, &endings, BASIS).run(&stems, &wanted);
        let mut fast = Meet::with_basis(&openings, &endings, BASIS, true).run(&stems, &wanted);

        plain.sort();
        fast.sort();
        plain.dedup();
        fast.dedup();

        assert_eq!(plain.len(), 600);
        assert_eq!(plain, fast);
    }

    /// A search with no endings at all still has a question to ask: the beginning and the stem
    /// on their own. Slicing an empty ending list into batches yields no batches, so a search
    /// written around those batches can sweep nothing and report it as a clean run of no
    /// matches.
    #[test]
    fn a_search_with_no_endings_still_sweeps() {
        let openings: Vec<String> = ["arena/", "menu/"]
            .iter()
            .map(|t| (*t).to_owned())
            .collect();
        let stems: Vec<String> = (0..100).map(|number| format!("key_{number}")).collect();

        let mut wanted: HashMap<u64, usize> = HashMap::new();
        for (index, stem) in stems.iter().enumerate() {
            wanted.insert(id_of(&format!("{}{stem}", openings[index % 2])), 29);
        }

        let found = Meet::with_basis(&openings, &[], BASIS, true)
            .dressed_only()
            .run(&stems, &wanted);

        assert_eq!(found.len(), stems.len());
    }
}
